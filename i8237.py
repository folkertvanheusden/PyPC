from typing import override, List, Tuple
import device

# DMA
class i8237(device.Device):
    class FlipFlop:
        def __init__(self):
            self._state = False

        def get_state(self) -> bool:
            rc = self._state
            self._state = not self._state
            return rc

        def reset(self):
            self._state = False

    class b16buffer:
        def __init__(self, f):
            self._value: int = 0
            self._f = f

        def Put(self, v: int):
            assert v >= 0 and v <= 255
            low_high = self._f.get_state()

            if low_high:
                self._value &= 0xff
                self._value |= v << 8
            else:
                self._value &= 0xff00
                self._value |= v

        def GetValue(self) -> int:
            return self._value

        def SetValue(self, v: int):
            self._value = v

        def Get(self) -> int:
            low_high = self._f.get_state()

            if low_high:
                return self._value >> 8

            return self._value & 0xff

    def __init__(self, b):
        self._channel_page: List[int] = [ 0 ] * 4
        self._channel_address_register: List[b16buffer] = [ None ] * 4
        self._channel_word_count: List[b16buffer] = [ None ] * 4
        self._command: int = 0
        self._channel_mask: List[bool] = [ False ] * 4
        self._reached_tc: List[bool] = [ False ] * 4
        self._channel_mode: List[int] = [ 0 ] * 4
        self._ff = self.FlipFlop()
        self._dma_enabled = True

        for i in range(4):
            self._channel_address_register[i] = self.b16buffer(self._ff)
            self._channel_word_count[i] = self.b16buffer(self._ff)
            self._reached_tc[i] = False

        self._b = b

    @override
    def GetIRQNumber(self) -> int:
        return -1

    @override
    def GetName(self) -> str:
        return "i8237"

    @override
    def RegisterDevice(self, mappings: dict):
        for i in range(0x10):
            mappings[i] = self
        mappings[0x81] = self
        mappings[0x82] = self
        mappings[0x83] = self
        mappings[0x87] = self

    def TickChannel0(self, n):
        # RAM refresh
        self._channel_address_register[0].SetValue((self._channel_address_register[0].GetValue() + n) & 0xffff)

        new_count = self._channel_word_count[0].GetValue() - n
        if new_count < 0:
            self._reached_tc[0] = True
        self._channel_word_count[0].SetValue(new_count & 0xffff)

    @override
    def IO_Read(self, addr: int) -> int:
        v = 0
        if addr in (0, 2, 4, 6):
            v = self._channel_address_register[addr // 2].Get()
        elif addr in (1, 3, 5, 7):
            v = self._channel_word_count[addr // 2].Get()
        elif addr == 8:  # status register
            for i in range(4):
                if self._reached_tc[i]:
                    self._reached_tc[i] = False
                    v |= 1 << i
        return v

    def reset_masks(self, state: bool):
        for i in range(4):
            self._channel_mask[i] = state

    @override
    def IO_Write(self, addr: int, value: int) -> bool:
        if addr in (0, 2, 4, 6):
            self._channel_address_register[addr // 2].Put(value)
        elif addr in (1, 3, 5, 7):
            self._channel_word_count[addr // 2].Put(value)
            self._reached_tc[addr // 2] = False
        elif addr == 8:
            self._command = value
            self._dma_enabled = (self._command & 4) == 0
        elif addr == 0x0a:  # mask
            self._channel_mask[value & 3] = (value & 4) == 4  # dreq enable/disable
        elif addr == 0x0b:  # mode register
            self._channel_mode[value & 3] = value
            for i in range(4):
                self._reached_tc[i] = False
        elif addr == 0x0c:  # reset flipflop
            self._ff.reset()
        elif addr == 0x0d:  # master reset
            self.reset_masks(True)
            self._ff.reset()
            for i in range(4):
                self._reached_tc[i] = False
        elif addr == 0x0e:  # reset masks
            self.reset_masks(False)
        elif addr == 0x0f:  # multiple mask
            for i in range(4):
                self._channel_mask[i] = (value & (1 << i)) != 0
        elif addr == 0x87:
            self._channel_page[0] = value & 0x0f
        elif addr == 0x83:
            self._channel_page[1] = value & 0x0f
        elif addr == 0x81:
            self._channel_page[2] = value & 0x0f
        elif addr == 0x82:
            self._channel_page[3] = value & 0x0f

        return False

    def ReceiveFromChannel(self, channel: int) -> int:
        if self._dma_enabled == False:
            return -1

        if self._channel_mask[channel]:
            return -1

        if self._reached_tc[channel]:
            return -1

        addr = self._channel_address_register[channel].GetValue()
        full_addr = (self._channel_page[channel] << 16) | addr
        addr += 1
        self._channel_address_register[channel].SetValue(addr & 0xffff)

        rc = self._b.ReadByte(full_addr)[0]

        count = self._channel_word_count[channel].GetValue()
        count -= 1
        if count == -1:
            self._reached_tc[channel] = True
        _channel_word_count[channel].SetValue(count & 0xffff)

        return rc

    def IsChannelTC(self, channel: int) -> bool:
        return self._reached_tc[channel]

    # used by devices (floppy etc) to send data to memory
    def SendToChannel(self, channel: int, value: int) -> bool:
        if self._dma_enabled == False:
            return False

        if self._channel_mask[channel]:
            return False

        if self._reached_tc[channel]:
            return False

        addr = self._channel_address_register[channel].GetValue()
        full_addr = (_channel_page[channel] << 16) | addr
        addr += 1
        self._channel_address_register[channel].SetValue(addr & 0xffff)

        self._b.WriteByte(full_addr, value)

        count = _channel_word_count[channel].GetValue()
        count -= 1
        if count == -1:
            self._reached_tc[channel] = True

        _channel_word_count[channel].SetValue(count & 0xffff)

        return True

    @override
    def GetAddressList(self):
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
