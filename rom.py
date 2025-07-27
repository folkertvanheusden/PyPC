from typing import override, List, Tuple
from device import Device

class Rom(Device):
    def __init__(self, filename: str, offset: int):
        self._contents: List[int] = [ b for b in open(filename, 'rb').read() ]
        self._offset: int = offset

        if self._contents[0] != 0x55 or self._contents[1] != 0xaa:
            # string msg = $"ROM {filename} might not be valid! (0x55aa header missing)";
            # Log.DoLog(msg, LogLevel.INFO);
            # Log.Cnsl(msg);
            pass

    @override
    def ReadByte(self, address: int) -> int:
        return self._contents[address - self._offset]

    @override
    def GetName(self) -> str:
        return "ROM"

    @override
    def WriteByte(self, address: int, v: int):
        pass

    @override
    def GetAddressList(self) -> list[Tuple[int, int]]:
        return ((self._offset, len(self._contents)))

    @override
    def IO_Read(self, port: int) -> int:
        return 0xff

    @override
    def GetIRQNumber(self) -> int:
        return -1

    @override
    def IO_Write(self, port: int, value: int) -> bool:
        return False

    @override
    def RegisterDevice(self, mappings: dict):
        pass

    @override
    def Ticks(self) -> bool:
        return False
