import at28c256


def hexdump(b, address=0):
    for i in range(0, len(b), 16):
        b_slice = b[i:i+16]
        b_slice = b_slice + bytes(16 - len(b_slice))
        b_hex = ' '.join([f'{v:02x}' for v in b_slice])
        b_chr = ''.join(['%c' % (v if v >= 0x20 and v < 0x7f else '.') for v in b_slice])
        print(f'[{address+i:04x}]  ', b_hex, '  ', b_chr)


digits = [
    0x77, # 0
    0x14, # 1
    0xb3, # 2
    0xb6, # 3
    0xd4, # 4
    0xe6, # 5
    0xe7, # 6
    0x34, # 7
    0xf7, # 8
    0xf6  # 9
]

a = at28c256.AT28C256()

for i in range(0, 256):
    a.write(i, 0x8);                                # .
    a.write(i + 256, digits[(i // 100) % 10]);      # 100s
    a.write(i + 512, digits[(i // 10) % 10]);       # 10s
    a.write(i + 768, digits[i % 10]);               # 1s

hexdump(a.read_range(0, 256), address=0)
hexdump(a.read_range(256, 256), address=256)
hexdump(a.read_range(512, 256), address=512)
hexdump(a.read_range(768, 256), address=768)
