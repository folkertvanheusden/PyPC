from typing import override, List, Tuple
import font
import graphics
import time


class MDA(graphics.Graphics):
    def __init__(self):
        self._ram: bytearray = bytearray(b'\xff' * 16384)
        self._hsync: bool = False
        self._last_update: int = 0
        self._font = font.Font().get_font()

        self._palette = [
                (   0,   0,   0, 255 ),
                (   0,   0, 127, 255 ),
                (   0, 127,   0, 255 ),
                (   0, 127, 127, 255 ),
                ( 127,   0,   0, 255 ),
                ( 127,   0, 127, 255 ),
                ( 127, 127,   0, 255 ),
                ( 127, 127, 127, 255 ),
                ( 127, 127, 127, 255 ),
                (   0,   0, 255, 255 ),
                (   0, 255,   0, 255 ),
                (   0, 255, 255, 255 ),
                ( 255,   0,   0, 255 ),
                ( 255,   0, 255, 255 ),
                ( 255, 255,   0, 255 ),
                ( 255, 255, 255, 255 )
                ]

    @override
    def GetName(self) -> str:
        return "MDA"

    @override
    def GetIRQNumber(self) -> int:
        return -1

    @override
    def RegisterDevice(self, mappings: dict):
        for port in range(0x3b0, 0x3c0):
            mappings[port] = self

    def GetClock(self):
        return self._last_update

    @override
    def GetAddressList(self) -> list[Tuple[int, int]]:
        return [(0xb0000, 0x8000)]

    @override
    def IO_Write(self, port: int, value:  int) -> bool:
        return False

    @override
    def IO_Read(self, port: int) -> int:
        rc = 0

        if port == 0x03ba:
            rc = 9 if self._hsync else 0
            self._hsync = not self._hsync

        return rc

    @override
    def WriteByte(self, offset: int, value: int):
        use_offset = (offset - 0xb0000) & 0x3fff
        self._ram[use_offset] = value
        self._last_update += 1

        #print(self.UpdateConsole(use_offset), end='', flush=True)

    def GetFrame(self):
        try:
            width = 80
            gf_width = 640
            gf_height = 401
            pixels = [ 0 ] * (gf_width * gf_height * 4)
            mem_pointer = 0
            for y in range(25):
                for x in range(80):
                    mem_pointer = y * 80 * 2 + x * 2
                    char_base_offset = mem_pointer & 16382
                    character = self._ram[char_base_offset + 0]
                    attributes = self._ram[char_base_offset + 1]

                    char_offset = character * self._font[1]
                    fg = attributes & 15
                    bg = (attributes >> 4) & 7

                    for py in range(8):
                        bit_mask = 128
                        line = self._font[2][char_offset + py]
                        y_pixel_offset = (y * 8 + py) * 640 * 4 * 2
                        for px in range(8):
                            is_fg = bool(line & bit_mask)
                            pixel_offset = y_pixel_offset + (x * 8 + px) * 4
                            if is_fg:
                                pixels[pixel_offset:pixel_offset + 4] = self._palette[fg][0:4]
                                pixel_offset += 640 * 4
                                pixels[pixel_offset:pixel_offset + 4] = self._palette[fg][0:4]
                            else:
                                pixels[pixel_offset:pixel_offset + 4] = self._palette[bg][0:4]
                                pixel_offset += 640 * 4
                                pixels[pixel_offset:pixel_offset + 4] = self._palette[bg][0:4]

                            bit_mask >>= 1

            return gf_width, gf_height, pixels

        except Exception as e:
            print(f'MDA::GetFrame exception: {e}, line number: {e.__traceback__.tb_lineno}')


    def EmulateTextDisplay(self, x: int, y: int, character: int, attributes: int):
        out = f'\033[{y + 1};{x + 1}H'   # position cursor

        colormap = ( 0, 4, 2, 6, 1, 5, 3, 7 )
        fg = colormap[(attributes >> 4) & 7]
        bg = colormap[attributes & 7]

        out += f'\033[0;{40 + fg};{30 + bg}m'   # set attributes (colors)
        if (attributes & 8) == 8:
            out += f'\033[1m'   # bright

        if character == 0:
            character = 32
        out += f'{character:c}'

        return out

    def UpdateConsole(self, offset: int):
        if offset >= 80 * 25 * 2:
            return ''

        y = offset // (80 * 2)
        x = (offset % (80 * 2)) // 2

        char_base_offset = offset

        character = self._ram[char_base_offset + 0]
        attributes = self._ram[char_base_offset + 1]

        return self.EmulateTextDisplay(x, y, character, attributes)

    @override
    def ReadByte(self, offset: int) -> int:
        return self._ram[(offset - 0xb0000) & 0x3fff]

    @override
    def Ticks(self) -> bool:
        return True

    @override
    def Tick(self, cycles: int, clock: int) -> bool:
        return super().Tick(cycles, clock)
