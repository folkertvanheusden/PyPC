# TIMER

from typing import override, List, Tuple
import device
import i8237
import random


class i8253(device.Device):
    class Timer:
        counter_cur: int = 0
        counter_prv: int = 0
        counter_ini: int = 0
        mode: int = 0
        latch_type: int = 0
        latch_n: int = 0
        latch_n_cur: int = 0
        is_running: int = 0
        is_pending: int = 0
        is_bcd: int = 0

    def __init__(self):
        self._timers = [ None ] * 3
        self._irq_nr = 0
        self._i8237 = None
        self._clock = 0

        for i in range(3):
            self._timers[i] = i8253.Timer()

    @override
    def GetStat(self) -> List[str]:
        out_ = []
        for i in range(3):
            t = self._timers[i]
            out_.append(f'Timer {i}: counter cur/prv/ini {t.counter_cur}/{t.counter_prv}/{t.counter_ini}, mode {t.mode} ({_mode_names[t.mode]}) running {t.is_running} pending {t.is_pending}, BCD: {t.is_bcd}')
        return out_

    @override
    def GetIRQNumber(self):
        return self._irq_nr

    @override
    def GetName(self):
        return 'i8253'

    @override
    def RegisterDevice(self, mappings: dict):
        mappings[0x0040] = self
        mappings[0x0041] = self
        mappings[0x0042] = self
        mappings[0x0043] = self

    @override
    def IO_Read(self, port: int) -> int:
        if port == 0x0040:
            return self.GetCounter(0)

        if port == 0x0041:
            return self.GetCounter(1)

        if port == 0x0042:
            return self.GetCounter(2)

        return 0xaa

    @override
    def IO_Write(self, port: int, value: int) -> bool:
        if port == 0x0040:
            self.LatchCounter(0, value)
        elif port == 0x0041:
            self.LatchCounter(1, value)
        elif port == 0x0042:
            self.LatchCounter(2, value)
        elif port == 0x0043:
            self.Command(value)
        else:
            print(f'error {port:04x}')

        return self._timers[0].is_pending or self._timers[1].is_pending or self._timers[2].is_pending

    @override
    def GetAddressList(self) -> list[Tuple[int, int]]:
        return [ ]

    @override
    def WriteByte(self, offset: int, value: int):
        pass

    @override
    def ReadByte(self, offset: int) -> int:
        return 0xee

    @override
    def SetDma(self, dma_instance: i8237.i8237):
        self._i8237 = dma_instance

    def LatchCounter(self, nr: int, v: int):
        if self._timers[nr].latch_n_cur > 0:
            if self._timers[nr].latch_type == 1:
                self._timers[nr].counter_ini &= 0xff00
                self._timers[nr].counter_ini |= v
            elif self._timers[nr].latch_type == 2:
                self._timers[nr].counter_ini &= 0x00ff
                self._timers[nr].counter_ini |= (ushort)(v << 8)
            elif self._timers[nr].latch_type == 3:
                if self._timers[nr].latch_n_cur == 2:
                    self._timers[nr].counter_ini &= 0xff00
                    self._timers[nr].counter_ini |= v
                else:
                    self._timers[nr].counter_ini &= 0x00ff
                    self._timers[nr].counter_ini |= v << 8

            self._timers[nr].latch_n_cur -= 1
            self._timers[nr].latch_n_cur &= 0xffff

            if self._timers[nr].latch_n_cur == 0:
                self._timers[nr].latch_n_cur = self._timers[nr].latch_n  # restart setup
                self._timers[nr].counter_cur = self._timers[nr].counter_ini
                self._timers[nr].is_running = True
                self._timers[nr].is_pending = False

    # TODO WHY?!?!
    def AddNoiseToLSB(self, nr: int) -> int:
        current_prv = self._timers[nr].counter_prv

        self._timers[nr].counter_prv = self._timers[nr].counter_cur

        if abs(self._timers[nr].counter_cur - current_prv) >= 2:
            return (self._timers[nr].counter_cur ^ 1 if random.choice([True, False]) else self._timers[nr].counter_cur) & 0xff

        return self._timers[nr].counter_cur & 0xff

    def GetCounter(self, nr: int) -> int:
        rc = 0

        if self._timers[nr].latch_type == 1:
            rc = self.AddNoiseToLSB(nr)
        elif self._timers[nr].latch_type == 2:
            rc = (self._timers[nr].counter_cur >> 8) & 0xff
        elif self._timers[nr].latch_type == 3:
            if self._timers[nr].latch_n_cur == 2:
                rc = self.AddNoiseToLSB(nr)
            else:
                rc = (self._timers[nr].counter_cur >> 8) & 0xff

        self._timers[nr].latch_n_cur -= 1
        self._timers[nr].latch_n_cur &= 0xffff

        if self._timers[nr].latch_n_cur == 0:
            self._timers[nr].latch_n_cur = self._timers[nr].latch_n

        return rc

    def Command(self, v: int):
        nr    = v >> 6
        latch = (v >> 4) & 3
        mode  = (v >> 1) & 7
        type  = v & 1

        if latch != 0:
            self._timers[nr].mode = mode
            self._timers[nr].latch_type = latch
            self._timers[nr].is_running = False
            self._timers[nr].is_bcd = type == 1

            self._timers[nr].counter_ini = 0

            if self._timers[nr].latch_type == 1 or self._timers[nr].latch_type == 2:
                self._timers[nr].latch_n = 1
            elif self._timers[nr].latch_type == 3:
                self._timers[nr].latch_n = 2

            self._timers[nr].latch_n_cur = self._timers[nr].latch_n

    @override
    def Ticks(self) -> bool:
        return True

    @override
    def Tick(self, ticks: int, ignored):
        self._clock += ticks
        if self._clock < 4:
            return False

        interrupt = False

        n_to_subtract = self._clock // 4

        for i in range(3):
            if self._timers[i].is_running == False:
                continue

            self._timers[i].counter_cur -= n_to_subtract

            n_interrupts = 0
            if self._timers[i].counter_cur < 0:
                n_interrupts = -self._timers[i].counter_cur // 0x10000

            if n_interrupts > 0:
                # timer 1 is RAM refresh counter
                if i == 1:
                    for k in range(n_interrupts):
                        self._i8237.TickChannel0()

                if self._timers[i].mode != 1:
                    self._timers[i].counter_cur = self._timers[i].counter_ini - (-self._timers[i].counter_cur % (0x10000 if self._timers[i].counter_ini == 0 else self._timers[i].counter_ini))
                else:
                    self._timers[i].counter_cur &= 0xffff

                if i == 0:
                    self._timers[i].is_pending = True
                    interrupt = True

        self._clock -= n_to_subtract * 4

        if interrupt:
            self._pic.RequestInterruptPIC(self._irq_nr)  # Timers are on IRQ0

        return interrupt
