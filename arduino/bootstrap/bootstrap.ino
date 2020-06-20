////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#include "rom.h"

//
// Shift Register Pins
//

constexpr uint32_t PIN_SER = 2;
constexpr uint32_t PIN_SRCLK = 3;
constexpr uint32_t PIN_RCLK = 4;
constexpr uint32_t PIN_OUT = 5;

//
// Memory Control Pins
//

constexpr uint32_t PIN_MCLK = 6;
constexpr uint32_t PIN_MADDRIN = 7;
constexpr uint32_t PIN_MOUT = 8;
constexpr uint32_t PIN_MIN = 9;

//
// General Control Pins
//

constexpr uint32_t PIN_PROGRAM = 12;

//
// Constants
//

constexpr uint32_t DELAY_US = 50;
constexpr uint32_t DELAY_LONG_MS = 1000;

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

void clear_bus() {
    digitalWrite(PIN_OUT, HIGH);
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

void write_bus(uint16_t address) {
    clear_bus();

    address = ((address & 0x00ff) << 8) | ((address & 0xff00) >> 8);

    for (int8_t i = 15; i >= 0; --i) {
        bool bit = address & (1 << i);
        digitalWrite(PIN_SER, bit ? HIGH : LOW);
        digitalWrite(PIN_SRCLK, HIGH);
        delayMicroseconds(DELAY_US);
        digitalWrite(PIN_SRCLK, LOW);
    }

    digitalWrite(PIN_RCLK, HIGH);
    delayMicroseconds(DELAY_US);
    digitalWrite(PIN_RCLK, LOW);

    digitalWrite(PIN_OUT, LOW);
    delayMicroseconds(DELAY_US);
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

void write_mem_addr(uint16_t address) {
    write_bus(address);
    digitalWrite(PIN_MADDRIN, HIGH);
    digitalWrite(PIN_MCLK, HIGH);
    delayMicroseconds(DELAY_US);
    digitalWrite(PIN_MCLK, LOW);
    digitalWrite(PIN_MADDRIN, LOW);
    clear_bus();
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

void write_mem_value(uint8_t value) {
    write_bus(value);
    digitalWrite(PIN_MIN, HIGH);
    delayMicroseconds(DELAY_US);
    digitalWrite(PIN_MIN, LOW);
    clear_bus();
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

void output_mem(uint16_t address) {
    write_mem_addr(address);
    delay(DELAY_LONG_MS);
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

void write_mem(uint16_t address, uint8_t value) {
    write_mem_addr(address);
    delayMicroseconds(DELAY_US);

    write_mem_value(value);
    delayMicroseconds(DELAY_US);
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

void disable() {
    pinMode(PIN_MADDRIN, INPUT);
    pinMode(PIN_MIN, INPUT);
    pinMode(PIN_MOUT, INPUT);
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

void enable() {
    pinMode(PIN_MADDRIN, OUTPUT);
    pinMode(PIN_MIN, OUTPUT);
    pinMode(PIN_MOUT, OUTPUT);
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

void setup() {
    Serial.begin(115200);
    Serial.println("8bitcpu Bootstrap");

    pinMode(PIN_SER, OUTPUT);
    pinMode(PIN_SRCLK, OUTPUT);
    pinMode(PIN_RCLK, OUTPUT);
    pinMode(PIN_OUT, OUTPUT);

    pinMode(PIN_PROGRAM, INPUT);

    digitalWrite(PIN_SER, LOW);
    digitalWrite(PIN_SRCLK, LOW);
    digitalWrite(PIN_RCLK, LOW);
    digitalWrite(PIN_OUT, HIGH);

    pinMode(PIN_MCLK, OUTPUT);
    pinMode(PIN_MADDRIN, INPUT);
    pinMode(PIN_MIN, INPUT);
    pinMode(PIN_MOUT, INPUT);

    digitalWrite(PIN_MCLK, LOW);

    delay(2500);
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

void program_rom() {
    enable();
    write_mem(255, 255);

    for (uint16_t i = 0; i < 256; ++i) {
        uint8_t v = 0;
        if (i < sizeof(INIT_PROGRAM)) {
            v = pgm_read_byte(&INIT_PROGRAM[i]);
        }
        write_mem(i, v);
    }
    for (uint16_t i = 0; i < sizeof(INIT_PROGRAM); ++i) {
        output_mem(i);
    }
    disable();
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

void loop() {
    static bool have_programmed_rom = false;

    if (!have_programmed_rom && digitalRead(PIN_PROGRAM) == HIGH) {
        have_programmed_rom = true;
        program_rom();
    }
    else if (have_programmed_rom) {
        have_programmed_rom = false;
    }

    if (Serial.available() > 0) {
        auto cmd = Serial.read();

        uint16_t address{ 0 };
        uint8_t value{ 0 };

        switch(cmd) {
            case 0x1:
                enable();
                Serial.write(1);
                break;

            case 0x2:
                disable();
                Serial.write(1);
                break;

            case 0x3:
                Serial.readBytes(reinterpret_cast<char *>(&address), sizeof(address));
                output_mem(address);
                Serial.write(address & 0xff);
                break;

            case 0x4:
                Serial.readBytes(reinterpret_cast<char *>(&address), sizeof(address));
                Serial.readBytes(reinterpret_cast<char *>(&value), sizeof(value));
                write_mem(address, value);
                Serial.write(address & 0xff);
                break;
        }
    }
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
