from typing import List, Tuple
import device
import memory
import rom

class Bus:
    class CacheEntry:
        def __init__(self):
            self._start_addr: int = 0
            self._end_addr: int = 0
            self._wait_states: int = 0
            self._device: device.Device = None

    def __init__(self, size: int, devices: List[device], roms: List[rom.Rom]):
        self._size = size
        self._m = memory.Memory(size)

        self._devices = devices
        self._roms = roms

        self._cache: List[Bus.CacheEntry] = None
        self.RecreateCache()

    def GetState(self) -> List[str]:
        out = []
        for entry in self._cache:
            out.append(f'{entry.device.GetName()}, start address: {entry.start_addr:06x}, end address: {entry.end_addr:06x}, wait states: {entry.wait_states}')
        return out

    def _AddEntries(self, devices: List[device]):
        for device in devices:
            segments = device.GetAddressList()
            for segment in segments:
                entry = Bus.CacheEntry()
                entry.start_addr = segment[0]
                entry.end_addr = entry.start_addr + segment[1]
                entry.wait_states = device.GetWaitStateCycles()  # different per segment?
                entry.device = device
                self._cache.append(entry)

    def RecreateCache(self):
        self._cache = []
        self._AddEntries(self._devices)

        for rom in self._roms:
            self._AddEntries((rom,))

        # last! because it is a full 1 MB
        self._AddEntries((self._m,))

    def ClearMemory():
        self._m = Memory(self._size)
        self.RecreateCache()

    def ReadByte(self, address: int) -> Tuple[int, int]:
        for entry in self._cache:
            if address >= entry.start_addr and address < entry.end_addr:
                return (entry.device.ReadByte(address), entry.wait_states)

        return (0xff, 1)  # TODO

    def WriteByte(self, address: int, v: int) -> int:
        assert v >= 0 and v <= 255
        for entry in self._cache:
            if address >= entry.start_addr and address < entry.end_addr:
                entry.device.WriteByte(address, v)
                return entry.wait_states

        return 1  #  TODO
