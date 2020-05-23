import time

import bootstrap


def hexdump(b, address=0):
    for i in range(0, len(b), 16):
        b_slice = b[i:i+16]
        b_slice = b_slice + bytes(16 - len(b_slice))
        b_hex = ' '.join([f'{v:02x}' for v in b_slice])
        b_chr = ''.join(['%c' % (v if v >= 0x20 and v < 0x7f else '.') for v in b_slice])
        print(f'[{address+i:04x}]  ', b_hex, '  ', b_chr)


with bootstrap.Bootstrap() as b:
    # for i in range(0, 256):
    #     b.write(i, 255 - i)

    for i in range(0, 256):
    #     b.write(i, i)
        v = b.output(i)
    #     time.sleep(0.1)
