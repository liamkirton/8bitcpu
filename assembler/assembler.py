import argparse
import os
import re

import at28c256
import bootstrap


class Label:
    def __init__(self, label):
        self.label = label

    def __str__(self):
        return f'Label[{self.label}]'


class LabelRef:
    def __init__(self, label):
        self.label = label

    def __str__(self):
        return f'LabelRef[{self.label}]'


class Memory:
    def __init__(self, ref):
        self.ref = ref

    def __str__(self):
        return f'Memory[{self.ref}]'


class Register:
    def __init__(self, reg):
        reg = reg.upper()
        if not reg in ['A', 'B', 'C', 'DL', 'DH', 'D', 'SEG']:
            raise Exception(f'Invalid Register Specified {reg}')
        self.reg = reg
        self.reg_offset = {'A': 0, 'B': 1, 'C': 2, 'DL': 3, 'DH': 4, 'D': 5, 'SEG': 6}[reg]

    def __str__(self):
        return f'Register[{self.reg}]'


class Value:
    def __init__(self, val):
        self.val = val

    def __str__(self):
        return f'Value[{self.val}]'


def assemble(tokens):
    for i in range(0, len(tokens)):
        mneumonic, params = tokens[i][0], tokens[i][1:]

        if type(mneumonic) == Label:
            continue
        elif type(mneumonic) != str:
            raise Exception(f'Unknown Mneumonic {mneumonic}')
            
        mneumonic = mneumonic.upper()

        translation = []

        if mneumonic == 'HLT':
            translation.append(0x01)
        elif mneumonic == 'NOP':
            translation.append(0x00)
        elif mneumonic == 'OUT':
            translation.append(0x43)

        elif mneumonic == 'LD':
            if len(params) != 2:
                raise Exception(f'Syntax: LD SRC DST')
            src, dst = params

            if type(dst) != Register:
                raise Exception(f'LD DST Register Expected {dst}')

            if type(src) == Value:
                translation.append(0x09 + dst.reg_offset)
                translation.append(src.val)
            elif type(src) == Memory:
                src = src.ref
                if type(src) != Value:
                    raise Exception(f'LD SRC Memory Requires Fixed Address {src}')
                translation.append(0x02 + dst.reg_offset)
                translation.append(src.val)
        elif mneumonic == 'MV':
            if len(params) != 2:
                raise Exception(f'Syntax: MV SRC DST')
            src, dst = params

            if type(src) != Register:
                raise Exception(f'MV SRC Register Expected')
            elif type(dst) != Register:
                raise Exception(f'MV DST Register Expected')

            translation.append(0x25 + 7 * src.reg_offset + dst.reg_offset)

        elif mneumonic == 'ST':
            if len(params) != 2:
                raise Exception(f'Syntax: ST SRC DST')
            src, dst = params

            if type(src) != Register:
                raise Exception(f'ST SRC Register Expected')
            elif type(dst) is not Memory:
                raise Exception(f'ST DST Memory Expected')

            dst = dst.ref
            if type(dst) not in [Register, Value]:
                raise Exception(f'ST DST Memory *Register/*Value')

            if type(dst) == Value:
                translation.append(0x10 + src.reg_offset)
                translation.append(dst.val)
            else:
                if dst.reg not in ['C', 'D']:
                    raise Exception(f'ST DST Register Must Be C or D')
                if dst.reg == 'C':
                    translation.append(0x17 + src.reg_offset)
                else:
                    translation.append(0x1e + src.reg_offset)

        elif mneumonic == 'ADD':
            translation.append(0x41)
        elif mneumonic == 'SUB':
            translation.append(0x42)

        elif mneumonic == 'JMP':
            if len(params) != 1:
                raise Exception(f'Syntax: JMP TARGET')
            target = params[0]
            if type(target) not in [LabelRef, Memory, Register]:
                raise Exception('JMP TARGET Memory/Label/Register Expected')

            if type(target) == Register:
                translation.append(0x45 + target.reg_offset)
            else:
                translation.append(0x44)
                if type(target) == Memory:
                    translation.append(target.addr)
                else:
                    translation.append(target)

        elif mneumonic in ['JC', 'JZ']:
            if len(params) != 1:
                raise Exception(f'Syntax: JC/JZ TARGET')
            target = params[0]
            if type(target) not in [LabelRef, Memory]:
                raise Exception('JMP TARGET Memory/Label Expected')
            translation.append({'JC': 0x4c, 'JZ': 0x4d}[mneumonic])
            if type(target) == Memory:
                translation.append(target.addr)
            else:
                translation.append(target)

        else:
            raise Exception(f'Unknown Mneumonic {mneumonic}')

        tokens[i] = translation

    return tokens


