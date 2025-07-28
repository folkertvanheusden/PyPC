#! /usr/bin/python3

import bus
import i8088
import i8253
import mda
import rom

devices = []
devices.append(i8253.i8253())
devices.append(mda.MDA())

roms = []
roms.append(rom.Rom('GLABIOS.ROM', 0xf000 * 16 + 0xe000))

b = bus.Bus(1024 * 1024, devices, roms)
p = i8088.i8088(b, [], False)
state = p.GetState()
state.SetCS(0xf000)
state.SetIP(0xfff0)

while True:
    print(f'{state.GetCS():04x}:{state.GetIP():04x}')
    rc = p.Tick()
    if rc == -1:
        break
