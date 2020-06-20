import argparse

import at28c256


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


def run(port):
    a = at28c256.AT28C256()

    for i in range(0, 256):
        a.write(i, 0x8);                                # .
        a.write(i + 256, digits[(i // 100) % 10]);      # 100s
        a.write(i + 512, digits[(i // 10) % 10]);       # 10s
        a.write(i + 768, digits[i % 10]);               # 1s

    at28c256.hexdump(a.read_range(0, 256), address=0)
    at28c256.hexdump(a.read_range(256, 256), address=256)
    at28c256.hexdump(a.read_range(512, 256), address=512)
    at28c256.hexdump(a.read_range(768, 256), address=768)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('port', type=str)
    args = parser.parse_args()

    if not args.port:
        raise Exception('Invalid COM PORT')

    run(args.port)
