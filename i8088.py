from typing import List, Tuple
import bus
import device
import pc_io
import state8088


class i8088:
    def __init__(self, b: bus.Bus, devices: List[device.Device], run_IO: bool):
        self._terminate_on_off_the_rails: bool = False
        self._MemMask: int = 0x000fffff

        self._breakpoints = set()
        self._ignore_breakpoints: bool = False
        self._stop_reason: str = ''

        self._state: state8088.State8088 = state8088.State8088()

        self._b = b
        self._devices = devices
        self._io = pc_io.IO(b, devices, not run_IO)
        self._terminate_on_off_the_rails = run_IO

        self._ops = dict()
        self._ops[0x00] = self.Op_ADD_SUB_ADC_SBC
        self._ops[0x01] = self.Op_ADD_SUB_ADC_SBC
        self._ops[0x02] = self.Op_ADD_SUB_ADC_SBC
        self._ops[0x03] = self.Op_ADD_SUB_ADC_SBC
        self._ops[0x04] = self.Op_ADD_AL_xx
        self._ops[0x05] = self.Op_ADD_AX_xxxx
        self._ops[0x06] = self.Op_PUSH_ES
        self._ops[0x07] = self.Op_POP_ES
        self._ops[0x08] = self.Op_logic_functions
        self._ops[0x09] = self.Op_logic_functions
        self._ops[0x0a] = self.Op_logic_functions
        self._ops[0x0b] = self.Op_logic_functions
        self._ops[0x0c] = self.Op_OR_AND_XOR
        self._ops[0x0e] = self.Op_PUSH_CS
        self._ops[0x0f] = self.Op_POP_CS
        self._ops[0x0d] = self.Op_OR_AND_XOR
        self._ops[0x10] = self.Op_ADD_SUB_ADC_SBC
        self._ops[0x11] = self.Op_ADD_SUB_ADC_SBC
        self._ops[0x12] = self.Op_ADD_SUB_ADC_SBC
        self._ops[0x13] = self.Op_ADD_SUB_ADC_SBC
        self._ops[0x14] = self.Op_ADD_AL_xx
        self._ops[0x15] = self.Op_ADD_AX_xxxx
        self._ops[0x16] = self.Op_PUSH_SS
        self._ops[0x17] = self.Op_POP_SS
        self._ops[0x18] = self.Op_ADD_SUB_ADC_SBC
        self._ops[0x19] = self.Op_ADD_SUB_ADC_SBC
        self._ops[0x1a] = self.Op_ADD_SUB_ADC_SBC
        self._ops[0x1b] = self.Op_ADD_SUB_ADC_SBC
        self._ops[0x1c] = self.Op_SBB_AL_ib
        self._ops[0x1d] = self.Op_SBB_AX_iw
        self._ops[0x1e] = self.Op_PUSH_DS
        self._ops[0x1f] = self.Op_POP_DS
        self._ops[0x20] = self.Op_logic_functions
        self._ops[0x21] = self.Op_logic_functions
        self._ops[0x22] = self.Op_logic_functions
        self._ops[0x23] = self.Op_logic_functions
        self._ops[0x24] = self.Op_OR_AND_XOR
        self._ops[0x25] = self.Op_OR_AND_XOR
        self._ops[0x27] = self.Op_DAA
        self._ops[0x28] = self.Op_ADD_SUB_ADC_SBC
        self._ops[0x29] = self.Op_ADD_SUB_ADC_SBC
        self._ops[0x2a] = self.Op_ADD_SUB_ADC_SBC
        self._ops[0x2b] = self.Op_ADD_SUB_ADC_SBC
        self._ops[0x2c] = self.Op_SUB_AL_ib
        self._ops[0x2d] = self.Op_SUB_AX_iw
        self._ops[0x2f] = self.Op_DAS
        self._ops[0x30] = self.Op_logic_functions
        self._ops[0x31] = self.Op_logic_functions
        self._ops[0x32] = self.Op_logic_functions
        self._ops[0x33] = self.Op_logic_functions
        self._ops[0x34] = self.Op_OR_AND_XOR
        self._ops[0x35] = self.Op_OR_AND_XOR
        self._ops[0x37] = self.Op_AAA
        self._ops[0x38] = self.Op_ADD_SUB_ADC_SBC
        self._ops[0x39] = self.Op_ADD_SUB_ADC_SBC
        self._ops[0x3a] = self.Op_ADD_SUB_ADC_SBC
        self._ops[0x3b] = self.Op_ADD_SUB_ADC_SBC
        self._ops[0x3c] = self.Op_CMP
        self._ops[0x3d] = self.Op_CMP
        self._ops[0x3f] = self.Op_AAS
        for i in range(0x40, 0x50):
            self._ops[i] = self.Op_INC_DEC
        self._ops[0x50] = self.Op_PUSH_AX
        self._ops[0x51] = self.Op_PUSH_CX
        self._ops[0x52] = self.Op_PUSH_DX
        self._ops[0x53] = self.Op_PUSH_BX
        self._ops[0x54] = self.Op_PUSH_SP
        self._ops[0x55] = self.Op_PUSH_BP
        self._ops[0x56] = self.Op_PUSH_SI
        self._ops[0x57] = self.Op_PUSH_DI
        self._ops[0x58] = self.Op_POP_AX
        self._ops[0x59] = self.Op_POP_CX
        self._ops[0x5a] = self.Op_POP_DX
        self._ops[0x5b] = self.Op_POP_BX
        self._ops[0x5c] = self.Op_POP_SP
        self._ops[0x5d] = self.Op_POP_BP
        self._ops[0x5e] = self.Op_POP_SI
        self._ops[0x5f] = self.Op_POP_DI
        for i in range(0x60, 0x80):
            self._ops[i] = self.Op_Jxx
        self._ops[0x80] = self.Op_CMP_OR_XOR_etc
        self._ops[0x81] = self.Op_CMP_OR_XOR_etc
        self._ops[0x82] = self.Op_CMP_OR_XOR_etc
        self._ops[0x83] = self.Op_CMP_OR_XOR_etc
        self._ops[0x84] = self.Op_TEST
        self._ops[0x85] = self.Op_TEST
        self._ops[0x86] = self.Op_XCHG
        self._ops[0x87] = self.Op_XCHG
        self._ops[0x88] = self.Op_MOV2
        self._ops[0x89] = self.Op_MOV2
        self._ops[0x8a] = self.Op_MOV2
        self._ops[0x8b] = self.Op_MOV2
        self._ops[0x8c] = self.Op_MOV2
        self._ops[0x8d] = self.Op_LEA
        self._ops[0x8e] = self.Op_MOV2
        self._ops[0x8f] = self.Op_POP_rmw
        self._ops[0x90] = self.Op_NOP
        for i in range(0x91, 0x98):
            self._ops[i] = self.Op_XCHG_AX
        self._ops[0x98] = self.Op_CBW
        self._ops[0x99] = self.Op_CWD
        self._ops[0x9a] = self.Op_CALL_far
        self._ops[0x9b] = self.Op_FWAIT
        self._ops[0x9c] = self.Op_PUSHF
        # self._ops[0x9d] = self.Op_POPF  special case
        self._ops[0x9e] = self.Op_SAHF
        self._ops[0x9f] = self.Op_LAHF
        self._ops[0xa0] = self.Op_MOV_AL_mem
        self._ops[0xa1] = self.Op_MOV_AX_mem
        self._ops[0xa2] = self.Op_MOV_mem_AL
        self._ops[0xa3] = self.Op_MOV_mem_AX
        self._ops[0xa4] = self.Op_MOVSB
        self._ops[0xa5] = self.Op_MOVSW
        self._ops[0xa6] = self.Op_CMPSB
        self._ops[0xa7] = self.Op_CMPSW
        self._ops[0xa8] = self.Op_TEST_AL
        self._ops[0xa9] = self.Op_TEST_AX
        self._ops[0xaa] = self.Op_STOSB
        self._ops[0xab] = self.Op_STOSW
        self._ops[0xac] = self.Op_LODSB
        self._ops[0xad] = self.Op_LODSW
        self._ops[0xae] = self.Op_SCASB
        self._ops[0xaf] = self.Op_SCASW
        for i in range(0xb0, 0xc0):
            self._ops[i] = self.Op_MOV_reg_ib
        self._ops[0xc0] = self.Op_RET2
        self._ops[0xc1] = self.Op_RET3
        self._ops[0xc2] = self.Op_RET2
        self._ops[0xc3] = self.Op_RET3
        self._ops[0xc4] = self.Op_LES_LDS
        self._ops[0xc5] = self.Op_LES_LDS
        self._ops[0xc6] = self.Op_MOV
        self._ops[0xc7] = self.Op_MOV
        self._ops[0xc8] = self.Op_REFT
        self._ops[0xc9] = self.Op_REFT
        self._ops[0xca] = self.Op_REFT
        self._ops[0xcb] = self.Op_REFT
        self._ops[0xcc] = self.Op_INT
        self._ops[0xcd] = self.Op_INT
        self._ops[0xce] = self.Op_INT
