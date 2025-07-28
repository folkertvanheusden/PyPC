from typing import override, List, Tuple
import device

class MDA(device.Device):
    def __init__(self):
        self._ram: bytearray = bytearray(b'\xff' * 16384)
        self._hsync: bool = False

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

        self.UpdateConsole(use_offset)

    def UpdateConsole(self, offset: int):
        if offset >= 80 * 25 * 2:
            return

        y = offset / (80 * 2)
        x = (offset % (80 * 2)) / 2

        char_base_offset = offset

        character = self._ram[char_base_offset + 0]
        attributes = self._ram[char_base_offset + 1]

        #EmulateTextDisplay(x, y, character, attributes)
        print(f'{character:c}', end='', flush=True)

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
