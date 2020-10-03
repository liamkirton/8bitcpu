#include "cpuemu.h"

int main(int argc, char *argv[]) {
    std::cout << std::endl
        << "8bitcpu Emulator" << std::endl
        << "(C)2020 Liam Kirton <liam@int3.ws>" << std::endl
        << std::endl;

    auto usage = []() {
        std::cout << "Usage: cpuemu.exe <program.bin>" << std::endl
            << std::endl;
        return -1;
    };

    std::string src_file;
    uint32_t delay_ms = 100;
    uint8_t output_level = 1;

    for (int i = 1; i < argc; ++i) {
        std::string k = argv[i];
        if ((k[0] == '-') && (i + 1 < argc)) {
            std::string v = argv[++i];
            if (k == "--delay") {
                delay_ms = std::atoi(v.c_str());
            }
            else if (k == "--output") {
                output_level = std::atoi(v.c_str());
                if (output_level > 4) {
                    output_level = 4;
                }
            }
            else {
                return usage();
            }
        }
        else {
            src_file = k;
        }
    }

    if (src_file.empty()) {
        return usage();
    }

    std::ifstream memory_init_file(src_file, std::ios::binary);
    if (!memory_init_file.is_open()) {
        return usage();
    }

    memory_init_file.seekg(0, std::ios::end);

    size_t memory_init_size = memory_init_file.tellg();
    std::shared_ptr<uint8_t[]> memory_init(new uint8_t[memory_init_size]);

    memory_init_file.seekg(0, std::ios::beg);
    memory_init_file.read(reinterpret_cast<char *>(memory_init.get()), memory_init_size);
    memory_init_file.close();

    cpuemu::Machine machine(memory_init, memory_init_size);
    machine.set_output(output_level);

    while (machine.running()) {
        machine.step();

        if (delay_ms > 0) {
            std::this_thread::sleep_for(std::chrono::milliseconds(delay_ms));
        }
    }

    std::cout << std::endl << std::endl;
}
