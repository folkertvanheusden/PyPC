# programmable interrupt controller (PIC)
from typing import override, List, Tuple
import device

class i8259(device.Device):
    def __init__(self):
        self._int_offset = 8  # TODO updaten bij ICW (OCW?) en dan XT::Tick() de juiste vector
        self._irr = 0  # which irqs are requested
        self._isr = 0  # ...and which are in service
        self._imr = 255  # all irqs masked (disabled)
        self._auto_eoi = False
        self._irq_request_level = 7  # default value? TODO
        self._read_irr = False
        self._has_slave = False
        self._int_in_service = -1  # used by EOI

        self._icw1 = 0
        self._in_init = False
        self._ii_icw2 = False
        self._icw2 = 0
        self._ii_icw3 = False
        self._icw3 = 0
        self._ii_icw4 = False
        self._icw4 = 0
        self._ii_icw4_req = False
        self._ocw2 = 0
        self._ocw3 = 0

    @override
    def GetIRQNumber(self) -> int:
        return -1

    @override
    def GetName(self) -> str:
        return 'i8259'

    @override
    def GetState(self) -> List[str]:
        out = []
        out.append(f'IRR: {self._irr:X2}, ISR: {self._isr:X2}, IMR: {self._imr:X2}, int in serice: {self._int_in_service}')
        out.append(f'auto eoi: {self._auto_eoi}, request level: {self._irq_request_level}')
        out.append(f'read irr: {self._read_irr}')
        out.append(f'in init: {self._in_init}, icw1: {self._icw1:X2}, icw2: {self._ii_icw2}/{self._icw2:X2}, ic3w: {self._ii_icw3}/{self._icw3:X2}, icw4: {self._ii_icw4}/{self._icw4:X2}, icw4 req: {self._ii_icw4_req}')
        out.append(f'ocw2: {self._ocw2:X2}, ocw3: {self._ocw3:X2}')
        return out

    @override
    def RegisterDevice(self, mappings: dict):
        mappings[0x0020] = self
        mappings[0x0021] = self

    def GetPendingInterrupt(self) -> int:
        if self._irr == 0 or self._int_in_service != -1:
            return 255

        for i in range(8):
            mask = 1 << i
            if (self._irr & mask) == mask and (self._isr & mask) == 0 and (self._imr & mask) == 0:
                return i

    def GetInterruptLevel(self) -> int:
        return self._irq_request_level

    def RequestInterruptPIC(self, interrupt_nr: int):
        mask = 1 << interrupt_nr
        self._irr |= mask

    def SetIRQBeingServiced(self, interrupt_nr: int):
        if self._auto_eoi == False:
            self._int_in_service = interrupt_nr
            mask = 1 << interrupt_nr
            self._isr |= mask
        else:
            mask = ~(1 << interrupt_nr)
            self._irr &= mask
            self._isr &= mask
            self._int_in_service = -1

    @override
    def IO_Read(self, addr: int) -> int:
        rc = 0

        if addr == 0x0020:
            if self._read_irr:
                rc = self._irr
            else:
                rc = self._isr
        elif addr == 0x0021:
            rc = self._imr

        return rc

    @override
    def IO_Write(self, addr: int, value: int) -> bool:
        if addr == 0x0020:
            self._in_init = (value & 16) == 16
            self._has_slave = (value & 2) == 0
            self._icw1 = value

            if self._in_init:  # ICW
                self._ii_icw2 = False
                self._ii_icw3 = False
                self._ii_icw4 = False
                self._ii_icw4_req = (value & 1) == 1

                self._imr = 0  # TODO 255?
                self._isr = 0
                self._irr = 0

                self._int_in_service  = -1

            else:  # OCW 2/3
                if (value & 8) == 8:  # OCW3
                    self._read_irr = (value & 3) == 2
                    self._ocw3 = value
                else:  # OCW2
                    self._irq_request_level = value & 7
                    self._ocw2 = value

                    # EOI
                    if ((value >> 5) & 1) == 1:  # EOI set (in OCW2)?
                        if (value & 0x60) == 0x60:  # ack a certain level
                            i = value & 7

                            mask = ~(1 << i)
                            self._irr &= mask
                            self._isr &= mask
                            if i == self._int_in_service:
                                self._int_in_service = -1

                        else:
                            if self._int_in_service != -1:
                                mask = ~(1 << self._int_in_service)
                                self._irr &= mask
                                self._isr &= mask
                                self._int_in_service = -1

        elif addr == 0x0021:
            if self._in_init:
                if self._ii_icw2 == False:
                    self._icw2 = value
                    self._ii_icw2 = True
                    self._int_offset = value

                elif self._ii_icw3 == False and self._has_slave:
                    self._ii_icw3 = True
                    self._icw3 = value

                    # ignore value: slave-devices are not supported in this emulator

                    if self._ii_icw4_req == False:
                        self._in_init = False

                elif self._ii_icw4 == False:
                    self._ii_icw4 = True
                    self._icw4 = value
                    self._in_init = False
                    new_auto_eoi = (value & 2) == 2
                    if new_auto_eoi != self._auto_eoi:
                        self._auto_eoi = new_auto_eoi
            else:
                self._imr = value

        # when reconfiguring the PIC8259, force an interrupt recheck
        return True

    def GetInterruptOffset(self) -> int:
        return self._int_offset

    def GetInterruptMask(self) -> int:
        return self._imr

    @override
    def GetAddressList(self) -> list[Tuple[int, int]]:
        return []

    @override
    def WriteByte(self, offset: int, value: int):
        pass

    @override
    def ReadByte(self, offset: int) -> int:
        return 0xee

    @override
    def Ticks(self) -> bool:
        return False
