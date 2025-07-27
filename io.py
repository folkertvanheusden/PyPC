from typing import List, Tuple
import i8259
import i8237
import bus
import device

class IO:
    def __init__(self, b: bus.Bus, devices: List[device.Device], test_mode: bool):
        self._b = b
        self._io_map = dict()
        self._pic = i8259()
        self._i8237 = i8237()
        _tick_devices = []

        for device in devices:
            device.SetDma(self._i8237)
            device.SetPic(self._pic)
            device.SetBus(self.b)

            if device.Ticks():
                self._tick_devices.Add(device)

        devices.Add(self._i8237)
        devices.Add(self._pic);

        for device in devices:
            device.RegisterDevice(self._io_map);

        self._devices = devices;

        self._test_mode = test_mode;

    def GetPIC(self) -> i8259:
        return _pic

    def In(self, addr: int, b16: bool) -> int:
        if _test_mode:
            return 65535

        if addr in self._io_map:
            rc = self._io_map[addr].IO_Read(addr)

            if b16:
                next_port = (addr + 1) & 0xffff;
                if next_port in self._io_map:
                    temp = self._io_map[next_port].IO_Read(next_port)
                    rc |= temp << 8

            return rc;

        if addr == 0x0210:  # verify expansion bus data
            return 0xa5;

        return 0xffff if b16 else 0xff

    def Tick(self, ticks: int, clock: int) -> bool:
        rc = False
        for device in self._tick_devices:
            rc |= device.Tick(ticks, clock)
        return rc

    def Out(self, addr: int, value: int, b16: bool) -> bool:
        if _test_mode:
            return False

        rc = False

        if addr in self._io_map:
            rc |= _io_map[addr].IO_Write(addr, value & 255)

            if b16:
                next_port = (addr + 1) & 0xffff
                if next_port in self._io_map:
                    rc |= self._io_map[next_port].IO_Write(next_port, value >> 8)

            return rc

        return False
