from typing import List, Tuple
import abc

class Device(abc.ABC):
    def __init__(self):
        self._pic: i8259 = None
        self._b = None  # cannot ': bus.Bus' because of circular dependencies
        self._next_interrupt: List[int] = []
        self._clock = 0

    @abc.abstractmethod
    def GetName(self) -> str:
        pass

    def GetState(self) -> List[str]:
        return []

    @abc.abstractmethod
    def RegisterDevice(self, mappings: dict):
        pass

    @abc.abstractmethod
    def IO_Write(self, port: int, value: int):
        pass

    @abc.abstractmethod
    def IO_Read(self, port: int) -> int:
        pass

    def GetWaitStateCycles(self) -> int:
        return 0

    @abc.abstractmethod
    def GetAddressList(self) -> list[Tuple[int, int]]:
        pass

    @abc.abstractmethod
    def WriteByte(self, offset: int, value: int):
        pass

    @abc.abstractmethod
    def ReadByte(self, offset: int) -> int:
        pass

    @abc.abstractmethod
    def Ticks(self) -> bool:
        pass

    def Tick(self, cycles: int, clock: int) -> bool:
        self._clock = clock
        return False

    @abc.abstractmethod
    def GetIRQNumber(self) -> int:
        pass

    def SetDma(self, dma_instance):
        pass

    def ScheduleInterrupt(self, cycles_delay: int):
        self._next_interrupt.append(cycles_delay)

    def CheckScheduledInterrupt(self, cycles: int) -> bool:
        if len(self._next_interrupt) > 0:
            self._next_interrupt[0] -= cycles
            if self._next_interrupt[0] <= 0:
                del self._next_interrupt[0]
                return True
        return False

    def SetPic(self, pic_instance):
        self._pic = pic_instance

    def SetBus(self, bus_instance):
        self._b = bus_instance
