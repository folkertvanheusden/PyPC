#! /usr/bin/python3

import bus
import i8088
import i8253
import mda
import rom

def GetRegisters(state) -> str:
    return f'{state.GetFlagsAsString()} AX:{state.GetAX():04x} BX:{state.GetBX():04x} CX:{state.GetCX():04x} DX:{state.GetDX():04x} SP:{state.GetSP():04x} BP:{state.GetBP():04x} SI:{state.GetSI():04x} DI:{state.GetDI():04x} flags:{state.GetFlags():04x} ES:{state.GetES():04x} CS:{state.GetCS():04x} SS:{state.GetSS():04x} DS:{state.GetDS():04x} IP:{state.GetIP():04x}'

devices = []
devices.append(i8253.i8253())
devices.append(mda.MDA())

roms = []
roms.append(rom.Rom('GLABIOS.ROM', 0xf000 * 16 + 0xe000))

b = bus.Bus(1024 * 1024, devices, roms)
p = i8088.i8088(b, devices, True)
state = p.GetState()
state.SetCS(0xf000)
state.SetIP(0xfff0)

while True:
    # print(f'{state.GetCS():04x}:{state.GetIP():04x} {GetRegisters(state)}')
    rc = p.Tick()
    if rc == -1:
        break
