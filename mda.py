from typing import override, List, Tuple
import device
import time


class MDA(device.Device):
    def __init__(self):
        self._ram: bytearray = bytearray(b'\xff' * 16384)
        self._hsync: bool = False
        self._last_update: int = 0

        print('\033[2J', end='')   # clear screen

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

        print(self.UpdateConsole(use_offset), end='', flush=True)

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
        if character < 32 or character > 126:
            character = ord('_')
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
        self._clock = clock
        return super().Tick(cycles, clock)
