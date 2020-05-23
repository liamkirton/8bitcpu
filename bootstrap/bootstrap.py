import serial
import struct


class Bootstrap(object):

    def __init__(self):
        self.serial = serial.Serial('COM4', 115200)
        print('>>>>> AT28C256 Serial Connected ("', self.serial.readline().decode('ascii').strip(), '")', sep='')

    def __enter__(self):
        self.enable()
        return self

    def __exit__(self, type, value, traceback):
        self.disable()

    def enable(self):
        self.serial.write(b'\x01')
        return self.serial.read()

    def disable(self):
        self.serial.write(b'\x02')
        return self.serial.read()

    def output(self, address):
        self.serial.write(b'\x03' + struct.pack('<H', address & 0x7fff))
        return self.serial.read()[0]

    def write(self, address, value):
        self.serial.write(b'\x04' + struct.pack('<HB', address & 0x7fff, value & 0xff))
        return self.serial.read()[0]
