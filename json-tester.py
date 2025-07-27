#! /usr/bin/python3

import bus
import i8088
import json
import sys

def my_assert(state, test, exp, is_, what):
    if is_ != exp:
        state.DumpState()
        print()
        print(test)
        print()
        print(f'Expected: {exp}, is: {is_}, for {what}')
        sys.exit(1)


j = json.loads(open(sys.argv[1], 'r').read())

for test in j:
    print(f'Testing {test["name"]}')

    b = bus.Bus(1024 * 1024, [], [])
    p = i8088.i8088(b, [], False)
    state = p.GetState()

    regs = test['initial']['regs']
    for reg in regs:
        if reg == 'ax':
            state.SetAX(regs[reg])
        elif reg == 'bx':
            state.SetBX(regs[reg])
        elif reg == 'cx':
            state.SetCX(regs[reg])
        elif reg == 'dx':
            state.SetDX(regs[reg])
        elif reg == 'cs':
            state.SetCS(regs[reg])
        elif reg == 'ss':
            state.SetSS(regs[reg])
        elif reg == 'ds':
            state.SetDS(regs[reg])
        elif reg == 'es':
            state.SetES(regs[reg])
        elif reg == 'sp':
            state.SetSP(regs[reg])
        elif reg == 'bp':
            state.SetBP(regs[reg])
        elif reg == 'si':
            state.SetSI(regs[reg])
        elif reg == 'di':
            state.SetDI(regs[reg])
        elif reg == 'ip':
            state.SetIP(regs[reg])
        elif reg == 'flags':
            state.SetFlags(regs[reg])
    for ram in test['initial']['ram']:
        b.WriteByte(ram[0], ram[1])

    while True:
        rc = p.Tick();
        if rc == -1:
            break;
        if p.IsProcessingRep() == False:
            break

    regs = test['final']['regs']
    for reg in regs:
        if reg == 'ax':
            my_assert(state, test, state.GetAX(), regs[reg], f'reg {reg}')
        elif reg == 'bx':
            my_assert(state, test, state.GetBX(), regs[reg], f'reg {reg}')
        elif reg == 'cx':
            my_assert(state, test, state.GetCX(), regs[reg], f'reg {reg}')
        elif reg == 'dx':
            my_assert(state, test, state.GetDX(), regs[reg], f'reg {reg}')
        elif reg == 'cs':
            my_assert(state, test, state.GetCS(), regs[reg], f'reg {reg}')
        elif reg == 'ss':
            my_assert(state, test, state.GetSS(), regs[reg], f'reg {reg}')
        elif reg == 'ds':
            my_assert(state, test, state.GetDS(), regs[reg], f'reg {reg}')
        elif reg == 'es':
            my_assert(state, test, state.GetES(), regs[reg], f'reg {reg}')
        elif reg == 'sp':
            my_assert(state, test, state.GetSP(), regs[reg], f'reg {reg}')
        elif reg == 'bp':
            my_assert(state, test, state.GetBP(), regs[reg], f'reg {reg}')
        elif reg == 'si':
            my_assert(state, test, state.GetSI(), regs[reg], f'reg {reg}')
        elif reg == 'di':
            my_assert(state, test, state.GetDI(), regs[reg], f'reg {reg}')
        elif reg == 'ip':
            my_assert(state, test, state.GetIP(), regs[reg], f'reg {reg}')
        elif reg == 'flags':
            my_assert(state, test, state.GetFlags(), regs[reg], f'reg {reg}')
    for ram in test['final']['ram']:
        my_assert(state, test, b.ReadByte(ram[0]), ram[1], f'ram {ram[0]}')