def link(object_code):
    labels = {}
    machine_code = []
    offset = 0
    for i in range(0, len(object_code)):
        if len(object_code[i]) == 1 and type(object_code[i][0]) == Label:
            labels[object_code[i][0].label] = offset
            continue
        machine_code.append(object_code[i])
        offset += len(object_code[i])
    for i in range(0, len(machine_code)):
        for j in range(0, len(machine_code[i])):
            if type(machine_code[i][j]) == LabelRef:
                if not machine_code[i][j].label in labels:
                    raise Exception(f'Unmatched Label Reference {machine_code[i][j].label}')
                machine_code[i][j] = labels[machine_code[i][j].label]

    return machine_code


def read_lines(source_file):
    with open(source_file, 'r') as f:
        file_lines = f.readlines()

    for i in range(0, len(file_lines)):
        l = file_lines[i]
        l = l.strip()
        l = l.split('#', maxsplit=1)[0]
        file_lines[i] = l.strip()

    file_lines = [l for l in file_lines if len(l)]
    return file_lines


def parse(file_lines):
    tokens = []

    def _translate(t):
        if t.startswith('*'):
            t = _translate(t[1:])
            if type(t) not in [Register, Value]:
                raise Exception(f'Memory Syntax Error: *0x10')
            t = Memory(t)
        elif t.isdigit():
            t = Value(int(t))
        elif t.startswith('0x') and re.match('[0-9a-fA-F]+', t[2:]):
            t = Value(int(t, 16))
        elif re.match('^[a-zA-Z]{1}[a-zA-Z0-9\-_]+:$', t):
            t = Label(t[:-1])
        elif t.startswith('R'):
            t = Register(t[1:])
        elif j > 0 and re.match('^[a-zA-Z]{1}[a-zA-Z0-9\-_]+$', t):
            t = LabelRef(t)
        return t

    for i in range(0, len(file_lines)):
        l_tokens = file_lines[i].split(' ')
        for j in range(0, len(l_tokens)):
            l_tokens[j] = _translate(l_tokens[j])

        tokens.append(l_tokens)

    return tokens


def print_assembly(file_lines, machine_lines, machine_code):
    print()

    j = 0
    k = 0
    for i in range(0, len(file_lines)):
        if re.match('^[a-zA-Z]{1}[a-zA-Z0-9\-_]+:$', file_lines[i]):
            print(file_lines[i])
        else:
            machine_line = ' '.join([f'{v:02x}' for v in machine_lines[j]])
            pad = (5 - len(machine_line)) * ' '
            print(f'  [ {k:04x} ]  {machine_line}{pad}    {file_lines[i]}')
            k += len(machine_lines[j])
            j += 1

    print()
    at28c256.hexdump(machine_code)
    print()


def run(args):
    source_file = args.file
    bin_file = os.path.splitext(args.file)[0] + '.bin'

    file_lines = read_lines(source_file)
    tokens = parse(file_lines)
    object_lines = assemble(tokens)
    machine_lines = link(object_lines)
    machine_code = b''.join([bytes(b) for b in machine_lines])

    print_assembly(file_lines, machine_lines, machine_code)

    if args.port:
        with bootstrap.Bootstrap(args.port) as b:
            b.write_range(0, machine_code)
        print()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Assembler.')
    parser.add_argument('--program', dest='port', default='', type=str)
    parser.add_argument('file', type=str)
    args = parser.parse_args()

    if not args.file:
        raise Exception(f'Invalid File {args.file}')
    
    args.file = os.path.abspath(args.file)
    if not os.path.exists(args.file):
        raise Exception(f'Cannot File File {args.file}')

    run(args)
