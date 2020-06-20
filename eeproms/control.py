import argparse
import copy
import itertools
import sys

import at28c256


# Control Lines

HALT  = (0, 0)  # 1
AIN   = (0, 1)  # 2
AOUT  = (0, 2)  # 3
BIN   = (0, 3)  # 4
BOUT  = (0, 4)  # 5
SOUT  = (0, 5)  # 6
SNEG  = (0, 6)  # 7
CIN   = (0, 7)  # 8
COUT  = (1, 0)  # 9
DLIN  = (1, 1)  # 10
DHIN  = (1, 2)  # 11
DOUT  = (1, 3)  # 12
OIN   = (1, 4)  # 13
ILIN  = (1, 5)  # 14
IHIN  = (1, 6)  # 15
IOUT  = (1, 7)  # 16
PCEN  = (2, 0)  # 17
PCLD  = (2, 1)  # 18
PCOUT = (2, 2)  # 19
MAIN  = (2, 3)  # 20
MIN   = (2, 4)  # 21, -> M Bus Dir [ M Bus Enable = not Mo and not Mi ]
MOUT  = (2, 5)  # 22, -> M out enable, not M write enable
FLIN  = (2, 6)  # 23
SGIN  = (2, 7)  # 24


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
    'HALT': (0x01, (
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (HALT,),
        (),
        (),
        (),
        (),
        (),
    )),

    ###
    ### LDXM
    ###

    'LDAM': (0x02, (
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (PCOUT, MAIN),
        (MOUT, ILIN, PCEN),
        (IOUT, MAIN),
        (MOUT, AIN),
        (),
        ()
    )),
    'LDBM': (0x03, (
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (PCOUT, MAIN),
        (MOUT, ILIN, PCEN),
        (IOUT, MAIN),
        (MOUT, BIN),
        (),
        ()
    )),
    'LDCM': (0x04, (
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (PCOUT, MAIN),
        (MOUT, ILIN, PCEN),
        (IOUT, MAIN),
        (MOUT, CIN),
        (),
        ()
    )),
    'LDDLM': (0x05, (
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (PCOUT, MAIN),
        (MOUT, ILIN, PCEN),
        (IOUT, MAIN),
        (MOUT, DLIN),
        (),
        ()
    )),
    'LDDHM': (0x06, (
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (PCOUT, MAIN),
        (MOUT, ILIN, PCEN),
        (IOUT, MAIN),
        (MOUT, DHIN),
        (),
        ()
    )),
    'LDDM': (0x07, ( # Equivalent to 'DL'
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (PCOUT, MAIN),
        (MOUT, ILIN, PCEN),
        (IOUT, MAIN),
        (MOUT, DLIN),
        (),
        ()
    )),
    'LDSGM': (0x08, (
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (PCOUT, MAIN),
        (MOUT, ILIN, PCEN),
        (IOUT, MAIN),
        (MOUT, SGIN),
        (),
        ()
    )),

    ###
    ### LDXI
    ###

    'LDAI': (0x09, (
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (PCOUT, MAIN),
        (MOUT, AIN, PCEN),
        (),
        (),
        (),
        ()
    )),
    'LDBI': (0x0a, (
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (PCOUT, MAIN),
        (MOUT, BIN, PCEN),
        (),
        (),
        (),
        ()
    )),
    'LDCI': (0x0b, (
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (PCOUT, MAIN),
        (MOUT, CIN, PCEN),
        (),
        (),
        (),
        ()
    )),
    'LDDLI': (0x0c, (
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (PCOUT, MAIN),
        (MOUT, DLIN, PCEN),
        (),
        (),
        (),
        ()
    )),
    'LDDHI': (0x0d, (
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (PCOUT, MAIN),
        (MOUT, DHIN, PCEN),
        (),
        (),
        (),
        ()
    )),
    'LDDI': (0x0e, ( # Equivalent to 'DL'
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (PCOUT, MAIN),
        (MOUT, DLIN, PCEN),
        (),
        (),
        (),
        ()
    )),
    'LDSGI': (0x0f, (
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (PCOUT, MAIN),
        (MOUT, SGIN, PCEN),
        (),
        (),
        (),
        ()
    )),

    ###
    ### STX
    ###

    'STA': (0x10, (
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (PCOUT, MAIN),
        (MOUT, ILIN, PCEN),
        (IOUT, MAIN),
        (AOUT, MIN),
        (),
        ()
    )),
    'STB': (0x11, (
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (PCOUT, MAIN),
        (MOUT, ILIN, PCEN),
        (IOUT, MAIN),
        (BOUT, MIN),
        (),
        ()
    )),
    'STC': (0x12, (
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (PCOUT, MAIN),
        (MOUT, ILIN, PCEN),
        (IOUT, MAIN),
        (COUT, MIN),
        (),
        ()
    )),
    'STDL': (0x13, (
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (PCOUT, MAIN),
        (MOUT, ILIN, PCEN),
        (IOUT, MAIN),
        (DOUT, MIN),
        (),
        ()
    )),
    'STDH': (0x14, ( # Equivalent to NOP
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (PCEN,),
        (),
        (),
        (),
        (),
        ()
    )),
    'STD': (0x15, ( # Equivalent to 'DL'
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (PCOUT, MAIN),
        (MOUT, ILIN, PCEN),
        (IOUT, MAIN),
        (DOUT, MIN),
        (),
        ()
    )),
    'STSG': (0x16, ( # Equivalent to NOP
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (PCEN,),
        (),
        (),
        (),
        (),
        ()
    )),

    ###
    ### MVAX
    ###

    'MVAA': (0x17, ( # Equivalent to NOP
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (),
        (),
        (),
        (),
        (),
        ()
    )),
    'MVAB': (0x18, (
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (AOUT, BIN),
        (),
        (),
        (),
        (),
        ()
    )),
    'MVAC': (0x19, (
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (AOUT, CIN),
        (),
        (),
        (),
        (),
        ()
    )),
    'MVADL': (0x1a, (
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (AOUT, DLIN),
        (),
        (),
        (),
        (),
        ()
    )),
    'MVADH': (0x1b, (
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (AOUT, DHIN),
        (),
        (),
        (),
        (),
        ()
    )),
    'MVAD': (0x1c, (
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (AOUT, DLIN, DHIN),
        (),
        (),
        (),
        (),
        ()
    )),
    'MVASG': (0x1d, (
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (AOUT, SGIN),
        (),
        (),
        (),
        (),
        ()
    )),

    ###
    ### MVBX
    ###

    'MVBA': (0x1e, (
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (BOUT, AIN),
        (),
        (),
        (),
        (),
        ()
    )),
    'MVBB': (0x1f, ( # Equivalent to NOP
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (),
        (),
        (),
        (),
        (),
        ()
    )),
    'MVBC': (0x20, (
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (BOUT, CIN),
        (),
        (),
        (),
        (),
        ()
    )),
    'MVBDL': (0x21, (
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (BOUT, DLIN),
        (),
        (),
        (),
        (),
        ()
    )),
    'MVBDH': (0x22, (
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (BOUT, DHIN),
        (),
        (),
        (),
        (),
        ()
    )),
    'MVBD': (0x23, (
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (BOUT, DLIN, DHIN),
        (),
        (),
        (),
        (),
        ()
    )),
    'MVBSG': (0x24, (
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (BOUT, SGIN),
        (),
        (),
        (),
        (),
        ()
    )),

    ###
    ### MVCX
    ###

    'MVCA': (0x25, (
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (COUT, AIN),
        (),
        (),
        (),
        (),
        ()
    )),
    'MVCB': (0x26, (
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (COUT, BIN),
        (),
        (),
        (),
        (),
        ()
    )),
    'MVCC': (0x27, ( # Equivalent to NOP
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (),
        (),
        (),
        (),
        (),
        ()
    )),
    'MVCDL': (0x28, (
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (COUT, DLIN),
        (),
        (),
        (),
        (),
        ()
    )),
    'MVCDH': (0x29, (
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (COUT, DHIN),
        (),
        (),
        (),
        (),
        ()
    )),
    'MVCD': (0x2a, (
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (COUT, DLIN, DHIN),
        (),
        (),
        (),
        (),
        ()
    )),
    'MVCSG': (0x2b, (
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (COUT, SGIN),
        (),
        (),
        (),
        (),
        ()
    )),

    ###
    ### MVDX
    ###

    'MVDA': (0x2c, (
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (DOUT, AIN),
        (),
        (),
        (),
        (),
        ()
    )),
    'MVDB': (0x2d, (
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (DOUT, BIN),
        (),
        (),
        (),
        (),
        ()
    )),
    'MVDC': (0x2e, (
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (DOUT, CIN),
        (),
        (),
        (),
        (),
        ()
    )),
    'MVDDL': (0x2f, ( # Equivalent to NOP
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (),
        (),
        (),
        (),
        (),
        ()
    )),
    'MVDDH': (0x30, ( # Equivalent to NOP
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (),
        (),
        (),
        (),
        (),
        ()
    )),
    'MVDD': (0x31, ( # Equivalent to NOP
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (),
        (),
        (),
        (),
        (),
        ()
    )),
    'MVDSG': (0x32, (
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (DOUT, SGIN),
        (),
        (),
        (),
        (),
        ()
    )),

    ###
    ### ALU
    ###

    'ADD': (0x33, (
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (FLIN,),
        (SOUT, AIN),
        (),
        (),
        (),
        ()
    )),
    'SUB': (0x34, (
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (SNEG, FLIN),
        (SNEG, SOUT, AIN),
        (),
        (),
        (),
        ()
    )),

    ###
    ### OUT
    ###

    'OUT': (0x35, (
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (AOUT, DLIN),
        (OIN,),
        (),
        (),
        (),
        ()
    )),

    ###
    ### JMP
    ###

    'JMPM': (0x36, (
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (PCOUT, MAIN),
        (MOUT, ILIN, PCEN),
        (IOUT, PCLD, SGIN),
        (),
        (),
        ()
    )),
    'JMPA': (0x37, (
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (AOUT, PCLD, SGIN),
        (),
        (),
        (),
        (),
        ()
    )),
    'JMPB': (0x38, (
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (BOUT, PCLD, SGIN),
        (),
        (),
        (),
        (),
        ()
    )),
    'JMPC': (0x39, (
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (COUT, PCLD, SGIN),
        (),
        (),
        (),
        (),
        ()
    )),
    'JMPDL': (0x3a, (
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (DOUT, PCLD),
        (),
        (),
        (),
        (),
        ()
    )),
    'JMPDH': (0x3b, ( # Equivalent to NOP
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (),
        (),
        (),
        (),
        (),
        ()
    )),
    'JMPD': (0x3c, (
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (DOUT, PCLD, SGIN),
        (),
        (),
        (),
        (),
        ()
    )),
    'JMPSG': (0x3d, ( # Equivalent to NOP
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (),
        (),
        (),
        (),
        (),
        ()
    )),

    ###
    ### Conditional JMPs (NOPs here)
    ###

    'JC': (0x3e, (
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (PCEN,),
        (),
        (),
        (),
        (),
        ()
    )),
    'JZ': (0x3f, (
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (PCEN,),
        (),
        (),
        (),
        (),
        ()
    ))
}

