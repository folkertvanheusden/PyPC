from enum import Enum

class State8088:
    class RepMode(Enum):
        NotSet = 0
        REPE_Z = 1
        REPNZ = 2
        REP = 3

    def __init__(self):
        self._ah: int = 0
        self._al: int = 0
        self._bh: int = 0
        self._bl: int = 0
        self._ch: int = 0
        self._cl: int = 0
        self._dh: int = 0
        self._dl: int = 0

        self._si: int = 0
        self._di: int = 0
        self._bp: int = 0
        self._sp: int = 0

        self._ip: int = 0

        self._cs: int = 0
        self._ds: int = 0
        self._es: int = 0
        self._ss: int = 0

        # replace by an Optional-type when available
        self._segment_override: int = 0
        self._segment_override_set: bool = False

        self._flags: int = 0

        self._in_hlt: bool = False
        self._inhibit_interrupts : bool = False  # for 1 instruction after loading segment registers

        self._rep: bool = False
        self._rep_do_nothing: bool = False
        self._rep_mode: State8088.RepMode = State8088.RepMode.NotSet
        self._rep_addr: int = 0
        self._rep_opcode: int = 0

        self._clock: int = 0

        self._crash_counter: int = 0

    def GetInHlt(self) -> bool:
        return self._in_hlt

    def GetClock(self) -> int:
        return self._clock

    def GetFlagsAsString(self) -> str:
        out = ''

        out += 'o' if self.GetFlagO() else '-'
        out += 'I' if self.GetFlagI() else '-'
        out += 'T' if self.GetFlagT() else '-'
        out += 's' if self.GetFlagS() else '-'
        out += 'z' if self.GetFlagZ() else '-'
        out += 'a' if self.GetFlagA() else '-'
        out += 'p' if self.GetFlagP() else '-'
        out += 'c' if self.GetFlagC() else '-'

        return out

    def DumpState(self):
        print(f"State for clock {self.GetClock()}:")
        print(f"{self.GetFlagsAsString()} AX:{self.GetAX():4x} BX:{self.GetBX():4x} CX:{self.GetCX():4x} DX:{self.GetDX():4x} SP:{self.GetSP():4x} BP:{self.GetBP():4x} SI:{self.GetSI():4x} DI:{self.GetDI():4x} flags:{self.GetFlags():4x} ES:{self.GetES():4x} CS:{self._cs:4x} SS:{self.GetSS():4x} DS:{self.GetDS():4x} IP:{self._ip:4x}")
        print(f"REP: {self._rep}, do-nothing: {self._rep_do_nothing}, mode: {self._rep_mode}, addr {self._rep_addr}, opcode {self._rep_opcode}")
        print(f"In HLT: {self._in_hlt}, inhibit interrupts: {self._inhibit_interrupts}")
        print(f"Segment override: {self._segment_override_set}, value: {self._segment_override}")
        print(f"Crash counter: {self._crash_counter}")

    def SetIP(self, cs_in: int, ip_in: int):
        assert cs_in >= 0 and cs_in <= 65535
        assert ip_in >= 0 and ip_in <= 65535
        self._cs = cs_in
        self._ip = ip_in

    def FixFlags(self):
        self._flags &= 0b1111111111010101
        self._flags |= 2  # bit 1 is always set
        self._flags |= 0xf000  # upper 4 bits are always 1

    def GetAL(self) -> int:
        return self._al

    def SetAL(self, v: int):
        assert v >= 0 and v <= 255
        self._al = v

    def GetAH(self) -> int:
        return self._ah

    def SetAH(self, v: int):
        assert v >= 0 and v <= 255
        self._ah = v

    def GetAX(self) -> int:
        return (self._ah << 8) | self._al

    def SetAX(self, v: int):
        assert v >= 0 and v <= 65535
        self._ah = v >> 8
        self._al = v & 255

    def GetBX(self) -> int:
        return (self._bh << 8) | self._bl

    def SetBX(self, v: int):
        assert v >= 0 and v <= 65535
        self._bh = v >> 8
        self._bl = v & 255

    def GetCX(self) -> int:
        return (self._ch << 8) | self._cl

    def SetCX(self, v: int):
        assert v >= 0 and v <= 65535
        self._ch = v >> 8
        self._cl = v & 255

    def GetDX(self) -> int:
        return (self._dh << 8) | self._dl

    def SetDX(self, v: int):
        assert v >= 0 and v <= 65535
        self._dh = v >> 8
        self._dl = v & 255

    def SetSS(self, v: int):
        assert v >= 0 and v <= 65535
        self._ss = v

    def SetCS(self, v: int):
        assert v >= 0 and v <= 65535
        self._cs = v

    def SetDS(self, v: int):
        assert v >= 0 and v <= 65535
        self._ds = v

    def SetES(self, v: int):
        assert v >= 0 and v <= 65535
        self._es = v

    def SetSP(self, v: int):
        assert v >= 0 and v <= 65535
        self._sp = v

    def SetBP(self, v: int):
        assert v >= 0 and v <= 65535
        self._bp = v

    def SetSI(self, v: int):
        assert v >= 0 and v <= 65535
        self._si = v

    def SetDI(self, v: int):
        assert v >= 0 and v <= 65535
        self._di = v

    def SetIP(self, v: int):
        assert v >= 0 and v <= 65535
        self._ip = v

    def SetFlags(self, v: int):
        assert v >= 0 and v <= 65535
        self._flags = v

    def GetSS(self) -> int:
        return self._ss

    def GetCS(self) -> int:
        return self._cs

    def GetDS(self) -> int:
        return self._ds

    def GetES(self) -> int:
        return self._es

    def GetSP(self) -> int:
        return self._sp

    def GetBP(self) -> int:
        return self._bp

    def GetSI(self) -> int:
        return self._si

    def GetDI(self) -> int:
        return self._di

    def GetIP(self) -> int:
        return self._ip

    def GetFlags(self) -> int:
        return self._flags

    def SetZSPFlags(self, v: int):
        assert v >= 0 and v <= 65535
        self.SetFlagZ(v == 0)
        self.SetFlagS((v & 0x80) == 0x80)
        self.SetFlagP(v)

    def ClearFlagBit(self, bit: int):
        self._flags &= ~(1 << bit)

    def SetFlagBit(self, bit: int):
        self._flags |= 1 << bit

    def SetFlag(self, bit: int, state: bool):
        self._flags &= ~(1 << bit)
        self._flags |= state << bit

    def GetFlag(self, bit: int) -> bool:
        return (self._flags & (1 << bit)) != 0

    def SetFlagC(self, state: bool):
        self.SetFlag(0, state)

    def GetFlagC(self) -> bool:
        return self.GetFlag(0)

    def SetFlagP(self, v: int):
        count = 0

        v &= 0xff

        while v != 0:
            count += 1
            v &= v - 1

        self.SetFlag(2, (count & 1) == 0)

    def GetFlagP(self) -> bool:
        return self.GetFlag(2)

    def SetFlagA(self, state: bool):
        self.SetFlag(4, state)

    def GetFlagA(self) -> bool:
        return self.GetFlag(4)

    def SetFlagZ(self, state: bool):
        self.SetFlag(6, state)

    def GetFlagZ(self) -> bool:
        return self.GetFlag(6)

    def SetFlagS(self, state: bool):
        self.SetFlag(7, state)

    def GetFlagS(self) -> bool:
        return self.GetFlag(7)

    def SetFlagT(self, state: bool):
        self.SetFlag(8, state)

    def GetFlagT(self) -> bool:
        return self.GetFlag(8)

    def SetFlagI(self, state: bool):
        self.SetFlag(9, state)

    def GetFlagI(self) -> bool:
        return self.GetFlag(9)

    def SetFlagD(self, state: bool):
        self.SetFlag(10, state)

    def GetFlagD(self) -> bool:
        return self.GetFlag(10)

    def SetFlagO(self, state: bool):
        self.SetFlag(11, state)

    def GetFlagO(self) -> bool:
        return self.GetFlag(11)
