import keyboard
import mda
import select
import socket
import threading
import time


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

        s.send(bytearray(dont_auth))
        s.send(bytearray(suppress_goahead))
        s.send(bytearray(dont_linemode))
        s.send(bytearray(dont_new_env))
        s.send(bytearray(will_echo))
        s.send(bytearray(dont_echo))
        s.send(bytearray(noecho))

    def PushScreen(self, s):
        out = ''
        for i in range(0, 25 * 80 * 2, 2):
            out += self._scr.UpdateConsole(i)
        s.send(out.encode('ascii'))

    def runner(self, s):
        self.SetupTelnetSession(s)

        p_send = 0.0
        last_mda = 0
        kb = False
        while True:
            now = time.time()
            mda_clock = self._scr.GetClock()
            if now - p_send >= 0.04 and kb == False and mda_clock > last_mda:
                last_mda = mda_clock
                p_send = now
                self.PushScreen(s)

            (r_read, r_write, has_errors) = select.select([ s ], [ ], [ ], 0.01)

            kb = False
            for ready in r_read:
                kb = True
                b = int.from_bytes(ready.recv(1), 'little')
                self.push(b)

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
