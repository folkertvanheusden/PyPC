#! /usr/bin/python3

import bus
import i8088
import json
import pprint
import sys
import time

def my_assert(state, test, is_, exp, what):
    if is_ != exp:
        print(f'--> Expected: {exp} ({exp:x}h), is: {is_} ({is_:x}h), different bits: {exp ^ is_:x}h, for {what}')
        print()
        state.DumpState()
        pprint.pp(test)
        print()
        print()
        #sys.exit(1)
        return False

    return True

def dissect_flags(f):
    out = ''
    out += 'o' if f & 2048 else '-'
    out += 's' if f & 128 else '-'
    out += 'z' if f & 64 else '-'
    out += 'a' if f & 16 else '-'
    out += 'p' if f & 4 else '-'
    out += 'c' if f & 1 else '-'
    return out

def my_assert_flags(state, test, is_, exp, what):
    if is_ != exp:
        print(f'flags is  : {dissect_flags(is_)}')
        print(f'flags exp : {dissect_flags(exp)}')
        print(f'flags diff: {dissect_flags(is_ ^ exp)}')

    return my_assert(state, test, is_, exp, what)

start = time.time()

j = json.loads(open(sys.argv[1], 'r').read())

count = 0
ok = 0

b = bus.Bus(1024 * 1024, [], [])
p = i8088.i8088(b, [], False)
state = p.GetState()

for test in j:
    b.ClearMemory()
    p.Reset()

    opcodes = [ f'{b:02x}' for b in test['bytes'] ]
    print(f'Testing {test["name"]} / {test["hash"]} / opcodes: {", ".join(opcodes)}')

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
        rc = p.Tick()
        if rc == -1:
            break
        if p.IsProcessingRep() == False:
            break

    regs = test['final']['regs']
    failed = False
    for reg in regs:
        if reg == 'ax':
            failed |= not my_assert(state, test, state.GetAX(), regs[reg], f'reg {reg}')
        elif reg == 'bx':
            failed |= not my_assert(state, test, state.GetBX(), regs[reg], f'reg {reg}')
        elif reg == 'cx':
            failed |= not my_assert(state, test, state.GetCX(), regs[reg], f'reg {reg}')
        elif reg == 'dx':
            failed |= not my_assert(state, test, state.GetDX(), regs[reg], f'reg {reg}')
        elif reg == 'cs':
            failed |= not my_assert(state, test, state.GetCS(), regs[reg], f'reg {reg}')
        elif reg == 'ss':
            failed |= not my_assert(state, test, state.GetSS(), regs[reg], f'reg {reg}')
        elif reg == 'ds':
            failed |= not my_assert(state, test, state.GetDS(), regs[reg], f'reg {reg}')
        elif reg == 'es':
            failed |= not my_assert(state, test, state.GetES(), regs[reg], f'reg {reg}')
        elif reg == 'sp':
            failed |= not my_assert(state, test, state.GetSP(), regs[reg], f'reg {reg}')
        elif reg == 'bp':
            failed |= not my_assert(state, test, state.GetBP(), regs[reg], f'reg {reg}')
        elif reg == 'si':
            failed |= not my_assert(state, test, state.GetSI(), regs[reg], f'reg {reg}')
        elif reg == 'di':
            failed |= not my_assert(state, test, state.GetDI(), regs[reg], f'reg {reg}')
        elif reg == 'ip':
            failed |= not my_assert(state, test, state.GetIP(), regs[reg], f'reg {reg}')
        elif reg == 'flags':
            failed |= not my_assert_flags(state, test, state.GetFlags(), regs[reg], f'reg {reg}')
    for ram in test['final']['ram']:
        failed |= not my_assert(state, test, b.ReadByte(ram[0])[0], ram[1], f'ram {ram[0]}')
    ok += not failed
    count += 1

    if failed:
        print(f'FAILED: {test["name"]} opcodes: {", ".join(opcodes)}')
        print('---')

print(f'Total count: {count}, ok: {ok}, failed: {(count - ok) / count * 100:.2f}%')
print(f'Took: {time.time() - start:.2f}')

sys.exit(0 if ok == count else 1)
