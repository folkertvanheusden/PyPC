from typing import override, List, Tuple
import device


class XTIDE(device.Device):
    def __init__(self, disk_filenames: List[str]):
        self._disk_filenames = disk_filenames
        self._status_register = 0
        self._error_register = 0
        self._drv = 0
        self._sector_buffer = bytearray(512)
        self._sector_buffer_offset = 0
        self._target_lba = 0
        self._target_drive = 255
        self._cylinder_count = 614
        self._head_count = 4
        self._sectors_per_track = 17
        self._registers = [ 0 ] * 8

    def PushSectorBufferWord(self, v: int):
        self._sector_buffer[self._sector_buffer_offset] = v & 255
        self._sector_buffer_offset += 1
        self._sector_buffer[self._sector_buffer_offset] = v >> 8
        self._sector_buffer_offset += 1

    def PushSectorBufferString(self, what: str, length: int):
        for i in range(0, length, 2):
            word = 0
            if i < len(what):
                word |= ord(what[i]) << 8
            if i + 1 < len(what):
                word |= ord(what[i + 1])
            self.PushSectorBufferWord(word)

    def CMDIdentifyDrive(self):
        drive_head = self._registers[6]
        drive = 1 if (drive_head & 16) != 0 else 0
        if drive == 1 and len(self._disk_filenames) == 1:
            self._error_register |= 4  # ABRT
            self.SetERR()
            return

        self._sector_buffer = bytearray(512)
        self._sector_buffer_offset = 0

        self.PushSectorBufferWord(64 + 32)
        self.PushSectorBufferWord(self._cylinder_count)
        self.PushSectorBufferWord(0)  # reserved, 2
        self.PushSectorBufferWord(self._head_count)
        self.PushSectorBufferWord(512 * self._sectors_per_track)
        self.PushSectorBufferWord(512)  # bytes per sector
        self.PushSectorBufferWord(self._sectors_per_track)
        self.PushSectorBufferWord(0)  # reserved, 7
        self.PushSectorBufferWord(0)  # reserved
        self.PushSectorBufferWord(0)  # reserved, 9
        self.PushSectorBufferString(f"{hash(self._disk_filenames[drive])}", 20) # serial number, ascii
        self.PushSectorBufferWord(0)  # buffer type
        self.PushSectorBufferWord(0)  # buffer size
        self.PushSectorBufferWord(0)  # ECC byte count
        for i in range(4):
            self.PushSectorBufferWord(0)  # firmware revision, ascii
        self.PushSectorBufferString("PyPC", 40) # model number, ascii
        self.PushSectorBufferWord(1)  # Maximum number of sectors that can be transferred per interrupt on read and write multiple commands
        self.PushSectorBufferWord(0)  # no doubleword transfers
        self.PushSectorBufferWord(1024)  # LBA supported
        self.PushSectorBufferWord(0)  # reserved
        self.PushSectorBufferWord(0)  # PIO data transfer cycle timing mode
        self.PushSectorBufferWord(0)  # DMA data transfer cycle timing mode
        self.PushSectorBufferWord(0)  # the fields reported in words 54-58 may be valid
        self.PushSectorBufferWord(self._cylinder_count)
        self.PushSectorBufferWord(self._head_count)
        self.PushSectorBufferWord(self._sectors_per_track)
        total_sector_count = self._cylinder_count * self._head_count * self._sectors_per_track
        self.PushSectorBufferWord(total_sector_count)  # capacity in sectors
        self.PushSectorBufferWord(total_sector_count >> 16)  # ^
        self.PushSectorBufferWord(1)  #  Current setting for number of sectors that can be transferred per interrupt on R/W multiple commands
        self.PushSectorBufferWord(total_sector_count)  # Total number of user addressable sectors (LBA mode only) 
        self.PushSectorBufferWord(total_sector_count >> 16)  # ^
        self.PushSectorBufferWord(0)  # dma related
        self.PushSectorBufferWord(0)  # dma related
        for i in range(256 - 64):
            self.PushSectorBufferWord(0)  # reserved
        assert self._sector_buffer_offset == 512
        self._sector_buffer_offset = 0

    def CMDSeek(self):
        self.SetDSC()

    def CMDReadMultiple(self):
        sector_count = self._registers[2]
        sector_number = self._registers[3]
        cylinder = self._registers[4] | (self._registers[5] << 8)
        drive_head = self._registers[6]
        drive = 1 if (drive_head & 16) != 0 else 0
        if drive == 1 and len(_disk_filenames) == 1:
            self._error_register |= 4  # ABRT
            self.SetERR()
            return

        head = drive_head & 15
        if sector_count == 0:
            sector_count = 256
        lba = (cylinder * self._head_count + head) * self._sectors_per_track + sector_number - 1
        offset = lba * 512

        self._sector_buffer = bytearray(sector_count * 512)
        self._sector_buffer_offset = 0

        fh = open(self._disk_filenames[drive], 'rb')
        for nr in range(sector_count):
            lba = (cylinder * self._head_count + head) * self._sectors_per_track + sector_number - 1
            offset = lba * 512

            fh.seek(offset)
            self._sector_buffer[512 * nr: 512 * nr + 512] = fh.read(512)

            sector_number += 1
            if sector_number > self._sectors_per_track:  # > because starting at 1!
                sector_number = 1
                head += 1
                if head == self._head_count:
                    head = 0
                    cylinder += 1

            self._registers[3] = sector_number
            self._registers[4] = cylinder & 255
            self._registers[5] = cylinder >> 8
            self._registers[6] &= 0xf0
            self._registers[6] |= head
        fh.close()

        self.SetDRDY()
        self.SetDRQ()

    def CMDWriteMultiple(self):
        sector_count = self._registers[2]
        sector_number = self._registers[3]
        cylinder = self._registers[4] | (self._registers[5] << 8)
        drive_head = self._registers[6]
        drive = 1 if (drive_head & 16) != 0 else 0
        if drive == 1 and len(_disk_filenames) == 1:
            self._error_register |= 4  # ABRT
            self.SetERR()
            return

        head = drive_head & 15
        if sector_count == 0:
            sector_count = 256
        lba = (cylinder * self._head_count + head) * self._sectors_per_track + sector_number - 1
        offset = lba * 512

        self._sector_buffer = bytearray(sector_count * 512)
        self._sector_buffer_offset = 0
        self._target_lba = lba
        self._target_drive = drive

        self.SetDRDY()
        self.SetDRQ()

    @override
    def GetIRQNumber(self) -> int:
        return -1

    @override
    def SetPic(self, pic_instance):
        pass

    @override
    def GetName(self) -> str:
        return "XT-IDE"

    @override
    def RegisterDevice(self, mappings: dict):
        for port in range(0x0300, 0x0310):
            mappings[port] = self

    @override
    def GetAddressList(self) -> list[Tuple[int, int]]:
        return [ ]

    @override
    def WriteByte(self, offset: int, value: int):
        pass

    @override
    def ReadByte(self, offset: int) -> int:
        return 0xee

    def SetBSY(self):
        self._status_register |= 128

    def SetDRDY(self):
        self._status_register |= 64

    def SetDRQ(self):
        self._status_register |= 8

    def SetDSC(self):
        self._status_register |= 16

    def SetERR(self):
        self._status_register |= 1

    def ResetStatusRegister(self):
        self._status_register = 0
        self.SetDRDY()

    @override
    def IO_Read(self, port: int) -> int:
        register = (port - 0x300) // 2

        rc = 0xee

        if port == 0x300:  # Data register
            if self._sector_buffer_offset < len(self._sector_buffer):
                rc = self._sector_buffer[self._sector_buffer_offset]
                self._sector_buffer_offset += 1

        elif port == 0x302:  # error register
            rc = self._error_register
            self._error_register = 0

        elif port == 0x30e:  # status register
            if self._sector_buffer != None and self._sector_buffer_offset < len(self._sector_buffer):
                self.SetDRQ()
            rc = self._status_register
            self.ResetStatusRegister()

        else:
            rc = self._registers[register]

        return rc

    def StoreSectorBuffer(self):
        fh = open(self._disk_filenames[self._target_drive], 'a+b')
        fh.seek(self._target_lba * 512)
        fh.write(self._sector_buffer)
        fh.close()

    @override
    def IO_Write(self, port: int, value: int) -> bool:
        register = (port - 0x300) // 2
        self._registers[register] = value

        if port == 0x300:  # data register
            if self._sector_buffer_offset < len(self._sector_buffer):
                self._sector_buffer[self._sector_buffer_offset] = value  # FIXME
                self._sector_buffer_offset += 1

            if self._sector_buffer_offset == len(self._sector_buffer):
                if self._target_drive != 255:
                    self.StoreSectorBuffer()
                    self._target_drive = 255

        elif port == 0x30c:  # drive/head register
            self._drv = 1 if (value & 16) != 0 else 0

        elif port == 0x30e:  # command register
            if value == 0xef:  # set features
                # send aborted command error
                self._error_register |= 4  # ABRT
                self.SetERR()

            elif value == 0xec:  # identify drive
                self.CMDIdentifyDrive()

            elif value == 0x91:  # initialize drive parameters
                # send aborted command error
                self._error_register |= 4  # ABRT
                self.SetERR()

            elif (value & 0xf0) == 0x70:  # seek
                self.CMDSeek()

            elif value == 0xc6:  # set multiple mode
                pass

            elif value == 0xc4:  # read multiple
                self.CMDReadMultiple()

            elif value == 0xc5:  # write multiple
                self.CMDWriteMultiple()

        return False

    @override
    def Ticks(self) -> bool:
        return False
