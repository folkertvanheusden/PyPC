from typing import override, List, Tuple
from device import Device

class Memory(Device):
    def __init__(self, size: int):
        self._m: List[int] = [ 255 ] * size

    @override
    def ReadByte(self, address: int) -> int:
        return self._m[address]

    @override
    def WriteByte(self, address: int, v: int):
        self._m[address] = v

    @override
    def GetName(self) -> str:
        return "RAM"

    @override
    def IO_Read(self, port: int) -> int:
        return 0xff

    @override
    def GetIRQNumber(self) -> int:
        return -1

    @override
    def GetAddressList(self) -> list[Tuple[int, int]]:
        return [(0, len(self._m))]

    @override
    def IO_Write(self, port: int, value: int) -> bool:
        return false

    @override
    def RegisterDevice(self, mappings: dict):
        pass

    @override
    def Ticks(self) -> bool:
        return False
