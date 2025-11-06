from enum import Enum
from typing import override, List, Tuple
import font
import graphics
import m6845
import mda
import time


class CGA(mda.MDA):
    class CGAMode(Enum):
        Text40 = 0
        Text80 = 1
        G320 = 2
        G640 = 3

    def __init__(self, palette_per_scanline: bool):
        super().__init__()
        self._ram_offset = 0xb8000
        self._m6845 = m6845.M6845()
        self._m6845_reg = 0
        self._graphics_mode = 255
        self._cursor_location = -1
        self._cga_mode = self.CGAMode.Text80
        self._color_configuration = 0
        self._color_configuration_changed = False
        self._color_update_line_count = 0
        self._render_version = 1
        self._pulse_vsync = False
        self._palette_index: List = [ 0x00 ] * 200
        self._palette_per_scanline = palette_per_scanline

    @override
    def GetName(self) -> str:
        return "CGA"

    @override
    def RegisterDevice(self, mappings: dict):
        mappings[0x3d0] = self
        mappings[0x3d1] = self
        mappings[0x3d2] = self
        mappings[0x3d3] = self
        mappings[0x3d4] = self
        mappings[0x3d5] = self
        mappings[0x3d6] = self
        mappings[0x3d7] = self
        mappings[0x3d8] = self
        mappings[0x3d9] = self
        mappings[0x3da] = self
        mappings[0x3db] = self
        mappings[0x3dc] = self

    def GetCurrentScanLine(self):
        # 304 cpu cycles per scan line
        # 262 scan lines
        return (self._clock // 304) % 262

    def IsInHSync(self):
        pixel = self._clock % 304
        return pixel < 16 or pixel > 280  # TODO

    def IsInVSync(self):
        scan_line = self.GetCurrentScanLine()
        return scan_line < 16 or scan_line >= 216

    @override
    def IO_Read(self, port: int) -> int:
        rc = 0

        if (port == 0x3d5 or port == 0x3d7) and _m6845_reg >= 0x0c:
            rc = self._m6845.Read(_m6845_reg)
        elif port == 0x3da:
            if self.IsInVSync():
                rc = 9  # regen buffer | 8 in vertical retrace
            elif self.IsInHSync():
                rc = 1
            else:
                rc = 0
        elif port == 0x3d8:
            rc = self._graphics_mode

        return rc

    @override
    def IO_Write(self, port: int, value: int) -> bool:
        if port == 0x3d4 or port == 0x3d6 or port == 0x3d0 or port == 0x3d2:
            self._m6845_reg = value
        elif port == 0x3d5 or port == 0x3d7 or port == 0x3d1 or port == 0x3d3:
            self._m6845.Write(self._m6845_reg, value)

            if self._m6845_reg == 12 or self._m6845_reg == 13:
                self._display_address = (self._m6845.Read(12) << 8) | self._m6845.Read(13)

            if self._m6845_reg == 14 or self._m6845_reg == 15:
                self._cursor_location = (self._m6845.Read(14) << 8) | self._m6845.Read(15)
        elif port == 0x3d8:
            if self._graphics_mode != value:
                prev_cga_mode = self._cga_mode

                if (value & 2) == 2:  # graphics 320x200
                    if (value & 16) == 16:  # graphics 640x200
                        self._cga_mode = self.CGAMode.G640
                    else:
                        self._cga_mode = self.CGAMode.G320
                else:
                    if (value & 1) == 1:
                        self._cga_mode = self.CGAMode.Text80
                    else:
                        self._cga_mode = self.CGAMode.Text40
                self._graphics_mode = value

                if self._cga_mode != prev_cga_mode:
                    self._cursor_location = -1
        elif port == 0x3d9:
            self._color_configuration = (value >> 4) & 3
            self._color_configuration_changed = True
            self._color_update_line_count = 0

        self._last_update += 1

        return False

    def GetPixelColor(self, line: int, color_index: int, rgb: List):  # TODO
        if self._palette_index[line] >= 2:
            brightness = 255 if self._palette_index[line] == 3 else 200
            if color_index == 1:
                rgb[1] = rgb[2] = brightness  # cyan
                rgb[0] = 0
            elif color_index == 2:
                rgb[0] = rgb[2] = brightness  # magenta
                rgb[1] = 0
            elif color_index == 3:
                rgb[0] = rgb[1] = rgb[2] = brightness  # white
            else:
                rgb[0] = rgb[1] = rgb[2] = 0  # black
        else:
            brightness = 255 if self._palette_index[line] == 1 else 200
            if color_index == 1:  # green
                rgb[0] = rgb[2] = 0
                rgb[1] = brightness
            elif color_index == 2:  # red
                rgb[0] = brightness
                rgb[1] = rgb[2] = 0
            elif color_index == 3:  # blue
                rgb[0] = rgb[1] = 0
                rgb[2] = brightness
            else:
                rgb[0] = rgb[1] = rgb[2] = 0

    def RenderG320FrameGraphical(self):
        try:
            rgb_pixels = [ 0 ] * 640 * 400 * 4
            rgb = [ 0 ] * 3
            for addr in range(self._display_address, min(self._display_address + 16000, 16384)):
                if addr - self._display_address >= 8192:
                    addr_without_base = addr - 8192 - self._display_address
                    y = addr_without_base // 80 * 2 + 1
                    x = (addr_without_base % 80) * 4
                else:
                    addr_without_base = addr - self._display_address
                    y = addr_without_base // 80 * 2
                    x = (addr_without_base % 80) * 4

                if y >= 200:
                    continue

                b = self._ram[addr]

                y_offset = y * 320 * 3 * 4
                for x_i in range(4):
                    color_index = (b >> (x_i * 2)) & 3
                    x_offset = (x + 3 - x_i) * 3 * 2
                    offset = y_offset + x_offset
                    self.GetPixelColor(y if self._palette_per_scanline else 0, color_index, rgb)
                    rgb_pixels[offset + 0] = rgb_pixels[offset + 4] = rgb[2]
                    rgb_pixels[offset + 1] = rgb_pixels[offset + 5] = rgb[1]
                    rgb_pixels[offset + 2] = rgb_pixels[offset + 6] = rgb[0]
                    rgb_pixels[offset + 3] = rgb_pixels[offset + 7] = rgb[255]
                    offset += 320 * 3 * 2
                    rgb_pixels[offset + 0] = rgb_pixels[offset + 4] = rgb[2]
                    rgb_pixels[offset + 1] = rgb_pixels[offset + 5] = rgb[1]
                    rgb_pixels[offset + 2] = rgb_pixels[offset + 6] = rgb[0]
                    rgb_pixels[offset + 3] = rgb_pixels[offset + 7] = rgb[255]

            return 640, 400, rgb_pixels

        except Exception as e:
            print(f'CGA::RenderG320FrameGraphical exception: {e}, line number: {e.__traceback__.tb_lineno}')

    def RenderG640FrameGraphical(self):
        try:
            rgb_pixels = [ 0 ] * 640 * 400 * 4
            for addr in range(self._display_address, min(self._display_address + 16000, 16384)):
                if addr - self._display_address >= 8192:
                    addr_without_base = addr - 8192 - self._display_address
                    y = addr_without_base // 80 * 2 + 1
                    x = (addr_without_base % 80) * 8
                else:
                    addr_without_base = addr - self._display_address
                    y = addr_without_base // 80 * 2
                    x = (addr_without_base % 80) * 8

                if y >= 200:
                    continue

                b = self._ram[addr]
                for x_i in range(8):
                    value = 255 if b & 1 else 0
                    offset1 = (y * 640 * 2 + x + 7 - x_i) * 4
                    rgb_pixels[offset1 + 0] = rgb_pixels[offset1 + 1] = rgb_pixels[offset1 + 2] = value
                    rgb_pixels[offset1 + 3] =  255
                    offset2 = offset1 + 640 * 4
                    rgb_pixels[offset2 + 0] = rgb_pixels[offset2 + 1] = rgb_pixels[offset2 + 2] = value
                    rgb_pixels[offset2 + 3] =  255
                    b >>= 1

                return 640, 400, rgb_pixels

        except Exception as e:
            print(f'CGA::RenderG640FrameGraphical exception: {e}, line number: {e.__traceback__.tb_lineno}')

    def GetFrame(self):
        try:
            if self._cga_mode == self.CGAMode.Text40 or self._cga_mode == self.CGAMode.Text80:
                return self.RenderTextFrameGraphical()
            if self._cga_mode == self.CGAMode.G320:
                return self.RenderG320FrameGraphical()
            if self._cga_mode == self.CGAMode.G640:
                return self.RenderG640FrameGraphical()

        except Exception as e:
            print(f'CGA::GetFrame exception: {e}, line number: {e.__traceback__.tb_lineno}')

    @override
    def Tick(self, cycles: int, clock: int) -> bool:
        self._clock = clock

        line = self.GetCurrentScanLine()

        if self._color_configuration_changed:
            # 200: there's also a 160x100 mode for which this needs to be adjusted
            if line >= 16 and line < 216:
                self._palette_index[line - 16] = self._color_configuration
                if self._palette_per_scanline == False:
                    self._palette_index[0] = self._color_configuration

                self._color_update_line_count += 1
                if self._color_update_line_count >= 200:
                    self._color_configuration_changed = False

        if line >= 216:  # VSync start
            if self._pulse_vsync == False:
                self._pulse_vsync = True
                self._last_update += 1
                #self.PublishVSync()
        else:
            self._pulse_vsync = False

        return super().Tick(cycles, clock)
