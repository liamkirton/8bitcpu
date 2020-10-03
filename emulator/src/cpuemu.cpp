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

    if (argc != 2) {
        return usage();
    }

    std::ifstream memory_init_file(argv[1], std::ios::binary);
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
    machine.set_dump(false);

    while (machine.running()) {
        machine.step();

        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }

    std::cout << std::endl << std::endl;
}
