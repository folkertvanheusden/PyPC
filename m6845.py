from typing import List

class M6845:
    def __init__(self):
        self._registers: List = [ 0x00 ] * 18

    def Write(self, reg: int, value: int):
        if reg < 18:
            self._registers[reg] = value

    def Read(self, reg: int) -> int:
        if reg < 18:
           return self._registers[reg]

        return 0xee
