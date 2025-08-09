import select
import socket
import threading


class VNCServer:
    class VNCServerThreadParameters:
        def __init__(self):
            self.vs = None  # VNCServer
            self.port = 0

    class VNCSession:
        def __init__(self):
            self.stream_lock = threading.Lock()
            self.stream = -1

    def __init__(self, display, kb, port, compatible):
        self._thread = None
        self._display = display
        self._kb = kb  # Keyboard
        self._listen_port = port
        self._compatible = compatible
        self._compatible_width = 720
        self._compatible_height = 400

        self._key_map = dict()
        self._key_map[0xff1b] = ( 0x01, )  # escape
        self._key_map[0xff0d] = ( 0x1c, )  # enter
        self._key_map[0xff08] = ( 0x0e, )  # backspace
        self._key_map[0xff09] = ( 0x0f, )  # tab
        self._key_map[0xffe1] = ( 0x2a, )  # left shift
        self._key_map[0xffe3] = ( 0x1d, )  # left control
        self._key_map[0xffe9] = ( 0x38, )  # left alt
        self._key_map[0xffbe] = ( 0x3b, )  # F1
        self._key_map[0xffbf] = ( 0x3c, )  # F2
        self._key_map[0xffc0] = ( 0x3d, )  # F3
        self._key_map[0xffc1] = ( 0x3e, )  # F4
        self._key_map[0xffc2] = ( 0x3f, )  # F5
        self._key_map[0xffc3] = ( 0x40, )  # F6
        self._key_map[0xffc4] = ( 0x41, )  # F7
        self._key_map[0xffc5] = ( 0x42, )  # F8
        self._key_map[0xffc6] = ( 0x43, )  # F9
        self._key_map[0xffc7] = ( 0x44, )  # F10
        self._key_map[0x31] = ( 0x02, )  # 1
        self._key_map[0x32] = ( 0x03, )
        self._key_map[0x33] = ( 0x04, )
        self._key_map[0x34] = ( 0x05, )
        self._key_map[0x35] = ( 0x06, )
        self._key_map[0x36] = ( 0x07, )
        self._key_map[0x37] = ( 0x08, )
        self._key_map[0x38] = ( 0x09, )
        self._key_map[0x39] = ( 0x0a, )  # 9
        self._key_map[0x30] = ( 0x0b, )  # 0
        self._key_map[0x41] = ( 0x1e, )  # A
        self._key_map[0x42] = ( 0x30, )
        self._key_map[0x43] = ( 0x2e, )
        self._key_map[0x44] = ( 0x20, )
        self._key_map[0x45] = ( 0x12, )
        self._key_map[0x46] = ( 0x21, )
        self._key_map[0x47] = ( 0x22, )
        self._key_map[0x48] = ( 0x23, )
        self._key_map[0x49] = ( 0x17, )
        self._key_map[0x4a] = ( 0x24, )
        self._key_map[0x4b] = ( 0x25, )
        self._key_map[0x4c] = ( 0x26, )
        self._key_map[0x4d] = ( 0x32, )
        self._key_map[0x4e] = ( 0x31, )
        self._key_map[0x4f] = ( 0x18, )
        self._key_map[0x50] = ( 0x19, )
        self._key_map[0x51] = ( 0x10, )
        self._key_map[0x52] = ( 0x13, )
        self._key_map[0x53] = ( 0x1f, )
        self._key_map[0x54] = ( 0x14, )
        self._key_map[0x55] = ( 0x16, )
        self._key_map[0x56] = ( 0x2f, )
        self._key_map[0x57] = ( 0x11, )
        self._key_map[0x58] = ( 0x2d, )
        self._key_map[0x59] = ( 0x15, )
        self._key_map[0x5a] = ( 0x2c, )  # Z
        self._key_map[0x61] = ( 0x1e, )  # a
        self._key_map[0x62] = ( 0x30, )
        self._key_map[0x63] = ( 0x2e, )
        self._key_map[0x64] = ( 0x20, )
        self._key_map[0x65] = ( 0x12, )
        self._key_map[0x66] = ( 0x21, )
        self._key_map[0x67] = ( 0x22, )
        self._key_map[0x68] = ( 0x23, )
        self._key_map[0x69] = ( 0x17, )
        self._key_map[0x6a] = ( 0x24, )
        self._key_map[0x6b] = ( 0x25, )
        self._key_map[0x6c] = ( 0x26, )
        self._key_map[0x6d] = ( 0x32, )
        self._key_map[0x6e] = ( 0x31, )
        self._key_map[0x6f] = ( 0x18, )
        self._key_map[0x70] = ( 0x19, )
        self._key_map[0x71] = ( 0x10, )
        self._key_map[0x72] = ( 0x13, )
        self._key_map[0x73] = ( 0x1f, )
        self._key_map[0x74] = ( 0x14, )
        self._key_map[0x75] = ( 0x16, )
        self._key_map[0x76] = ( 0x2f, )
        self._key_map[0x77] = ( 0x11, )
        self._key_map[0x78] = ( 0x2d, )
        self._key_map[0x79] = ( 0x15, )
        self._key_map[0x7a] = ( 0x2c, )  # z
        self._key_map[0x20] = ( 0x39, )  # space
        self._key_map[0x22] = ( 0x28, )  # "
        self._key_map[0x2c] = ( 0x33, )  # ,
        self._key_map[0x2e] = ( 0x34, )  # .
        self._key_map[0x25] = ( 0x06, )  # %
        self._key_map[0x24] = ( 0x05, )  # $
        self._key_map[0x2d] = ( 0x0c, )  # -
        self._key_map[0x5f] = ( 0x0c, )  # _
        self._key_map[0x3a] = ( 0x27, )  # :
        self._key_map[0x2f] = ( 0x35, )  # /
        self._key_map[0x3f] = ( 0x35, )  # ?
        self._key_map[0x2a] = ( 0x09, )  # *  (shift)
        self._key_map[0x26] = ( 0x08, )  # &  (shift)
        self._key_map[0x40] = ( 0x03, )  # @
        self._key_map[0x5c] = ( 0x2b, )  # \
        self._key_map[0x7c] = ( 0x2b, )  # |  (shift)
        self._key_map[0x3d] = ( 0x0d, )  # =
        self._key_map[0xff54] = ( 0x50, )  # cursor down
        self._key_map[0xff52] = ( 0x48, )  # cursor up
        self._key_map[0xff51] = ( 0x4b, )  # cursor left
        self._key_map[0xff53] = ( 0x4d, )  # cursor right
        self._key_map[0xff50] = ( 0x47, )  # home
        self._key_map[0xff57] = ( 0x4f, )  # end


        _thread = threading.Thread(target=self.VNCServerThread, args=(port, ))
        _thread.name = "vnc-server-thread"
        _thread.start()

    def PushChar(self, c, press):
        if self._kb == None:
            return

        if c in self._key_map:
            for m in self._key_map[c]:
                self._kb.PushKeyboardScancode(m if press else (m | 0x80))

    def VNCSendVersion(self, stream):
        msg = "RFB 003.008\n".encode('ascii')
        stream.send(msg)

        # wait for reply, ignoring what it is
        while True:
            buffer = int.from_bytes(stream.recv(1))
            print(f'{buffer:c}', end='')
            if buffer == ord('\n'):
                break
        print()

    def VNCSecurityHandshake(self, stream):
        list_ = (1, 1)  # 1, None
        stream.send(bytes(list_))

        # receive reply with choice, ignoring choice
        buffer = stream.recv(1)

        reply = [ 0 ] * 4
        stream.send(bytes(reply))

    def VNCClientServerInit(self, stream):
        shared = stream.recv(1)

        example = self._display.GetFrame()
        width = self._compatible_width if self._compatible else example[0]
        height = self._compatible_height if self._compatible else example[1]
        reply = [ 0 ] * 24
        reply[0] = width >> 8
        reply[1] = width & 255
        reply[2] = height >> 8
        reply[3] = height & 255
        reply[4] = 32  # bits per pixel
        reply[5] = 32  # depth
        reply[6] = 1  # big endian
        reply[7] = 1  # True color
        reply[8] = 0  # red max
        reply[9] = 255  # red max
        reply[10] = 0  # green max
        reply[11] = 255  # green max
        reply[12] = 0  # blue max
        reply[13] = 255  # blue max
        reply[14] = 16  # red shift
        reply[15] = 8  # green shift
        reply[16] = 0  # blue shift
        reply[17] = reply[18] = reply[19] = 0  # padding
        name = 'PyPC'
        name_bytes = name.encode('ascii')
        reply[20] = (len(name_bytes) >> 24) & 255
        reply[21] = (len(name_bytes) >> 16) & 255
        reply[22] = (len(name_bytes) >>  8) & 255
        reply[23] = len(name_bytes) & 255
        stream.send(bytes(reply))
        stream.send(name_bytes)

    def VNCWaitForEvent(self, session):
        try:
            poller = select.poll()
            poller.register(session.stream, select.POLLIN)
            events = poller.poll(1 / 15)  # 15 fps
            if len(events) == 0:
                return True

            type_ = int.from_bytes(session.stream.recv(1))

            if type_ == 0:  # SetPixelFormat
                temp = session.stream.recv(3 + 16)
            elif type_ == 2:  # SetEncodings
                temp = session.stream.recv(3)

                no_encodings = (temp[1] << 8) | temp[2]
                print(f'VNC: retrieve {no_encodings} encodings')
                for i in range(no_encodings):
                    encoding = session.stream.recv(4)
                    e = int.from_bytes(encoding, 'big', signed=True)
                    print(f'VNC: retrieved encoding {i}: {e}')
                    if e == -259:
                        print("VNC client supports audio")
                        session.audio_enabled = True
            elif type_ == 3:  # FramebufferUpdateRequest
                buffer = session.stream.recv(9)
                # TODO
            elif type_ == 4:  # KeyEvent
                buffer = session.stream.recv(7)
                vnc_scan_code = (buffer[3] << 24) | (buffer[4] << 16) | (buffer[5] << 8) | buffer[6]
                print(f'Key {buffer[0]} {vnc_scan_code:04x}')
                self.PushChar(vnc_scan_code, buffer[0] != 0)
            elif type_ == 5:  # PointerEvent
                buffer = session.stream.recv(5)
            elif type_ == 6:  # ClientCutText
                buffer = session.stream.recv(7)
                n_to_read = (buffer[3] << 24) | (buffer[4] << 16) | (buffer[5] << 8) | buffer[6]
                temp = session.stream.recv(n_to_read)
            else:
                print(f'VNC: Client message {type_} not understood')
                return False

            return True

        except Exception as e:
            print(f'VNCWaitForEvent exception: {e}, line number: {e.__traceback__.tb_lineno}')

        return False

    def VNCSendFrame(self, session, first):
        frame = self._display.GetFrame()

        width = self._compatible_width if self._compatible else frame[0]
        height = self._compatible_height if self._compatible else frame[1]

        if not self._compatible:
            resize = [ 0 ] * 5
            resize[0] = 15  # ResizeFrameBuffer
            resize[1] = width >> 8  # width
            resize[2] = width & 255
            resize[3] = height >> 8  # height
            resize[4] = height & 255
            with session.stream_lock:
                session.stream.send(bytes(resize))

        update = [ 0 ] * (4 + 12)
        update[0] = 0  # FrameBufferUpdate
        update[1] = 0  # padding
        update[2] = 0  # 1 rectangle
        update[3] = 1
        update[4] = 0  # x pos
        update[5] = 0
        update[6] = 0  # y pos
        update[7] = 0
        update[8] = width >> 8  # width
        update[9] = width & 255
        update[10] = height >> 8  # height
        update[11] = height & 255
        update[12] = 0
        update[13] = 0
        update[14] = 0
        update[15] = 0

        if self._compatible:
            buffer = [ 0 ] * (width * height * 4)
            use_width = min(width, frame[0])
            use_height = min(height, frame[1])
            for y in range(use_height):
                in_offset = y * frame[0] * 4
                out_offset = y * width * 4
                buffer[out_offset:out_offset + use_width * 4] = frame[2][in_offset:in_offset + use_width * 4]
            with session.stream_lock:
                session.stream.send(bytes(update))
                session.stream.send(bytes(buffer))
        else:
            with session.stream_lock:
                session.stream.send(bytes(update))
                session.stream.send(bytes(frame[2]))

    def VNCClientThread(self, session):
        try:
            self.VNCSendVersion(session.stream)
            self.VNCSecurityHandshake(session.stream)
            self.VNCClientServerInit(session.stream)

            version = 0
            first = True
            while True:
                new_version = self._display.GetClock()
                if new_version != version or first:
                    version = new_version
                    self.VNCSendFrame(session, first)
                    first = False

                if self.VNCWaitForEvent(session) == False:
                    break
        except Exception as e:
            print(f'VNCClientThread exception: {e}, line number: {e.__traceback__.tb_lineno}')

        session.stream.close()

    def VNCServerThread(self, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('0.0.0.0', port))
        s.listen(128)
        print(f'Listening on port {port} for a VNC session')

        while True:
            client, c_addr = s.accept()
            print(f'VNC server connected to {c_addr}')

            session = self.VNCSession()
            session.stream_lock = threading.Lock()
            session.stream = client

            t = threading.Thread(target=self.VNCClientThread, args=(session,))
            t.daemon = True
            t.name = 'VNC client'
            t.start()
