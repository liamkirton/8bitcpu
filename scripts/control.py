import argparse
import copy
import sys

import at28c256


# Control Lines

HALT  = (0, 0)
AIN   = (0, 1)
AOUT  = (0, 2)
BIN   = (0, 3)
BOUT  = (0, 4)
SOUT  = (0, 5)
SNEG  = (0, 6)
CIN   = (0, 7)
COUT  = (1, 0)
DLIN  = (1, 1)
DHIN  = (1, 2)
DOUT  = (1, 3)
OIN   = (1, 4)
ILIN  = (1, 5)
IHIN  = (1, 6)
IOUT  = (1, 7)
PCEN  = (2, 0)
PCLD  = (2, 1)
PCOUT = (2, 2)
MAIN  = (2, 3)
MIN  =  (2, 4)
MOUT =  (2, 5)


INSTRUCTIONS = {
    'NOP': (0x00, (
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (),
        (),
        (),
        (),
        (),
        (),
    )),
    'LDA': (0x01, (
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (PCOUT, MAIN),
        (MOUT, ILIN, PCEN),
        (IOUT, MAIN),
        (MOUT, AIN),
        (),
        ()
    )),
    'LDB': (0x02, (
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (PCOUT, MAIN),
        (MOUT, ILIN, PCEN),
        (IOUT, MAIN),
        (MOUT, BIN),
        (),
        ()
    )),
    'STA': (0x03, (
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (PCOUT, MAIN),
        (MOUT, ILIN, PCEN),
        (IOUT, MAIN),
        (AOUT, MIN),
        (),
        ()
    )),
    'STB': (0x04, (
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (PCOUT, MAIN),
        (MOUT, ILIN, PCEN),
        (IOUT, MAIN),
        (BOUT, MIN),
        (),
        ()
    )),
    'LDIA': (0x05, (
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (PCOUT, MAIN),
        (MOUT, AIN, PCEN),
        (),
        (),
        (),
        ()
    )),
    'LDIB': (0x06, (
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (PCOUT, MAIN),
        (MOUT, BIN, PCEN),
        (),
        (),
        (),
        ()
    )),
    'ADD': (0x07, (
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (SOUT, AIN),
        (),
        (),
        (),
        (),
        ()
    )),
    'OUT': (0x08, (
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (AOUT, DLIN),
        (OIN,),
        (),
        (),
        (),
        ()
    )),
    'JMP': (0x09, (
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (PCOUT, MAIN),
        (MOUT, ILIN, PCEN),
        (IOUT, PCLD),
        (),
        (),
        ()
    )),
    'MVAC': (0x0a, (
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (AOUT, CIN),
        (),
        (),
        (),
        (),
        ()
    )),
    'MVCB': (0x0b, (
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (COUT, BIN),
        (),
        (),
        (),
        (),
        ()
    )),
}

OPCODES_USED = [ v[0] for v in INSTRUCTIONS.values() ]
OPCODES_UNUSED = [ v for v in range(0, 256) if not v in OPCODES_USED ]

INSTRUCTIONS.update({
    f'NOP_{o:02x}' : (o, copy.deepcopy(INSTRUCTIONS['NOP'][1]))
        for o in OPCODES_UNUSED
})


def run(target_eeprom):
    a = at28c256.AT28C256()

    for instr, (opcode, uops) in INSTRUCTIONS.items():
         for j in range(0, 8):
            addr = (opcode << 3) | j

            control_byte = 0
            for u in uops[j]:
                eeprom, control_line = u
                if eeprom == target_eeprom:
                    control_byte |= 1 << control_line

            print(f'{addr:04x}', f'{control_byte:02x}')
            a.write(addr, control_byte)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Program Control EEPROM.')
    parser.add_argument('eeprom', type=int)
    args = parser.parse_args()

    if args.eeprom < 0 or args.eeprom > 3:
        raise Exception('Invalid Target EEPROM')

    run(args.eeprom)
