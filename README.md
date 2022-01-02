# 8bitcpu

![8bitcpu](docs/img/20210404_0060023.jpg)

## Overview

This is my modified build of [Ben Eater’s 8-bit computer project](https://eater.net/8bit/) - which is an incredible introduction to digital electronics and computer architecture! I won’t explain the background to the project in detail here, so do check out Ben’s awesome [YouTube series](https://www.youtube.com/watch?v=HyznrdDSSGM&list=PLowKtXNTBypGqImE405J2565dvjafglHU).

In brief, the idea is to use basic 7400-series logic chips wired together on breadboards to build the simplest possible programmable computer from scratch.

The architecture and layout of my build follows Ben’s fairly closely, with a few enhancements:

* 74HC series chips
* 16-bit address bus, to enable addressing of 32KB SRAM
* 16-bit memory address register
* 16-bit instruction register, to give an 8-bit instruction opcode and 8-bit operand
* 2 x 16-bit general purpose registers C and D, although arithmetic remains 8-bit
* 8-bit segment register to extend the 8-bit program counter (allowing execution beyond the bottom 256-byte memory segment)
* Arduino Nano to bootstrap the SRAM, and allow direct SRAM write-only via USB
 
I've also written an assembler and emulator, to ease development.

## Docs

See [docs/Index.md](docs/Index.md).