#        self._ops[0xcf] = self.Op_IRET special case
        self._ops[0xd0] = self.Op_shift
        self._ops[0xd1] = self.Op_shift
        self._ops[0xd2] = self.Op_shift
        self._ops[0xd3] = self.Op_shift
        self._ops[0xd4] = self.Op_AAM
        self._ops[0xd5] = self.Op_AAD
        self._ops[0xd6] = self.Op_SALC
        self._ops[0xd7] = self.Op_XLATB
        for i in range(0xd8, 0xe0):
            self._ops[i] = self.Op_FPU
        self._ops[0xe0] = self.Op_LOOP
        self._ops[0xe1] = self.Op_LOOP
        self._ops[0xe2] = self.Op_LOOP
        self._ops[0xe3] = self.Op_JCXZ
        self._ops[0xe4] = self.Op_IN_AL_ib
        self._ops[0xe5] = self.Op_IN_AX_ib
        self._ops[0xe6] = self.Op_OUT_AL
        self._ops[0xe7] = self.Op_OUT_AX
        self._ops[0xe8] = self.Op_CALL
        self._ops[0xe9] = self.Op_JMP_np
        self._ops[0xea] = self.Op_JMP_far
        self._ops[0xeb] = self.Op_JMP
        self._ops[0xec] = self.Op_IN_AL_DX
        self._ops[0xed] = self.Op_IN_AX_DX
        self._ops[0xee] = self.Op_OUT_DX_AL
        self._ops[0xef] = self.Op_OUT_DX_AX
        self._ops[0xf4] = self.Op_HLT
        self._ops[0xf5] = self.Op_CMC
        self._ops[0xf6] = self.Op_TEST_others
        self._ops[0xf7] = self.Op_TEST_others
        self._ops[0xf8] = self.Op_CLC
        self._ops[0xf9] = self.Op_STC
        self._ops[0xfa] = self.Op_CLI
        self._ops[0xfb] = self.Op_STI
        self._ops[0xfc] = self.Op_CLD
        self._ops[0xfd] = self.Op_STD
        self._ops[0xfe] = self.Op_fe_ff
        self._ops[0xff] = self.Op_fe_ff

        # bit 1 of the flags register is always 1
        # https://www.righto.com/2023/02/silicon-reverse-engineering-intel-8086.html
        self._state.SetFlagBit(1)

    def ToSigned8(self, n):
        n &= 0xff
        return (n ^ 0x80) - 0x80

    def ToSigned16(self, n):
        n &= 0xffff
        return (n ^ 0x8000) - 0x8000

    def GetState(self) -> state8088.State8088:
        return self._state

    def ReadMemByte(self, segment: int, offset: int) -> int:
        a = ((segment << 4) + offset) & self._MemMask
        rc = self._b.ReadByte(a)
        self._state._clock += rc[1]
        return rc[0]

    def ReadMemWord(self, segment: int, offset: int) -> int:
        return self.ReadMemByte(segment, offset) + (self.ReadMemByte(segment, (offset + 1) & 0xffff) << 8)

    def WriteMemByte(self, segment: int, offset: int, v: int):
        a = ((segment << 4) + offset) & self._MemMask
        self._state._clock += self._b.WriteByte(a, v)

    def WriteMemWord(self, segment: int, offset: int, v: int):
        self.WriteMemByte(segment, offset, v & 0xff);
        self.WriteMemByte(segment, (offset + 1) & 0xffff, v >> 8)

    def GetPcByte(self) -> int:
        ip = self._state._ip
        self._state._ip += 1
        self._state._ip &= 0xffff
        return self.ReadMemByte(self._state._cs, ip)

    def GetPcWord(self) -> int:
        v = self.GetPcByte()
        v |= self.GetPcByte() << 8
        return v

    def SetAddSubFlags(self, word: bool, r1: int, r2: int, result: int, issub: bool, flag_c: bool):
        assert r1 >= 0 and r1 <= (65535 if word else 255)
        assert r2 >= 0 and r2 <= (65535 if word else 255)

        in_reg_result = (result & 0xffff) if word else (result & 0xff)
        u_result = result & 0xffffffff

        mask = 0x8000 if word else 0x80

        temp_r2 = ((r2 - flag_c) if issub else (r2 + flag_c)) & 0xffff

        before_sign = (r1 & mask) == mask
        value_sign = (r2 & mask) == mask
        after_sign = (u_result & mask) == mask

        self._state.SetFlagO(after_sign != before_sign and ((before_sign != value_sign and issub == True) or (before_sign == value_sign and issub == False)))
        self._state.SetFlagC(u_result >= 0x10000 if word else u_result >= 0x100)
        self._state.SetFlagS((in_reg_result & mask) != 0)
        self._state.SetFlagZ(in_reg_result == 0)

        if issub:
            self._state.SetFlagA((((r1 & 0x0f) - (r2 & 0x0f) - flag_c) & 0x10) > 0)
        else:
            self._state.SetFlagA((((r1 & 0x0f) + (r2 & 0x0f) + flag_c) & 0x10) > 0)

        self._state.SetFlagP(result & 0xff)

    def GetRegister(self, reg: int, w: bool) -> int:
        if w:
            if reg == 0:
                return self._state.GetAX()
            if reg == 1:
                return self._state.GetCX()
            if reg == 2:
                return self._state.GetDX()
            if reg == 3:
                return self._state.GetBX()
            if reg == 4:
                return self._state._sp
            if reg == 5:
                return self._state._bp
            if reg == 6:
                return self._state._si
            if reg == 7:
                return self._state._di
        else:
            if reg == 0:
                return self._state.GetAL()
            if reg == 1:
                return self._state._cl
            if reg == 2:
                return self._state._dl
            if reg == 3:
                return self._state._bl
            if reg == 4:
                return self._state.GetAH()
            if reg == 5:
                return self._state._ch
            if reg == 6:
                return self._state._dh
            if reg == 7:
                return self._state._bh

    def GetSRegister(self, reg: int) -> int:
        reg &= 0b00000011

        if reg == 0b000:
            return self._state._es
        if reg == 0b001:
            return self._state._cs
        if reg == 0b010:
            return self._state._ss
        if reg == 0b011:
            return self._state._ds

    # value, cycles
    def GetDoubleRegisterMod01_02(self, reg: int, word: bool) -> Tuple[int, int, bool, int]:
        a = 0
        cycles = 0
        override_segment = False
        new_segment = 0

        if reg == 6:
            a = self._state._bp
            cycles = 5
            override_segment = True
            new_segment = self._state._ss

        else:
            a, cycles = self.GetDoubleRegisterMod00(reg)

        disp = self.ToSigned16(self.GetPcWord()) if word else self.ToSigned8(self.GetPcByte())

        return ((a + disp) & 0xffff, cycles, override_segment, new_segment)

    # value, segment_a_valid, segment/, address of value, number of cycles
    def GetRegisterMem(self, reg: int, mod: int, w: bool) -> Tuple[int, bool, int, int, int]:
        if mod == 0:
            (a, cycles) = self.GetDoubleRegisterMod00(reg)

            segment =  self._state._segment_override if self._state._segment_override_set else self._state._ds

            if self._state._segment_override_set == False and (reg == 2 or reg == 3):  # BP uses SS
                segment = self._state._ss

            v = self.ReadMemWord(segment, a) if w else self.ReadMemByte(segment, a)

            cycles += 6

            return (v, True, segment, a, cycles)

        if mod == 1 or mod == 2:
            word = mod == 2

            (a, cycles, override_segment, new_segment) = self.GetDoubleRegisterMod01_02(reg, word)

            segment = self._state._segment_override if self._state._segment_override_set else self._state._ds

            if self._state._segment_override_set == False and override_segment:
                segment = new_segment

            if self._state._segment_override_set == False and (reg == 2 or reg == 3):  # BP uses SS
                segment = self._state._ss

            v = self.ReadMemWord(segment, a) if w else self.ReadMemByte(segment, a)

            cycles += 6

            return (v, True, segment, a, cycles)

        if mod == 3:
            v = self.GetRegister(reg, w)

            return (v, False, 0, 0, 0)

    def GetRegisterMem(self, reg: int, mod: int, w: bool):
        if mod == 0:
            a, cycles = self.GetDoubleRegisterMod00(reg)

            segment = self._state._segment_override if self._state._segment_override_set else self._state._ds

            if self._state._segment_override_set == False and (reg == 2 or reg == 3):  # BP uses SS
                segment = self._state._ss

            v = self.ReadMemWord(segment, a) if w else self.ReadMemByte(segment, a)

            cycles += 6

            return (v, True, segment, a, cycles)

        if mod == 1 or mod == 2:
            word = mod == 2

            a, cycles, override_segment, new_segment = self.GetDoubleRegisterMod01_02(reg, word)

            segment = self._state._segment_override if self._state._segment_override_set else self._state._ds

            if self._state._segment_override_set == False and override_segment:
                segment = new_segment

            if self._state._segment_override_set == False and (reg == 2 or reg == 3):  # BP uses SS
                segment = self._state._ss

            v = self.ReadMemWord(segment, a) if w else self.ReadMemByte(segment, a)

            cycles += 6

            return (v, True, segment, a, cycles)

        if mod == 3:
            v = self.GetRegister(reg, w)

            return (v, False, 0, 0, 0)

        return (0, False, 0, 0, 0)

    def UpdateRegisterMem(self, reg: int, mod: int, a_valid: bool, seg: int, addr: int, word: bool, v: int) -> int:
        if a_valid:
            assert seg >= 0 and seg <= 65535
            assert addr >= 0 and addr <= 65535
            if word:
                self.WriteMemWord(seg, addr, v)
            else:
                self.WriteMemByte(seg, addr, v & 0xff)
            return 4

        return self.PutRegisterMem(reg, mod, word, v)

    def PutRegister(self, reg: int, w: bool, val: int):
        if reg == 0:
            if w:
                self._state.SetAX(val)
            else:
                self._state.SetAL(val & 0xff)
        elif reg == 1:
            if w:
                self._state.SetCX(val)
            else:
                self._state._cl = val & 0xff
        elif reg == 2:
            if w:
                self._state.SetDX(val)
            else:
                self._state._dl = val & 0xff
        elif reg == 3:
            if w:
                self._state.SetBX(val)
            else:
                self._state._bl = val & 0xff
        elif reg == 4:
            if w:
                self._state._sp = val
            else:
                self._state.SetAH(val & 0xff)
        elif reg == 5:
            if w:
                self._state._bp = val
            else:
                self._state._ch = val
        elif reg == 6:
            if w:
                self._state._si = val
            else:
                self._state._dh = val
        elif reg == 7:
            if w:
                self._state._di = val
            else:
                self._state._bh = val

    def PutSRegister(self, reg: int, v: int):
        reg &= 0b00000011

        if reg == 0b000:
            self._state._es = v
        elif reg == 0b001:
            self._state._cs = v
        elif reg == 0b010:
            self._state._ss = v
        elif reg == 0b011:
            self._state._ds = v

    # returns cycle count
    def PutRegisterMem(self, reg: int, mod: int, w: bool, val: int) -> int:
        if mod == 0:
            (a, cycles) = self.GetDoubleRegisterMod00(reg)

            segment = self._state._segment_override if self._state._segment_override_set else self._state._ds

            if self._state._segment_override_set == False and (reg == 2 or reg == 3):  # BP uses SS
                segment = self._state._ss

            if w:
                self.WriteMemWord(segment, a, val)
            else:
                self.WriteMemByte(segment, a, val)

            cycles += 4

            return cycles

        if mod == 1 or mod == 2:
            (a, cycles, override_segment, new_segment) = self.GetDoubleRegisterMod01_02(reg, mod == 2)

            segment = self._state._segment_override if self._state._segment_override_set else self._state._ds

            if self._state._segment_override_set == False and override_segment:
                segment = new_segment

            if self._state._segment_override_set == False and (reg == 2 or reg == 3):  # BP uses SS
                segment = self._state._ss

            if w:
                self.WriteMemWord(segment, a, val)
            else:
                self.WriteMemByte(segment, a, val)

            cycles += 4

            return cycles

        if mod == 3:
            self.PutRegister(reg, w, val)
            return 0  # TODO

    # value, cycles
    def GetDoubleRegisterMod00(self, reg: int) -> Tuple[int, int]:
        a = None
        cycles = None

        if reg == 0:
            a = self._state.GetBX() + self._state._si
            cycles = 7

        elif reg == 1:
            a = self._state.GetBX() + self._state._di
            cycles = 8

        elif reg == 2:
            a = self._state._bp + self._state._si
            cycles = 8

        elif reg == 3:
            a = self._state._bp + self._state._di
            cycles = 7

        elif reg == 4:
            a = self._state._si
            cycles = 5

        elif reg == 5:
            a = self._state._di
            cycles = 5

        elif reg == 6:
            a = self.GetPcWord()
            cycles = 6

        elif reg == 7:
            a = self._state.GetBX()
            cycles = 5

        a &= 0xffff

        return (a, cycles)

    def SetLogicFuncFlags(self, word: bool, result: int):
        self._state.SetFlagO(False)
        self._state.SetFlagS(((result & 0x8000) if word else (result & 0x80)) != 0)
        self._state.SetFlagZ(result == 0 if word else (result & 0xff) == 0)
        self._state.SetFlagP(result)

        self._state.SetFlagA(False)  # undefined

        self._state.SetFlagC(False)

    def push(self, v: int):
        self._state._sp -= 2
        self._state._sp &= 0xffff
        self.WriteMemWord(self._state._ss, self._state._sp, v)

    def pop(self) -> int:
        v = self.ReadMemWord(self._state._ss, self._state._sp)
        self._state._sp += 2
        self._state._sp &= 0xffff
        return v

    def InvokeInterrupt(self, instr_start: int, interrupt_nr: int, pic: bool):
        self._state._segment_override_set = False

        if pic:
            self._io.GetPIC().SetIRQBeingServiced(interrupt_nr)
            interrupt_nr += self._io.GetPIC().GetInterruptOffset()

        self.push(self._state._flags)
        self.push(self._state._cs)
        if self._state._rep:
            self.push(self._state._rep_addr)
            self._state._rep = False

        else:
            self.push(instr_start)

        self._state.SetFlagI(False)
        self._state.SetFlagT(False)

        addr = interrupt_nr * 4

        self._state._ip = self.ReadMemWord(0, addr)
        self._state._cs = self.ReadMemWord(0, (addr + 2) & 0xffff)

    def IsProcessingRep(self) -> bool:
        return self._state._rep

    def PrefixMustRun(self) -> bool:
        rc = True

        if self._state._rep:
            cx = self._state.GetCX()

            if self._state._rep_do_nothing:
                self._state._rep = False
                rc = False

            else:
                cx -= 1
                self._state.SetCX(cx)

                if cx == 0:
                    self._state._rep = False
                elif self._state._rep_mode == state8088.State8088.RepMode.REPE_Z:
                    pass
                elif self._state._rep_mode == state8088.State8088.RepMode.REPNZ:
                    pass
                elif self._state._rep_mode == state8088.State8088.RepMode.REP:
                    pass
                else:
                    # unknown self._state._rep_mode
                    self._state._rep = False
                    rc = False

        self._state._rep_do_nothing = False

        return rc

    def PrefixEnd(self, opcode: int):
        if opcode in (0xa4, 0xa5, 0xa6, 0xa7, 0xaa, 0xab, 0xac, 0xad, 0xae, 0xaf):
            if self._state._rep_mode == state8088.State8088.RepMode.REPE_Z:
                # REPE/REPZ
                if self._state.GetFlagZ() != True:
                    self._state._rep = False

            elif self._state._rep_mode == state8088.State8088.RepMode.REPNZ:
                # REPNZ
                if self._state.GetFlagZ() != False:
                    self._state._rep = False
        else:
            self._state._rep = False

        if self._state._rep == False:
            self._state._segment_override_set = False

        if self._state._rep:
            self._state._ip = self._state._rep_addr

    def ResetCrashCounter(self):
        self._state._crash_counter = 0

    # cycle counts from https://zsmith.co/intel_i.php
    def Tick(self) -> int:
        cycle_count = 0  # cycles used for an instruction
        back_from_trace = False

        # check for interrupt
        if self._state.GetFlagI() == True and self._state._inhibit_interrupts == False:
            irq = self._io.GetPIC().GetPendingInterrupt()
            if irq != 255:
                for device in self._devices:
                    if device.GetIRQNumber() != irq:
                        continue

                    self._state._in_hlt = False
                    self.InvokeInterrupt(self._state._ip, irq, True)
                    cycle_count += 60
                    self._state._clock += cycle_count

                    return cycle_count

        self._state._inhibit_interrupts = False

        # T-flag produces an interrupt after each instruction
        if self._state.GetInHlt():
            cycle_count += 2
            self._state._clock += cycle_count  # time needs to progress for timers etc
            self._io.Tick(cycle_count, self._state._clock)
            return cycle_count

        instr_start = self._state._ip
        address = (self._state._cs * 16 + self._state._ip) & self._MemMask
        opcode = self.GetPcByte()

        if self._ignore_breakpoints:
            self._ignore_breakpoints = False

        else:
            if instr_start in self._breakpoints:
                self._stop_reason = f'Breakpoint reached at address {check_address:06x}'
                return -1

        # handle prefixes
        while opcode in (0x26, 0x2e, 0x36, 0x3e, 0xf2, 0xf3):
            if opcode == 0x26:
                self._state._segment_override = self._state._es
            elif opcode == 0x2e:
                self._state._segment_override = self._state._cs
            elif opcode == 0x36:
                self._state._segment_override = self._state._ss
            elif opcode == 0x3e:
                self._state._segment_override = self._state._ds
            elif opcode in (0xf2, 0xf3):
                self._state._rep = True
                self._state._rep_mode = state8088.State8088.RepMode.NotSet
                cycle_count += 9
                self._state._rep_do_nothing = self._state.GetCX() == 0

            address = (self._state._cs * 16 + self._state._ip) & self._MemMask
            next_opcode = self.GetPcByte()

            self._state._rep_opcode = next_opcode  # TODO: only allow for certain instructions

            if opcode == 0xf2:
                self._state._rep_addr = instr_start
                if next_opcode in (0xa6, 0xa7, 0xae, 0xaf):
                    self._state._rep_mode = state8088.State8088.RepMode.REPNZ
                else:
                    self._state._rep_mode = state8088.State8088.RepMode.REP
            elif opcode == 0xf3:
                self._state._rep_addr = instr_start
                if next_opcode in (0xa6, 0xa7, 0xae, 0xaf):
                    self._state._rep_mode = state8088.State8088.RepMode.REPE_Z
                else:
                    self._state._rep_mode = state8088.State8088.RepMode.REP
            else:
                self._state._segment_override_set = True  # TODO: move up
                cycle_count += 2

            opcode = next_opcode

        if opcode == 0x00:
            if self._terminate_on_off_the_rails == True:
                self._state._crash_counter += 1
                if self._state._crash_counter >= 5:
                    _stop_reason = f'Terminating because of {_state._crash_counter}x 0x00 opcode ({address:06x})'
                    return -1
        else:
            self._state._crash_counter = 0

        # main instruction handling
        if opcode in self._ops:
            cycle_count += self._ops[opcode](opcode)
        # special cases
        elif opcode == 0x9d:
            before = self._state.GetFlagT()
            self._state._flags = self.pop()
            if self._state.GetFlagT() and before == False:
                back_from_trace = True
            self._state.FixFlags()

            cycle_count += 12

        elif opcode == 0xcf:
            # IRET
            before = self._state.GetFlagT()

            self._state._ip = self.pop()
            self._state._cs = self.pop()
            self._state._flags = self.pop()
            self._state.FixFlags()

            if self._state.GetFlagT() and before == False:
                back_from_trace = True

            cycle_count += 32  # 44

        else:
            print(f'opcode {opcode:x} not implemented')

        self.PrefixEnd(opcode)

        if cycle_count == 0:
            cycle_count = 1  # TODO workaround

        self._state._clock += cycle_count

        # tick I/O
        self._io.Tick(cycle_count, self._state._clock)

        if self._state.GetFlagT() and back_from_trace == False and self._state._inhibit_interrupts == False:
            self.InvokeInterrupt(self._state._ip, 1, False)

        return cycle_count

    def Reset(self):
        self._state.Reset()
        self._state._cs = 0xf000
        self._state._ip = 0xfff0

    def GetStopReason(self) -> str:
        rc = self._stop_reason
        self._stop_reason = ''
        return rc

    def GetBreakpoints(self) -> set:
        return self._breakpoints

    def AddBreakpoint(self, a: int):
        self._breakpoints.add(a)

    def DelBreakpoint(self, a):
        del self._breakpoints[a]

    def ClearBreakpoints(self):
        self._breakpoints = set()

    # is only once
    def SetIgnoreBreakpoints(self):
        self._ignore_breakpoints = True

    def Op_NOP(self, opcode: int) -> int:  # 0x90
        return 4

    def Op_ADD_AL_xx(self, opcode: int) -> int:  # 0x04, 0x14
        # ADD AL,xx
        v = self.GetPcByte()

        flag_c = self._state.GetFlagC()
        use_flag_c = False

        result = self._state.GetAL() + v

        if opcode == 0x14:
            if flag_c:
                result += 1
            use_flag_c = True

        self.SetAddSubFlags(False, self._state.GetAL(), v, result, False, flag_c if use_flag_c else False)

        self._state.SetAL(result & 255)

        return 3

    def Op_ADD_AX_xxxx(self, opcode: int) -> int:  # 0x05, 0x15
        # ADD AX,xxxx
        v = self.GetPcWord()

        flag_c = self._state.GetFlagC()
        use_flag_c = False
        before = self._state.GetAX()

        result = before + v

        if opcode == 0x15:
            if flag_c:
                result += 1
            use_flag_c = True

        self.SetAddSubFlags(True, before, v, result, False, flag_c if use_flag_c else False)
        self._state.SetAX(result & 0xffff)

        return 3

    def Op_MOV_reg_ib(self, opcode: int) -> int:  # 0xb.
        # MOV reg,ib
        reg = opcode & 0x07
        word = (opcode & 0x08) == 0x08

        v = self.GetPcByte()
        if word:
            v |= self.GetPcByte() << 8

        self.PutRegister(reg, word, v)

        return 2

    def Op_CMP_OR_XOR_etc(self, opcode: int) -> int:  # 0x80-0x83
        # CMP and others
        o1 = self.GetPcByte()

        mod = o1 >> 6
        reg = o1 & 7

        function = (o1 >> 3) & 7

        r1 = 0
        a_valid = False
        seg = 0
        addr = 0

        r2 = 0

        word = False

        is_logic = False
        is_sub = False

        result = 0
        cycles = 0

        if opcode == 0x80:
            (r1, a_valid, seg, addr, cycles) = self.GetRegisterMem(reg, mod, False)
            r2 = self.GetPcByte()

        elif opcode == 0x81:
            (r1, a_valid, seg, addr, cycles) = self.GetRegisterMem(reg, mod, True)
            r2 = self.GetPcWord()
            word = True

        elif opcode == 0x82:
            (r1, a_valid, seg, addr, cycles) = self.GetRegisterMem(reg, mod, False)
            r2 = self.GetPcByte()

        elif opcode == 0x83:
            (r1, a_valid, seg, addr, cycles) = self.GetRegisterMem(reg, mod, True)

            r2 = self.GetPcByte()
            if (r2 & 128) == 128:
                r2 |= 0xff00

            word = True

        apply = True
        use_flag_c = False

        if function == 0:
            result = r1 + r2

        elif function == 1:
            result = r1 | r2
            is_logic = True

        elif function == 2:
            result = r1 + r2 + self._state.GetFlagC()
            use_flag_c = True

        elif function == 3:
            result = r1 - r2 - self._state.GetFlagC()
            is_sub = True
            use_flag_c = True

        elif function == 4:
            result = r1 & r2
            is_logic = True
            self._state.SetFlagC(False)

        elif function == 5:
            result = r1 - r2
            is_sub = True

        elif function == 6:
            result = r1 ^ r2
            is_logic = True

        elif function == 7:
            result = r1 - r2
            is_sub = True
            apply = False

        mask = 0xffff if word else 0xff

        if is_logic:
            self.SetLogicFuncFlags(word, result & mask)
        else:
            self.SetAddSubFlags(word, r1, r2, result, is_sub, self._state.GetFlagC() if use_flag_c else False)

        if apply:
            put_cycles = self.UpdateRegisterMem(reg, mod, a_valid, seg, addr, word, result & mask)
            cycles += put_cycles

        return 3 + cycles

    def Op_ADD_SUB_ADC_SBC(self, opcode: int) -> int:
        cycle_count = 0

        word = (opcode & 1) == 1
        direction = (opcode & 2) == 2
        o1 = self.GetPcByte()

        mod = o1 >> 6
        reg1 = (o1 >> 3) & 7
        reg2 = o1 & 7

        (r1, a_valid, seg, addr, get_cycles) = self.GetRegisterMem(reg2, mod, word)
        r2 = self.GetRegister(reg1, word)

        cycle_count += get_cycles

        result = 0
        is_sub = False
        apply = True
        use_flag_c = False

        if opcode <= 0x03:
            result = r1 + r2
            cycle_count += 4
        elif opcode >= 0x10 and opcode <= 0x13:
            use_flag_c = True
            result = r1 + r2 + self._state.GetFlagC()
            cycle_count += 4
        else:
            if direction:
                result = r2 - r1
            else:
                result = r1 - r2

            is_sub = True

            if opcode >= 0x38 and opcode <= 0x3b:
                apply = False
            elif opcode >= 0x28 and opcode <= 0x2b:
                  pass
            else:  # 0x18...0x1b
                use_flag_c = True
                result -= self._state.GetFlagC()

            cycle_count += 4

        new_flag_c = self._state.GetFlagC() if use_flag_c else False
        if direction:
            self.SetAddSubFlags(word, r2, r1, result, is_sub, new_flag_c)
        else:
            self.SetAddSubFlags(word, r1, r2, result, is_sub, new_flag_c)

        # 0x38...0x3b are CMP
        if apply:
            result &= 0xffff if word else 0xff
            if direction:
                self.PutRegister(reg1, word, result)
            else:
                override_to_ss = a_valid and word and self._state._segment_override_set == False and ((reg2 == 2 or reg2 == 3) and mod == 0)
                if override_to_ss:
                    seg = self._state._ss

                put_cycles = self.UpdateRegisterMem(reg2, mod, a_valid, seg, addr, word, result)
                cycle_count += put_cycles

        return cycle_count

    def Op_TEST(self, opcode: int) -> int:  # 0x84, 0x85
        # TEST ...,...
        word = (opcode & 1) == 1
        o1 = self.GetPcByte()

        mod = o1 >> 6
        reg1 = (o1 >> 3) & 7
        reg2 = o1 & 7

        (r1, a_valid, seg, addr, cycles) = self.GetRegisterMem(reg2, mod, word)
        r2 = self.GetRegister(reg1, word)

        if word:
            result = r1 & r2
            self.SetLogicFuncFlags(True, result)
        else:
            result = (r1 & r2) & 0xff
            self.SetLogicFuncFlags(False, result)

        self._state.SetFlagC(False)

        return 3 + cycles

    def Op_XCHG(self, opcode: int) -> int:
        # XCHG
        word = (opcode & 1) == 1
        o1 = self.GetPcByte()

        mod = o1 >> 6
        reg1 = (o1 >> 3) & 7
        reg2 = o1 & 7

        (r1, a_valid, seg, addr, get_cycles) = self.GetRegisterMem(reg2, mod, word)
        r2 = self.GetRegister(reg1, word)

        put_cycles = self.UpdateRegisterMem(reg2, mod, a_valid, seg, addr, word, r2)

        self.PutRegister(reg1, word, r1)

        return 3 + get_cycles + put_cycles

    def Op_XCHG_AX(self, opcode: int) -> int:  # 91...97
        # XCHG AX,...
        reg_nr = opcode & 0x07
        v = self.GetRegister(reg_nr, True)

        old_ax = self._state.GetAX()
        self._state.SetAX(v)

        self.PutRegister(reg_nr, True, old_ax)

        return 3

    def Op_fe_ff(self, opcode: int) -> int:
        cycle_count = 0

        # DEC and others
        word = (opcode & 1) == 1
        o1 = self.GetPcByte()
        mod = o1 >> 6
        reg = o1 & 7
        function = (o1 >> 3) & 7

        (v, a_valid, seg, addr, get_cycles) = self.GetRegisterMem(reg, mod, word)
        cycle_count += get_cycles

        if function == 0:
            # INC
            v += 1

            cycle_count += 3

            self._state.SetFlagO(v == 0x8000 if word else v == 0x80)
            self._state.SetFlagA((v & 15) == 0)

            self._state.SetFlagS((v & 0x8000) == 0x8000 if word else (v & 0x80) == 0x80)
            self._state.SetFlagZ(v == 0 if word else (v & 0xff) == 0)
            self._state.SetFlagP(v)

        elif function == 1:
            # DEC
            v -= 1

            cycle_count += 3

            self._state.SetFlagO(v == 0x7fff if word else v == 0x7f)
            self._state.SetFlagA((v & 15) == 15)

            self._state.SetFlagS((v & 0x8000) == 0x8000 if word else (v & 0x80) == 0x80)
            self._state.SetFlagZ(v == 0 if word else (v & 0xff) == 0)
            self._state.SetFlagP(v)

        elif function == 2:
            # CALL
            self.push(self._state._ip)

            self._state._rep = False
            self._state._ip = v

            cycle_count += 16

        elif function == 3:
            # CALL FAR
            self.push(self._state._cs)
            self.push(self._state._ip)

            self._state._ip = v
            self._state._cs = self.ReadMemWord(seg, addr + 2)

            cycle_count += 37

        elif function == 4:
            # JMP NEAR
            self._state._ip = v
            cycle_count += 18

        elif function == 5:
            # JMP
            self._state._cs = self.ReadMemWord(seg, (addr + 2) & 0xffff)
            self._state._ip = self.ReadMemWord(seg, addr)
            cycle_count += 15

        elif function == 6 or function == 7:
            # PUSH rmw
            if reg == 4 and mod == 3 and word == True:  # PUSH SP
                v -= 2
                self.WriteMemWord(self._state._ss, v, v)

            else:
                self.push(v)

            cycle_count += 16

        v &= 0xffff if word else 0xff

        put_cycles = self.UpdateRegisterMem(reg, mod, a_valid, seg, addr, word, v)

        return cycle_count + put_cycles

    def Op_LOOP(self, opcode: int) -> int:  # e0/e1/e2
        # LOOP
        cycle_count = 0

        to = self.GetPcByte()

        cx = self._state.GetCX()
        cx -= 1
        self._state.SetCX(cx)

        newAddresses = (self._state._ip + self.ToSigned8(to)) & 0xffff

        cycle_count += 4

        if opcode == 0xe2:
            if cx > 0:
                self._state._ip = newAddresses
                cycle_count += 4

        elif opcode == 0xe1:
            if cx > 0 and self._state.GetFlagZ() == True:
                self._state._ip = newAddresses
                cycle_count += 4

        elif opcode == 0xe0:
            if cx > 0 and self._state.GetFlagZ() == False:
                self._state._ip = newAddresses
                cycle_count += 4

        return cycle_count

    def Op_Jxx(self, opcode: int) -> int:
        # J..., 0x70/0x60
        to = self.GetPcByte()

        state = False
        if opcode == 0x70 or opcode == 0x60:
            state = self._state.GetFlagO()
        elif opcode == 0x71 or opcode == 0x61:
            state = self._state.GetFlagO() == False
        elif opcode == 0x72 or opcode == 0x62:
            state = self._state.GetFlagC()
        elif opcode == 0x73 or opcode == 0x63:
            state = self._state.GetFlagC() == False
        elif opcode == 0x74 or opcode == 0x64:
            state = self._state.GetFlagZ()
        elif opcode == 0x75 or opcode == 0x65:
            state = self._state.GetFlagZ() == False
        elif opcode == 0x76 or opcode == 0x66:
            state = self._state.GetFlagC() or self._state.GetFlagZ()
        elif opcode == 0x77 or opcode == 0x67:
            state = self._state.GetFlagC() == False and self._state.GetFlagZ() == False
        elif opcode == 0x78 or opcode == 0x68:
            state = self._state.GetFlagS()
        elif opcode == 0x79 or opcode == 0x69:
            state = self._state.GetFlagS() == False
        elif opcode == 0x7a or opcode == 0x6a:
            state = self._state.GetFlagP()
        elif opcode == 0x7b or opcode == 0x6b:
            state = self._state.GetFlagP() == False
        elif opcode == 0x7c or opcode == 0x6c:
            state = self._state.GetFlagS() != self._state.GetFlagO()
        elif opcode == 0x7d or opcode == 0x6d:
            state = self._state.GetFlagS() == self._state.GetFlagO()
        elif opcode == 0x7e or opcode == 0x6e:
            state = self._state.GetFlagZ() == True or self._state.GetFlagS() != self._state.GetFlagO()
        elif opcode == 0x7f or opcode == 0x6f:
            state = self._state.GetFlagZ() == False and self._state.GetFlagS() == self._state.GetFlagO()

        if state:
            self._state._ip = (self._state._ip + self.ToSigned8(to)) & 0xffff
            return 16

        return 4

    def Op_shift(self, opcode: int) -> int:
        cycle_count = 0
        word = (opcode & 1) == 1
        o1 = self.GetPcByte()

        mod = o1 >> 6
        reg1 = o1 & 7

        (v1, a_valid, seg, addr, get_cycles) = self.GetRegisterMem(reg1, mod, word)
        cycle_count += get_cycles

        count = 1
        if (opcode & 2) == 2:
            count = self._state._cl

        count_1_of = opcode in (0xd0, 0xd1, 0xd2, 0xd3)

        oldSign = (v1 & 0x8000 if word else v1 & 0x80) != 0

        set_flags = False

        mode = (o1 >> 3) & 7

        check_bit = 32768 if word else 128
        check_bit2 = 16384 if word else 64

        if mode == 0:
            # ROL
            for i in range(count):
                b7 = (v1 & check_bit) == check_bit

                self._state.SetFlagC(b7)

                v1 <<= 1
                if b7:
                    v1 |= 1

            if count_1_of:
                self._state.SetFlagO(self._state.GetFlagC() ^ ((v1 & check_bit) == check_bit))

            cycle_count += 2

        elif mode == 1:
            # ROR
            for i in range(count):
                b0 = (v1 & 1) == 1

                self._state.SetFlagC(b0)

                v1 >>= 1
                if b0:
                    v1 |= check_bit

            if count_1_of:
                self._state.SetFlagO(((v1 & check_bit) == check_bit) ^ ((v1 & check_bit2) == check_bit2))

            cycle_count += 2

        elif mode == 2:
            # RCL
            for i in range(count):
                new_carry = (v1 & check_bit) == check_bit
                v1 <<= 1

                oldCarry = self._state.GetFlagC()

                if oldCarry:
                    v1 |= 1

                self._state.SetFlagC(new_carry)

            if count_1_of:
                self._state.SetFlagO(self._state.GetFlagC() ^ ((v1 & check_bit) == check_bit))

            cycle_count += 2

        elif mode == 3:
            # RCR
            for i in range(count):
                new_carry = (v1 & 1) == 1
                v1 >>= 1

                oldCarry = self._state.GetFlagC()
                if oldCarry:
                    v1 |= 0x8000 if word else 0x80

                self._state.SetFlagC(new_carry)

            if count_1_of:
                self._state.SetFlagO(((v1 & check_bit) == check_bit) ^ ((v1 & check_bit2) == check_bit2))

            cycle_count += 2

        elif mode == 4:
            prev_v1 = v1

            # SAL/SHL
            for i in range(count):
                new_a_carry = (v1 & 0x08) == 0x08
                new_carry = (v1 & check_bit) == check_bit
                v1 <<= 1
                self._state.SetFlagA(new_a_carry)
                self._state.SetFlagC(new_carry)

            set_flags = count != 0
            if set_flags:
                self._state.SetFlagO(((v1 & check_bit) == check_bit) ^ self._state.GetFlagC())

            cycle_count += count * 4

        elif mode == 5:
            org_v1 = v1

            # SHR
            for i in range(count):
                new_carry = (v1 & 1) == 1
                v1 >>= 1
                self._state.SetFlagC(new_carry)

            set_flags = count != 0

            self._state.SetFlagA(False)

            if count == 1:
                self._state.SetFlagO((org_v1 & check_bit) != 0)
            else:
                self._state.SetFlagO(False)

            cycle_count += count * 4

        elif mode == 6:
            if opcode >= 0xd2:
                # SETMOC
                if self._state._cl != 0:
                    self._state.SetFlagC(False)
                    self._state.SetFlagA(False)
                    self._state.SetFlagZ(False)
                    self._state.SetFlagO(False)
                    self._state.SetFlagP(0xff)
                    self._state.SetFlagS(True)

                    v1 = 0xffff if word else 0xff

                    cycle_count += 5 if word else 4
            else:
                # SETMO
                self._state.SetFlagC(False)
                self._state.SetFlagA(False)
                self._state.SetFlagZ(False)
                self._state.SetFlagO(False)
                self._state.SetFlagP(0xff)
                self._state.SetFlagS(True)

                v1 = 0xffff if word else 0xff

                cycle_count += 3 if word else 2

        elif mode == 7:
            # SAR
            mask = check_bit if (v1 & check_bit) != 0 else 0

            for i in range(count):
                new_carry = (v1 & 0x01) == 0x01
                v1 >>= 1
                v1 |= mask
                self._state.SetFlagC(new_carry)

            set_flags = count != 0
            if set_flags:
                self._state.SetFlagO(False)

            self._state.SetFlagA(False)

            cycle_count += 2

        v1 &= 0xffff if word else 0xff

        if set_flags:
            self._state.SetFlagS((v1 & 0x8000 if word else v1 & 0x80) != 0)
            self._state.SetFlagZ(v1 == 0)
            self._state.SetFlagP(v1)

        put_cycles = self.UpdateRegisterMem(reg1, mod, a_valid, seg, addr, word, v1)
        return cycle_count + put_cycles

    def Op_FPU(self, opcode: int) -> int:
        # FPU
        o1 = self.GetPcByte()
        mod = o1 >> 6
        reg1 = o1 & 7
        (v1, a_valid, seg, addr, get_cycles) = self.GetRegisterMem(reg1, mod, False)
        return get_cycles + 2

    def Op_FWAIT(self, opcode: int) -> int:  # 0x9b
        # FWAIT
        return 2  # TODO

    def Op_REFT(self, opcode: int) -> int:
        # RETF n / RETF
        nToRelease = self.GetPcWord() if (opcode == 0xca or opcode == 0xc8) else 0

        self._state._ip = self.pop()
        self._state._cs = self.pop()

        if opcode == 0xca or opcode == 0xc8:
            self._state._sp += nToRelease
            return 33 if opcode == 0xca else 24

        return 34 if opcode == 0xcb else 20

    def Op_MOV(self, opcode: int) -> int:
        # MOV
        word = (opcode & 1) == 1

        o1 = self.GetPcByte()
        mod = o1 >> 6
        mreg = o1 & 7

        cycle_count = 2  # base (correct?)

        # get address to write to ('seg, addr')
        (dummy, a_valid, seg, addr, get_cycles) = self.GetRegisterMem(mreg, mod, word)
        cycle_count += get_cycles

        if word:
            # the value follows
            v = self.GetPcWord()
            put_cycles = self.UpdateRegisterMem(mreg, mod, a_valid, seg, addr, word, v)
            cycle_count += put_cycles
        else:
            # the value follows
            v = self.GetPcByte()
            put_cycles = self.UpdateRegisterMem(mreg, mod, a_valid, seg, addr, word, v)
            cycle_count += put_cycles

        return cycle_count

    def Op_INC_DEC(self, opcode: int) ->int:
        # INC/DECw
        reg = (opcode - 0x40) & 7
        v = self.GetRegister(reg, True)
        isDec = opcode >= 0x48

        if isDec:
            v -= 1
            self._state.SetFlagO(v == 0x7fff)
            self._state.SetFlagA((v & 15) == 15)
        else:
            v += 1
            self._state.SetFlagO(v == 0x8000)
            self._state.SetFlagA((v & 15) == 0)

        v &= 0xffff

        self._state.SetFlagS((v & 0x8000) == 0x8000)
        self._state.SetFlagZ(v == 0)
        self._state.SetFlagP(v)

        self.PutRegister(reg, True, v)

        return 3

    def Op_MOV2(self, opcode: int) -> int:
        cycle_count = 0
        dir = (opcode & 2) == 2 # direction
        word = (opcode & 1) == 1 # b/w

        o1 = self.GetPcByte()
        mode = o1 >> 6
        reg = (o1 >> 3) & 7
        rm = o1 & 7

        sreg = opcode == 0x8e or opcode == 0x8c
        if sreg:
            word = True
            self._state._inhibit_interrupts = opcode == 0x8e

        cycle_count += 13

        # 88: rm < r (byte) 00  False,byte
        # 89: rm < r (word) 01  False,word  <--
        # 8a: r < rm (byte) 10  True, byte
        # 8b: r < rm (word) 11  True, word

        # 89|E6 mode 3, reg 4, rm 6, dir False, word True, sreg False

        if dir:
            # to 'rm' from 'REG'
            (v, a_valid, seg, addr, get_cycles) = self.GetRegisterMem(rm, mode, word)
            cycle_count += get_cycles

            if sreg:
                self.PutSRegister(reg, v)
            else:
                self.PutRegister(reg, word, v)
        else:
            # from 'REG' to 'rm'
            v = 0
            if sreg:
                v = self.GetSRegister(reg)
            else:
                v = self.GetRegister(reg, word)

            put_cycles = self.PutRegisterMem(rm, mode, word, v)
            cycle_count += put_cycles

        return cycle_count

    def Op_TEST_others(self, opcode: int) -> int:
        # TEST and others
        cycle_count = 0
        word = (opcode & 1) == 1

        o1 = self.GetPcByte()
        mod = o1 >> 6
        reg1 = o1 & 7

        (r1, a_valid, seg, addr, get_cycles) = self.GetRegisterMem(reg1, mod, word)
        cycle_count += get_cycles

        function = (o1 >> 3) & 7
        if function == 0 or function == 1:
            # TEST
            if word:
                r2 = self.GetPcWord()

                result = r1 & r2
                self.SetLogicFuncFlags(True, result)

                self._state.SetFlagC(False)
            else:
                r2 = self.GetPcByte()
                result = r1 & r2
                self.SetLogicFuncFlags(word, result)

                self._state.SetFlagC(False)

        elif function == 2:
            # NOT
            put_cycles = self.UpdateRegisterMem(reg1, mod, a_valid, seg, addr, word, ~r1 & 0xffff)
            cycle_count += put_cycles
        elif function == 3:
            # NEG
            result = -r1 & 0xffff

            self.SetAddSubFlags(word, 0, r1, -r1, True, False)
            self._state.SetFlagC(r1 != 0)

            put_cycles = self.UpdateRegisterMem(reg1, mod, a_valid, seg, addr, word, result)
            cycle_count += put_cycles

        elif function == 4:
            negate = self._state._rep_mode == state8088.State8088.RepMode.REP and self._state._rep
            self._state._rep = False

            # MUL
            if word:
                ax = self._state.GetAX()
                resulti = ax * r1

                dx_ax = resulti & 0xffffffff
                if negate:
                    dx_ax = -dx_ax
                self._state.SetAX(dx_ax & 0xffff)
                self._state.SetDX(dx_ax >> 16)

                flag = self._state.GetDX() != 0
                self._state.SetFlagC(flag)
                self._state.SetFlagO(flag)

                cycle_count += 118
            else:
                result = self._state.GetAL() * r1
                if negate:
                    result = -result
                self._state.SetAX(result)

                flag = self._state.GetAH() != 0
                self._state.SetFlagC(flag)
                self._state.SetFlagO(flag)

                cycle_count += 70

        elif function == 5:
            negate = self._state._rep_mode == state8088.State8088.RepMode.REP and self._state._rep
            self._state._rep = False

            # IMUL
            if word:
                ax = self.ToSigned16(self._state.GetAX())
                resulti = ax * self.ToSigned16(r1)

                dx_ax = resulti
                if negate:
                    dx_ax = -dx_ax
                self._state.SetAX(dx_ax & 0xffff)
                self._state.SetDX(dx_ax >> 16)

                flag = self.ToSigned16(self._state.GetAX()) != resulti
                self._state.SetFlagC(flag)
                self._state.SetFlagO(flag)

                cycle_count += 128

            else:
                result = self.ToSigned8(self._state.GetAL()) * self.ToSigned8(r1)
                if negate:
                    result = -result
                self._state.SetAX(result)

                self._state.SetFlagS((self._state.GetAH() & 128) == 128)
                flag = self.ToSigned8(self._state.GetAL()) != self.ToSigned16(result)
                self._state.SetFlagC(flag)
                self._state.SetFlagO(flag)

                cycle_count += 80

        elif function == 6:
            self._state.SetFlagC(False)
            self._state.SetFlagO(False)

            # DIV
            if word:
                dx_ax = (self._state.GetDX() << 16) | self._state.GetAX()

                if r1 == 0 or dx_ax // r1 >= 0x10000:
                    self._state.SetZSPFlags(self._state.GetAH())
                    self._state.SetFlagA(False)
                    self.InvokeInterrupt(self._state._ip, 0x00, False)  # divide by zero or divisor too small
                else:
                    self._state.SetAX(dx_ax // r1)
                    self._state.SetDX(dx_ax % r1)

            else:
                ax = self._state.GetAX()

                if r1 == 0 or ax // r1 >= 0x100:
                    self._state.SetZSPFlags(self._state.GetAH())
                    self._state.SetFlagA(False)
                    self.InvokeInterrupt(self._state._ip, 0x00, False)  # divide by zero or divisor too small
                else:
                    self._state.SetAL(ax // r1)
                    self._state.SetAH(ax % r1)

        elif function == 7:
            negate = self._state._rep_mode == state8088.State8088.RepMode.REP and self._state._rep
            self._state._rep = False

            self._state.SetFlagC(False)
            self._state.SetFlagO(False)

            # IDIV
            if word:
                dx_ax = (self._state.GetDX() << 16) | self._state.GetAX()
                r1s = self.ToSigned16(r1)

                if r1s == 0 or dx_ax // r1s > 0x7fffffff or dx_ax // r1s < -0x80000000:
                    self._state.SetZSPFlags(self._state.GetAH())
                    self._state.SetFlagA(False)
                    self.InvokeInterrupt(self._state._ip, 0x00, False)  # divide by zero or divisor too small
                else:
                    if negate:
                        self._state.SetAX((-(dx_ax // r1s)) & 0xffff)
                    else:
                        self._state.SetAX((dx_ax // r1s) & 0xffff)
                    self._state.SetDX((dx_ax % r1s) & 0xffff)
            else:
                ax = self.ToSigned16(self._state.GetAX())
                r1s = self.ToSigned8(r1)

                if r1s == 0 or ax // r1s > 0x7fff or ax // r1s < -0x8000:
                    self._state.SetZSPFlags(self._state.GetAH())
                    self._state.SetFlagA(False)
                    self.InvokeInterrupt(self._state._ip, 0x00, False)  # divide by zero or divisor too small
                else:
                    if negate:
                        self._state.SetAL(-(ax // r1s) & 0xff)
                    else:
                        self._state.SetAL((ax // r1s) & 0xff)
                    self._state.SetAH((ax % r1s) & 0xff)

        return cycle_count + 4

    def Op_INT(self, opcode: int) -> int:
        # INT 0x..
        if opcode != 0xce or self._state.GetFlagO():
            int = 0

            if opcode == 0xcc:
                int = 3
            elif opcode == 0xce:
                int = 4
            else:
                int = self.GetPcByte()

            addr = (int * 4) & 0xffff

            self.push(self._state._flags)
            self.push(self._state._cs)
            if self._state._rep:
                self.push(self._state._rep_addr)
            else:
                self.push(self._state._ip)

            self._state.SetFlagI(False)

            self._state._ip = self.ReadMemWord(0, addr)
            self._state._cs = self.ReadMemWord(0, addr + 2)

            return 51  # 71  TODO

        return 0  # TODO

    def Op_CMP(self, opcode: int) -> int:
        # CMP
        word = (opcode & 1) == 1

        result = 0

        r1 = 0
        r2 = 0

        cycle_count = 4

        if opcode == 0x3d:
            r1 = self._state.GetAX()
            r2 = self.GetPcWord()

            result = r1 - r2

        elif opcode == 0x3c:
            r1 = self._state.GetAL()
            r2 = self.GetPcByte()

            result = r1 - r2

        self.SetAddSubFlags(word, r1, r2, result, True, False)

        return cycle_count

    def Op_logic_functions(self, opcode: int) -> int:
        word = (opcode & 1) == 1
        direction = (opcode & 2) == 2
        o1 = self.GetPcByte()

        mod = o1 >> 6
        reg1 = (o1 >> 3) & 7
        reg2 = o1 & 7

        (r1, a_valid, seg, addr, get_cycles) = self.GetRegisterMem(reg2, mod, word)
        r2 = self.GetRegister(reg1, word)

        cycle_count = get_cycles + 3

        result = 0

        function = opcode >> 4
        if function == 0:
            result = r1 | r2
        elif function == 2:
            result = r2 & r1
        elif function == 3:
            result = r2 ^ r1

        self.SetLogicFuncFlags(word, result)

        if direction:
            self.PutRegister(reg1, word, result)
        else:
            put_cycles = self.UpdateRegisterMem(reg2, mod, a_valid, seg, addr, word, result)
            cycle_count += put_cycles

        return cycle_count

    def Op_OR_AND_XOR(self, opcode: int) -> int:
        word = (opcode & 1) == 1

        bLow = self.GetPcByte()
        bHigh = self.GetPcByte() if word else 0

        function = opcode >> 4
        if function == 0:
            self._state._al |= bLow

            if word:
                self._state._ah |= bHigh

        elif function == 2:
            self._state._al &= bLow

            if word:
                self._state._ah &= bHigh

            self._state.SetFlagC(False)

        elif function == 3:
            self._state._al ^= bLow

            if word:
                self._state._ah ^= bHigh

        self.SetLogicFuncFlags(word, self._state.GetAX() if word else self._state.GetAL())

        self._state.SetFlagP(self._state.GetAL())

        return 4

    def Op_RET2(self, opcode: int) -> int:
        nToRelease = self.GetPcWord()

        # RET
        self._state._ip = self.pop()
        self._state._sp += nToRelease

        return 16

    def Op_RET3(self, opcode: int) -> int:
        # RET
        self._state._ip = self.pop()

        return 16

    def Op_LES_LDS(self, opcode: int) -> int:  # c4/c5
        # LES (c4) / LDS (c5)
        o1 = self.GetPcByte()
        mod = o1 >> 6
        reg = (o1 >> 3) & 7
        rm = o1 & 7

        (val, a_valid, seg, addr, get_cycles) = self.GetRegisterMem(rm, mod, True)

        if opcode == 0xc4:
            self._state._es = self.ReadMemWord(seg, (addr + 2) & 0xffff)
        else:
            self._state._ds = self.ReadMemWord(seg, (addr + 2) & 0xffff)

        self.PutRegister(reg, True, val)

        return 24 + get_cycles

    def Op_IN_AL_DX(self, opcode: int) -> int:  # 0xec
        # IN AL,DX
        val = self._io.In(self._state.GetDX(), False)
        self._state.SetAL(val & 0xff)

        return 12

    def Op_IN_AX_DX(self, opcode: int) -> int:  # 0xed
        # IN AX,DX
        val = self._io.In(self._state.GetDX(), True)
        self._state.SetAX(val)
        return 12

    def Op_OUT_DX_AL(self, opcode: int) -> int:  # 0xee
        # OUT
        self._io.Out(self._state.GetDX(), self._state.GetAL(), False)
        return 12

    def Op_OUT_DX_AX(self, opcode: int) -> int:  # 0xef
        # OUT
        self._io.Out(self._state.GetDX(), self._state.GetAX(), True)
        return 12

    def Op_TEST_AL(self, opcode: int) -> int:  # 0xa8
        # TEST AL,..
        v = self.GetPcByte()
        result = self._state.GetAL() & v
        self.SetLogicFuncFlags(False, result)
        self._state.SetFlagC(False)
        return 5

    def Op_TEST_AX(self, opcode: int) -> int:  # 0xa9
        # TEST AX,..
        v = self.GetPcWord()
        result = self._state.GetAX() & v
        self.SetLogicFuncFlags(True, result)
        self._state.SetFlagC(False)
        return 5

    def Op_STOSB(self, opcode: int) -> int:  # 0xaa
        if self.PrefixMustRun():
            # STOSB
            self.WriteMemByte(self._state._es, self._state._di, self._state.GetAL())
            self._state._di += -1 if self._state.GetFlagD() else 1
            self._state._di &= 0xffff
            return 11
        return 0  # TODO

    def Op_STOSW(self, opcode: int) -> int:  # 0xab
        if self.PrefixMustRun():
            # STOSW
            self.WriteMemWord(self._state._es, self._state._di, self._state.GetAX())
            self._state._di += -2 if self._state.GetFlagD() else 2
            self._state._di &= 0xffff
            return 11
        return 0  # TODO

    def Op_JCXZ(self, opcode: int) -> int:  # 0xe3
        # JCXZ np
        offset = self.ToSigned8(self.GetPcByte())

        addr = self._state._ip + offset

        if self._state.GetCX() == 0:
            self._state._ip = addr
            return 18

        return 6

    def Op_IN_AL_ib(self, opcode: int) -> int:  # 0xe4
        # IN AL,ib
        from_ = self.GetPcByte()

        val = self._io.In(from_, False)
        self._state.SetAL(val & 0xff)

        return 14

    def Op_IN_AX_ib(self, opcode: int) -> int:  #  0xe5
        # IN AX,ib
        from_ = self.GetPcByte()

        val = self._io.In(from_, True)
        self._state.SetAX(val)

        return 14

    def Op_OUT_AL(self, opcode: int) -> int:  # 0xe6
        # OUT
        to = self.GetPcByte()
        self._io.Out(to, self._state.GetAL(), False)
        return 10  # max 14

    def Op_OUT_AX(self, opcode: int) -> int:  # 0xe7
        # OUT
        to = self.GetPcByte()
        self._io.Out(to, self._state.GetAX(), True)
        return 10  # max 14

    def Op_XLATB(self, opcode: int) -> int:  # 0xd7
        # XLATB
        old_al = self._state.GetAL()
        self._state.SetAL(self.ReadMemByte(self._state._segment_override if self._state._segment_override_set else  self._state._ds, (self._state.GetBX() + self._state.GetAL()) & 0xffff))
        return 11

    def Op_MOVSB(self, opcode: int) -> int:  # 0xa4
        if self.PrefixMustRun():
            # MOVSB
            segment = self._state._segment_override if self._state._segment_override_set else self._state._ds
            v = self.ReadMemByte(segment, self._state._si)
            self.WriteMemByte(self._state._es, self._state._di, v)

            self._state._si += -1 if self._state.GetFlagD() else 1
            self._state._si &= 0xffff
            self._state._di += -1 if self._state.GetFlagD() else 1
            self._state._di &= 0xffff

            return 18

        return 0  # TODO

    def Op_MOVSW(self, opcode: int) -> int:  # 0xa5
        if self.PrefixMustRun():
            # MOVSW
            self.WriteMemWord(self._state._es, self._state._di, self.ReadMemWord(self._state._segment_override if self._state._segment_override_set else self._state._ds, self._state._si))

            self._state._si += -2 if self._state.GetFlagD() else 2
            self._state._si &= 0xffff
            self._state._di += -2 if self._state.GetFlagD() else 2
            self._state._di &= 0xffff

            return 26

        return 0  # TODO

    def Op_CMPSB(self, opcode: int) -> int:  # 0xa6
        if self.PrefixMustRun():
            # CMPSB
            v1 = self.ReadMemByte(self._state._segment_override if self._state._segment_override_set else  self._state._ds, self._state._si)
            v2 = self.ReadMemByte(self._state._es, self._state._di)

            result = v1 - v2

            self._state._si += -1 if self._state.GetFlagD() else 1
            self._state._si &= 0xffff
            self._state._di += -1 if self._state.GetFlagD() else 1
            self._state._di &= 0xffff

            self.SetAddSubFlags(False, v1, v2, result, True, False)

            return 30

        return 0  # TODO

    def Op_CMPSW(self, opcode: int) -> int:  # 0xa7
        if self.PrefixMustRun():
            # CMPSW
            v1 = self.ReadMemWord(self._state._segment_override if self._state._segment_override_set else self._state._ds, self._state._si)
            v2 = self.ReadMemWord(self._state._es, self._state._di)

            result = v1 - v2

            self._state._si += -2 if self._state.GetFlagD() else 2
            self._state._si &= 0xffff
            self._state._di += -2 if self._state.GetFlagD() else 2
            self._state._di &= 0xffff

            self.SetAddSubFlags(True, v1, v2, result, True, False)

            return 30

        return 0  # TODO

    def Op_MOV_AL_mem(self, opcode: int) -> int:  # 0xa0
        # MOV AL,[...]
        a = self.GetPcWord()
        self._state.SetAL(self.ReadMemByte(self._state._segment_override if self._state._segment_override_set else self._state._ds, a))
        return 12

    def Op_MOV_AX_mem(self, opcode: int) -> int:  # 0xa1
        # MOV AX,[...]
        a = self.GetPcWord()
        self._state.SetAX(self.ReadMemWord(self._state._segment_override if self._state._segment_override_set else self._state._ds, a))
        return 12

    def Op_MOV_mem_AL(self, opcode: int) -> int:  # 0xa2
        # MOV [...],AL
        a = self.GetPcWord()
        self.WriteMemByte(self._state._segment_override if self._state._segment_override_set else self._state._ds, a, self._state.GetAL())
        return 13

    def Op_MOV_mem_AX(self, opcode: int) -> int:  # 0xa3
        # MOV [...],AX
        a = self.GetPcWord()
        self.WriteMemWord(self._state._segment_override if self._state._segment_override_set else self._state._ds, a, self._state.GetAX())
        return 13

    def Op_PUSH_ES(self, opcode: int) -> int:  # 0x06
        # PUSH ES
        self.push(self._state._es)
        return 15

    def Op_POP_ES(self, opcode: int) -> int:  # 0x07
        # POP ES
        self._state._es = self.pop()
        self._state._inhibit_interrupts = True
        return 12

    def Op_PUSH_CS(self, opcode: int) -> int:  # 0x0e
        # PUSH CS
        self.push(self._state._cs)
        return 15

    def Op_POP_CS(self, opcode: int) -> int:  # 0x0f
        # POP CS
        self._state._cs = self.pop()
        self._state._inhibit_interrupts = True
        return 12

    def Op_PUSH_SS(self, opcode: int) -> int:  # 0x16
        # PUSH SS
        self.push(self._state._ss)
        return 15

    def Op_POP_SS(self, opcode: int) -> int:  # 0x17
        # POP SS
        self._state._ss = self.pop()
        self._state._inhibit_interrupts = True
        return 12

    def Op_PUSH_DS(self, opcode: int) -> int:  # 0x1e
        # PUSH DS
        self.push(self._state._ds)
        return 11  # 15

    def Op_POP_DS(self, opcode: int) -> int:  # 0x1f
        # POP DS
        self._state._ds = self.pop()
        self._state._inhibit_interrupts = True
        return 8

    def Op_PUSH_AX(self, opcode: int) -> int:  # 0x50
        # PUSH AX
        self.push(self._state.GetAX())
        return 15

    def Op_PUSH_CX(self, opcode: int) -> int:  # 0x51
        # PUSH CX
        self.push(self._state.GetCX())
        return 15

    def Op_PUSH_DX(self, opcode: int) -> int:  # 0x52
        # PUSH DX
        self.push(self._state.GetDX())
        return 15

    def Op_PUSH_BX(self, opcode: int) -> int:  # 0x53
        # PUSH BX
        self.push(self._state.GetBX())
        return 15

    def Op_PUSH_SP(self, opcode: int) -> int:  # 0x54
        # PUSH SP
        # special case, see:
        # https:#c9x.me/x86/html/file_module_x86_id_269.html
        self._state._sp -= 2
        self.WriteMemWord(self._state._ss, self._state._sp, self._state._sp)
        return 15

    def Op_PUSH_BP(self, opcode: int) -> int:  # 0x55
        # PUSH BP
        self.push(self._state._bp)
        return 15

    def Op_PUSH_SI(self, opcode: int) -> int:  # 0x56
        # PUSH SI
        self.push(self._state._si)
        return 15

    def Op_PUSH_DI(self, opcode: int) -> int:  # 0x57
        # PUSH DI
        self.push(self._state._di)
        return 15

    def Op_POP_rmw(self, opcode: int) -> int:  # 0x8f
        # POP rmw
        o1 = self.GetPcByte()
        mod = o1 >> 6
        reg2 = o1 & 7

        put_cycles = self.PutRegisterMem(reg2, mod, True, self.pop())
        return put_cycles + 17

    def Op_PUSHF(self, opcode: int) -> int:  # 0x9c
        # PUSHF
        self.push(self._state._flags)
        return 14

    def Op_POP_AX(self, opcode: int) -> int:  # 0x58
        # POP AX
        self._state.SetAX(self.pop())
        return 8

    def Op_POP_CX(self, opcode: int) -> int:  # 0x59
        # POP CX
        self._state.SetCX(self.pop())
        return 8

    def Op_POP_DX(self, opcode: int) -> int:  # 0x5a
        # POP DX
        self._state.SetDX(self.pop())
        return 8

    def Op_POP_BX(self, opcode: int) -> int:  # 0x5b
        # POP BX
        self._state.SetBX(self.pop())
        return 8

    def Op_POP_SP(self, opcode: int) -> int:  # 0x5c
        # POP SP
        self._state._sp = self.pop()
        return 8

    def Op_POP_BP(self, opcode: int) -> int:  # 0x5d
        # POP BP
        self._state._bp = self.pop()
        return 8

    def Op_POP_SI(self, opcode: int) -> int:  # 0x5e
        # POP SI
        self._state._si = self.pop()
        return 8

    def Op_POP_DI(self, opcode: int) -> int:  # 0x5f
        # POP DI
        self._state._di = self.pop()
        return 8

    def Op_SBB_AL_ib(self, opcode: int) -> int:  # 0x1c
        # SBB AL,ib
        v = self.GetPcByte()
        flag_c = self._state.GetFlagC()
        result = self._state.GetAL() - v
        if flag_c:
            result -= 1

        self.SetAddSubFlags(False, self._state.GetAL(), v, result, True, flag_c)
        self._state.SetAL(result & 0xff)

        return 3

    def Op_SBB_AX_iw(self, opcode: int) -> int:  # 0x1d
        # SBB AX,iw
        v = self.GetPcWord()
        AX = self._state.GetAX()
        flag_c = self._state.GetFlagC()
        result = AX - v
        if flag_c:
            result -= 1

        self.SetAddSubFlags(True, AX, v, result, True, flag_c)
        self._state.SetAX(result & 0xffff)

        return 3

    def Op_SUB_AL_ib(self, opcode: int) -> int:  # 0x2c
        # SUB AL,ib
        v = self.GetPcByte()
        result = self._state.GetAL() - v

        self.SetAddSubFlags(False, self._state.GetAL(), v, result, True, False)
        self._state.SetAL(result & 0xff)

        return 3

    def Op_SUB_AX_iw(self, opcode: int) -> int:  # 0x2d
        # SUB AX,iw
        v = self.GetPcWord()
        before = self._state.GetAX()
        result = before - v

        self.SetAddSubFlags(True, before, v, result, True, False)
        self._state.SetAX(result & 0xffff)

        return 3

    def Op_DAA(self, opcode: int) -> int:  # 0x27
        # DAA
        # https://www.felixcloutier.com/x86/daa
        old_al = self._state.GetAL()
        old_af = self._state.GetFlagA()
        old_cf = self._state.GetFlagC()

        self._state.SetFlagC(False)

        if ((self._state.GetAL() & 0x0f) > 9) or self._state.GetFlagA() == True:
            add_carry = self._state.GetAL() + 0x06 > 255

            self._state.SetAL((self._state.GetAL() + 0x06) & 0xff)
            self._state.SetFlagC(old_cf or add_carry)
            self._state.SetFlagA(True)
        else:
            self._state.SetFlagA(False)

        upper_nibble_check = 0x9f if old_af else 0x99

        if old_al > upper_nibble_check or old_cf:
            self._state.SetAL((self._state.GetAL() + 0x60) & 0xff)
            self._state.SetFlagC(True)
        else:
            self._state.SetFlagC(False)

        self._state.SetZSPFlags(self._state.GetAL())

        return 4

    def Op_DAS(self, opcode: int) -> int:  # 0x2f
        old_al = self._state.GetAL()
        old_af = self._state.GetFlagA()
        old_cf = self._state.GetFlagC()

        self._state.SetFlagC(False)

        if (self._state.GetAL() & 0x0f) > 9 or self._state.GetFlagA() == True:
            self._state.SetAL((self._state.GetAL() - 0x06) & 0xff)
            self._state.SetFlagA(True)
        else:
            self._state.SetFlagA(False)

        upper_nibble_check = 0x9f if old_af else 0x99

        if old_al > upper_nibble_check or old_cf:
            self._state.SetAL((self._state.GetAL() - 0x60) & 0xff)
            self._state.SetFlagC(True)

        self._state.SetZSPFlags(self._state.GetAL())

        return 4

    def Op_AAA(self, opcode: int) -> int:  # 0x37
        if (self._state.GetAL() & 0x0f) > 9 or self._state.GetFlagA():
            self._state.SetAL((self._state.GetAL() + 6) & 0xff)
            self._state.SetAH((self._state.GetAH() + 1) & 0xff)

            self._state.SetFlagA(True)
            self._state.SetFlagC(True)
        else:
            self._state.SetFlagA(False)
            self._state.SetFlagC(False)

        self._state._al &= 0x0f

        return 8

    def Op_AAS(self, opcode: int) -> int:  # 0x3f
        if (self._state.GetAL() & 0x0f) > 9 or self._state.GetFlagA():
            self._state.SetAL((self._state.GetAL() - 6) & 0xff)
            self._state.SetAH((self._state.GetAH() - 1) & 0xff)

            self._state.SetFlagA(True)
            self._state.SetFlagC(True)
        else:
            self._state.SetFlagA(False)
            self._state.SetFlagC(False)

        self._state._al &= 0x0f

        return 8

    def Op_JMP_np(self, opcode: int) -> int:  # 0xe9
        # JMP np
        offset = self.GetPcWord()
        self._state._ip = (self._state._ip + offset) & 0xffff
        return 15

    def Op_CALL_far(self, opcode: int) -> int:  # 0x9a
        # CALL far ptr
        temp_ip = self.GetPcWord()
        temp_cs = self.GetPcWord()

        self.push(self._state._cs)
        self.push(self._state._ip)

        self._state._ip = temp_ip
        self._state._cs = temp_cs

        return 37

    def Op_CALL(self, opcode: int) -> int:  # 0xe8
        # CALL
        a = self.GetPcWord()
        self.push(self._state._ip)
        self._state._ip = (a + self._state._ip) & 0xffff

        return 16

    def Op_JMP_far(self, opcode: int) -> int:  # 0xea
        # JMP far ptr
        temp_ip = self.GetPcWord()
        temp_cs = self.GetPcWord()

        self._state._ip = temp_ip
        self._state._cs = temp_cs

        return 15

    def Op_JMP(self, opcode: int) -> int:  # 0xeb
        # JMP
        to = self.GetPcByte()
        self._state._ip = (self._state._ip + self.ToSigned8(to)) & 0xffff
        return 15

    def Op_HLT(self, opcode: int) -> int:  # 0xf4
        # HLT
        self._state._in_hlt = True
        return 2

    def Op_CMC(self, opcode: int) -> int:  # 0xf5
        # CMC
        self._state.SetFlagC(not self._state.GetFlagC())
        return 2

    def Op_CLC(self, opcode: int) -> int:  # 0xf8
        # CLC
        self._state.SetFlagC(False)
        return 2

    def Op_STC(self, opcode: int) -> int:  # 0xf9
        # STC
        self._state.SetFlagC(True)
        return 2

    def Op_CLI(self, opcode: int) -> int:  # 0xfa
        # CLI
        self._state.SetFlagI(False) # IF
        return 2

    def Op_STI(self, opcode: int) -> int:  # 0xfb
        # STI
        self._state.SetFlagI(True) # IF
        self._state._inhibit_interrupts = True
        return 2

    def Op_CLD(self, opcode: int) -> int:  # 0xfc
        # CLD
        self._state.SetFlagD(False)
        return 2

    def Op_STD(self, opcode: int) -> int:  # 0xfd
        # STD
        self._state.SetFlagD(True)
        return 2

    def Op_CBW(self, opcode: int) -> int:  # 0x98
        # CBW
        new_value = self._state.GetAL()
        if (self._state.GetAL() & 128) == 128:
            new_value |= 0xff00
        self._state.SetAX(new_value)

        return 2

    def Op_CWD(self, opcode: int) -> int:  # 0x99
        # CWD
        if (self._state.GetAH() & 128) == 128:
            self._state.SetDX(0xffff)
        else:
            self._state.SetDX(0)

        return 5

    def Op_LODSB(self, opcode: int) -> int:  # 0xac
        if self.PrefixMustRun():
            # LODSB
            self._state.SetAL(self.ReadMemByte(self._state._segment_override if self._state._segment_override_set else self._state._ds, self._state._si))
            self._state._si += -1 if self._state.GetFlagD() else 1
            self._state._si &= 0xffff

            return 5

        return 0  # TODO

    def Op_LODSW(self, opcode: int) -> int:  # 0xad
        if self.PrefixMustRun():
            # LODSW
            self._state.SetAX(self.ReadMemWord(self._state._segment_override if self._state._segment_override_set else self._state._ds, self._state._si))
            self._state._si += -2 if self._state.GetFlagD() else 2
            self._state._si &= 0xffff

            return 5

        return 0  # TODO

    def Op_LEA(self, opcode: int) -> int:  # 0x8d
        # LEA
        o1 = self.GetPcByte()
        mod = o1 >> 6
        reg = (o1 >> 3) & 7
        rm = o1 & 7

        (val, a_valid, seg, addr, get_cycles) = self.GetRegisterMem(rm, mod, True)
        self.PutRegister(reg, True, addr)

        return get_cycles + 3

    def Op_SAHF(self, opcode: int) -> int:  # 0x9e
        # SAHF
        keep = self._state._flags & 0b1111111100101010
        add = self._state.GetAH() & 0b11010101

        self._state._flags = keep | add
        self._state.FixFlags()

        return 4

    def Op_LAHF(self, opcode: int) -> int:  # 0x9f
        # LAHF
        self._state.SetAH(self._state._flags & 0xff)
        return 2

    def Op_SCASB(self, opcode: int) -> int:  # 0xae
        if self.PrefixMustRun():
            # SCASB
            v = self.ReadMemByte(self._state._es, self._state._di)
            result = self._state.GetAL() - v
            self.SetAddSubFlags(False, self._state.GetAL(), v, result, True, False)
            self._state._di += -1 if self._state.GetFlagD() else 1
            self._state._di &= 0xffff

            return 15

        return 0

    def Op_SCASW(self, opcode: int) -> int:  # 0xaf
        if self.PrefixMustRun():
            # SCASW
            ax = self._state.GetAX()
            v = self.ReadMemWord(self._state._es, self._state._di)
            result = ax - v
            self.SetAddSubFlags(True, ax, v, result, True, False)
            self._state._di += -2 if self._state.GetFlagD() else 2
            self._state._di &= 0xffff

            return 15

        return 0

    def Op_AAM(self, opcode: int) -> int:  # 0xd4
        # AAM
        b2 = self.GetPcByte()

        if b2 != 0:
            self._state.SetAH(self._state.GetAL() // b2)
            self._state._al %= b2

            self._state.SetZSPFlags(self._state.GetAL())
        else:
            self._state.SetZSPFlags(0)

            self._state.SetFlagO(False)
            self._state.SetFlagA(False)
            self._state.SetFlagC(False)

            self.InvokeInterrupt(self._state._ip, 0x00, False)

        return 83

    def Op_AAD(self, opcode: int) -> int:  # 0xd5
        # AAD
        b2 = self.GetPcByte()

        self._state.SetAL((self._state.GetAL() + self._state.GetAH() * b2) & 0xff)
        self._state.SetAH(0)
        self._state.SetZSPFlags(self._state.GetAL())

        return 60

    def Op_SALC(self, opcode: int) -> int:  # 0xd6
        # SALC
        if self._state.GetFlagC():
            self._state.SetAL(0xff)
        else:
            self._state.SetAL(0x00)

        return 2  # TODO