INSTRUCTIONS_CF = {
    'JC': (0x3e, (
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (PCOUT, MAIN),
        (MOUT, ILIN, PCEN),
        (IOUT, PCLD, SGIN),
        (),
        (),
        ()
    ))
}

INSTRUCTIONS_ZF = {
    'JZ': (0x3f, (
        (PCOUT, MAIN),
        (MOUT, IHIN, PCEN),
        (PCOUT, MAIN),
        (MOUT, ILIN, PCEN),
        (IOUT, PCLD, SGIN),
        (),
        (),
        ()
    ))
}


def run(port, target_eeprom):
    a = at28c256.AT28C256(port=port)

    opcodes_used = [ v[0] for v in INSTRUCTIONS.values() ]
    opcodes_unused = [ v for v in range(0, 0x100) if not v in opcodes_used ]

    INSTRUCTIONS.update({
        f'NOP_{o:02x}' : (o, copy.deepcopy(INSTRUCTIONS['NOP'][1]))
            for o in opcodes_unused
    })

    for flag_range in (0,1,2,3):
        for instr, (opcode, uops) in INSTRUCTIONS.items():
            print(hex(flag_range), instr, hex(opcode))

            if flag_range in [1, 3] and instr in INSTRUCTIONS_CF:
                (opcode, uops) = INSTRUCTIONS_CF[instr]
            if flag_range in [2, 3] and instr in INSTRUCTIONS_ZF:
                (opcode, uops) = INSTRUCTIONS_ZF[instr]

            for j in range(0, 8):
                addr = (flag_range << 11) | (opcode << 3) | j

                control_byte = 0
                for u in uops[j]:
                    eeprom, control_line = u
                    if eeprom == target_eeprom:
                        control_byte |= 1 << control_line

                print(f'{addr:06x}', f'{control_byte:02x}')
                a.write(addr, control_byte)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Program Control EEPROM.')
    parser.add_argument('eeprom', type=int)
    parser.add_argument('port', type=str)
    args = parser.parse_args()

    if args.eeprom < 0 or args.eeprom > 3:
        raise Exception('Invalid Target EEPROM')
    elif not args.port:
        raise Exception('Invalid COM PORT')

    run(args.port, args.eeprom)
