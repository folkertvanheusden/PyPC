import keyboard
import mda
import select
import socket
import struct
import threading
import time


def rawbytes(s):
    """Convert a string to raw bytes without encoding"""
    outlist = []
    for cp in s:
        num = ord(cp)
        if num < 255:
            outlist.append(struct.pack('B', num))
        elif num < 65535:
            outlist.append(struct.pack('>H', num))
        else:
            b = (num & 0xFF0000) >> 16
            H = num & 0xFFFF
            outlist.append(struct.pack('>bH', b, H))
    return b''.join(outlist)

class Telnet:
    def __init__(self, port: int, kb: keyboard.Keyboard, scr: mda.MDA):
        self._port = port
        self._kb = kb
        self._scr = scr
        t = threading.Thread(target=self.listener)
        t.daemon = True
        t.start()

    def push(self, c):
        key_map = dict()
        key_map[8] = ( 0x0e, )
        key_map[9] = ( 0x0f, )
        key_map[13] = ( 0x1c, )
        key_map[27] = ( 0x01, )
        key_map[ord('1')] = ( 0x02, )
        key_map[ord('2')] = ( 0x03, )
        key_map[ord('3')] = ( 0x04, )
        key_map[ord('4')] = ( 0x05, )
        key_map[ord('5')] = ( 0x06, )
        key_map[ord('6')] = ( 0x07, )
        key_map[ord('7')] = ( 0x08, )
        key_map[ord('8')] = ( 0x09, )
        key_map[ord('9')] = ( 0x0a, )
        key_map[ord('0')] = ( 0x0b, )
        key_map[ord('A')] = ( 0x2a, 0x1e, 0x1e | 0x80, 0x2a, 0xaa, )
        key_map[ord('B')] = ( 0x2a, 0x30, 0x30 | 0x80, 0x2a, 0xaa, )
        key_map[ord('C')] = ( 0x2a, 0x2e, 0x2e | 0x80, 0x2a, 0xaa, )
        key_map[ord('D')] = ( 0x2a, 0x20, 0x20 | 0x80, 0x2a, 0xaa, )
        key_map[ord('E')] = ( 0x2a, 0x12, 0x12 | 0x80, 0x2a, 0xaa, )
        key_map[ord('F')] = ( 0x2a, 0x21, 0x21 | 0x80, 0x2a, 0xaa, )
        key_map[ord('G')] = ( 0x2a, 0x22, 0x22 | 0x80, 0x2a, 0xaa, )
        key_map[ord('H')] = ( 0x2a, 0x23, 0x23 | 0x80, 0x2a, 0xaa, )
        key_map[ord('I')] = ( 0x2a, 0x17, 0x17 | 0x80, 0x2a, 0xaa, )
        key_map[ord('J')] = ( 0x2a, 0x24, 0x24 | 0x80, 0x2a, 0xaa, )
        key_map[ord('K')] = ( 0x2a, 0x25, 0x25 | 0x80, 0x2a, 0xaa, )
        key_map[ord('L')] = ( 0x2a, 0x26, 0x26 | 0x80, 0x2a, 0xaa, )
        key_map[ord('M')] = ( 0x2a, 0x32, 0x32 | 0x80, 0x2a, 0xaa, )
        key_map[ord('N')] = ( 0x2a, 0x31, 0x31 | 0x80, 0x2a, 0xaa, )
        key_map[ord('O')] = ( 0x2a, 0x18, 0x18 | 0x80, 0x2a, 0xaa, )
        key_map[ord('P')] = ( 0x2a, 0x19, 0x19 | 0x80, 0x2a, 0xaa, )
        key_map[ord('Q')] = ( 0x2a, 0x10, 0x10 | 0x80, 0x2a, 0xaa, )
        key_map[ord('R')] = ( 0x2a, 0x13, 0x13 | 0x80, 0x2a, 0xaa, )
        key_map[ord('S')] = ( 0x2a, 0x1f, 0x1f | 0x80, 0x2a, 0xaa, )
        key_map[ord('T')] = ( 0x2a, 0x14, 0x14 | 0x80, 0x2a, 0xaa, )
        key_map[ord('U')] = ( 0x2a, 0x16, 0x16 | 0x80, 0x2a, 0xaa, )
        key_map[ord('V')] = ( 0x2a, 0x2f, 0x2f | 0x80, 0x2a, 0xaa, )
        key_map[ord('W')] = ( 0x2a, 0x11, 0x11 | 0x80, 0x2a, 0xaa, )
        key_map[ord('X')] = ( 0x2a, 0x2d, 0x2d | 0x80, 0x2a, 0xaa, )
        key_map[ord('Y')] = ( 0x2a, 0x15, 0x15 | 0x80, 0x2a, 0xaa, )
        key_map[ord('Z')] = ( 0x2a, 0x2c, 0x2c | 0x80, 0x2a, 0xaa, )
        key_map[ord('a')] = ( 0x1e, )
        key_map[ord('b')] = ( 0x30, )
        key_map[ord('c')] = ( 0x2e, )
        key_map[ord('d')] = ( 0x20, )
        key_map[ord('e')] = ( 0x12, )
        key_map[ord('f')] = ( 0x21, )
        key_map[ord('g')] = ( 0x22, )
        key_map[ord('h')] = ( 0x23, )
        key_map[ord('i')] = ( 0x17, )
        key_map[ord('j')] = ( 0x24, )
        key_map[ord('k')] = ( 0x25, )
        key_map[ord('l')] = ( 0x26, )
        key_map[ord('m')] = ( 0x32, )
        key_map[ord('n')] = ( 0x31, )
        key_map[ord('o')] = ( 0x18, )
        key_map[ord('p')] = ( 0x19, )
        key_map[ord('q')] = ( 0x10, )
        key_map[ord('r')] = ( 0x13, )
        key_map[ord('s')] = ( 0x1f, )
        key_map[ord('t')] = ( 0x14, )
        key_map[ord('u')] = ( 0x16, )
        key_map[ord('v')] = ( 0x2f, )
        key_map[ord('w')] = ( 0x11, )
        key_map[ord('x')] = ( 0x2d, )
        key_map[ord('y')] = ( 0x15, )
        key_map[ord('z')] = ( 0x2c, )
        key_map[ord(' ')] = ( 0x39, )
        key_map[ord('.')] = ( 0x34, )
        key_map[ord('-')] = ( 0x0c, )
        key_map[ord('_')] = ( 0x2a, 0x0c, 0x0c | 0x80, 0x2a, 0xaa, )
        key_map[ord(':')] = ( 0x2a, 0x27, 0x27 | 0x80, 0x2a, 0xaa, )

        if c in key_map:
            messages = key_map[c]
            for i in range(len(messages)):
                self._kb.PushKeyboardScancode(messages[i])
            if len(messages) == 1:
                self._kb.PushKeyboardScancode(messages[0] ^ 0x80)

    def SetupTelnetSession(self, s):
        dont_auth          = ( 0xff, 0xf4, 0x25 )
        suppress_goahead   = ( 0xff, 0xfb, 0x03 )
        dont_linemode      = ( 0xff, 0xfe, 0x22 )
        dont_new_env       = ( 0xff, 0xfe, 0x27 )
        will_echo          = ( 0xff, 0xfb, 0x01 )
        dont_echo          = ( 0xff, 0xfe, 0x01 )
        noecho             = ( 0xff, 0xfd, 0x2d )
        binary             = ( 0xff, 0xfd, 0x00 )
        charset            = ( 0xFF, 0xFA, 0x2A, 0x02, 0x55, 0x54, 0x46, 0x2D, 0x38, 0xFF, 0xF0 )

        s.send(bytearray(dont_auth))
        s.send(bytearray(suppress_goahead))
        s.send(bytearray(dont_linemode))
        s.send(bytearray(dont_new_env))
        s.send(bytearray(will_echo))
        s.send(bytearray(dont_echo))
        s.send(bytearray(noecho))
        s.send(bytearray(binary))
        s.send(bytearray(charset))

    def PushScreen(self, s):
        out = ''
        for i in range(0, 25 * 80 * 2, 2):
            out += self._scr.UpdateConsole(i)
        s.send(rawbytes(out))

    def checkForData(self, s):
        (r_read, r_write, has_errors) = select.select([ s ], [ ], [ ], 0)
        return len(r_read) > 0

    def send_cursor(self, s, ansii_code):
        code = None
        if ansii_code == ord('A'):  # UP
            print('UP')
            code = 0x48
        elif ansii_code == ord('B'):  # DOWN
            print('DOWN')
            code = 0x50
        elif ansii_code == ord('C'):  # RIGHT
            print('RIGHT')
            code = 0x4d
        elif ansii_code == ord('D'):  # LEFT
            print('LEFT')
            code = 0x4b
        else:
            return None

        self.push(code)
        return code | 0x80, time.time()

    def runner(self, s):
        self.SetupTelnetSession(s)

        undo_code = None
        p_send = 0.0
        last_mda = -1
        kb = False
        while True:
            now = time.time()
            mda_clock = self._scr.GetClock()
            if kb == False and mda_clock > last_mda:
                last_mda = mda_clock
                p_send = now
                self.PushScreen(s)

            (r_read, r_write, has_errors) = select.select([ s ], [ ], [ ], 0.01)
            kb = False
            if len(r_read) == 0:
                continue

            if not undo_code is None and time.time() - undo_code[1] >= 0.01:
                self.push(undo_code[0])
                undo_code = None

            kb = True

            temp = s.recv(1)
            if temp == None or len(temp) == 0:
                break
            buffer = int.from_bytes(temp, 'little')

            # if escape, wait 5 ms for more data
            # if more data in that delay, then check if that's a cursor key
            # else just return the escape
            if buffer == 27:
                time.sleep(0.005)  # sleep 5 ms

                if self.checkForData(s) == False:
                    print('no other data', buffer)
                    # no other data, just push the escape
                    self.push(buffer)
                    continue

                # see if the waiting data is a cursor key
                buffer = int.from_bytes(s.recv(1), 'little')
                if buffer == ord('['):  # if [ then assume a cursor movement was sent
                    cursor = [ 0 ] * 6
                    pos = 0
                    while True:
                        cursor[pos] = int.from_bytes(s.recv(1), 'little')
                        c = cursor[pos]
                        pos += 1
                        if pos == len(cursor):  # should not happen
                            print('escape too long')
                            break  # discard code: this can be improved TODO
                        if c < ord('0') or c > ord('9'):
                            break

                    ansii_code = cursor[pos - 1] if pos > 0 else 0

                    undo_code = self.send_cursor(s, ansii_code)
                    if undo_code == None:
                        print('escape', cursor, 'invalid?', '-')

                else:
                    print('escape invalid?', 27, buffer)
                    self.push(27)
                    self.push(buffer)
            else:
                print('as is', buffer)
                self.push(buffer)

    def listener(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('0.0.0.0', self._port))
        s.listen()

        while True:
            c_sock, c_addr = s.accept()

            t = threading.Thread(target=self.runner, args=(c_sock,))
            t.daemon = True
            t.start()
