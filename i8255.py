from typing import override, List, Tuple
import device
import keyboard

class i8255(device.Device):
    def __init__(self, kb: keyboard.Keyboard):
        self._control = 0
        self._dipswitches_high = False
        self._use_SW1 = False
        self._SW2 = 0
        self._kb = kb

        #if (_system_type == SystemType.XT)
        #    _SW1 = 0b00100000  # 2 floppy-drives, CGA80, 256kB, IPL bit
        #else
        #{
        #    _SW1 = (2 << 4) /*(cga80)*/ | (3 << 2 /* memory banks*/)
        #    _SW2 = 0b01101101
        #}
        # XT
        self._SW1 = 0b00110000  # 2 floppy-drives, MDA, 256kB, IPL bit

#        if (n_floppies > 0)
#            _SW1 |= (byte)(1 | ((n_floppies - 1) << 6))

    @override
    def GetIRQNumber(self) -> int:
        return -1

    @override
    def GetName(self) -> str:
        return 'PPI'

    @override
    def RegisterDevice(self, mappings: dict):
        mappings[0x0060] = self
        mappings[0x0061] = self
        mappings[0x0062] = self
        mappings[0x0063] = self

    @override
    def IO_Read(self, port: int) -> int:
        if self._use_SW1 and port == 0x0060:  # PA0
            return self._SW1

        if port == 0x0062:  # PC0
            #switches = _system_type == SystemType.XT ? _SW1 : _SW2
            switches = self._SW1

            if self._dipswitches_high == True:
                return switches >> 4

            return switches & 0x0f

        if port == 0x0063:  # mode
            return 0x99

        return self._kb.IO_Read(port)

    def IO_Write(self, port: int, value: int) -> bool:
        if port == 0x0061:  # PB0
            ## dipswitches selection
            #self._use_SW1 = (value & 0x80) != 0 and _system_type == SystemType.PC
            self._use_SW1 = False

            #if (_system_type == SystemType.XT)
            #    self._dipswitches_high = (value & 8) != 0
            #else
            #    self._dipswitches_high = (value & 4) != 0
            self._dipswitches_high = (value & 8) != 0

#            if ((_control & 2) == 2)  # speaker
#                # return False

            # fall through for keyboard

        elif port == 0x0063:  # control
            return False

        return self._kb.IO_Write(port, value)

    def GetAddressList(self) -> list[Tuple[int, int]]:
        return []

    def WriteByte(self, offset: int, value: int):
        pass

    def ReadByte(self, offset: int) -> int:
        return 0xee

    def Ticks(self) -> bool:
        return False
