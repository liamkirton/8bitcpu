#pragma once

namespace cpuemu {

    class Machine {
    public:
        Machine() : 
                memory_(new uint8_t[memory_size_]),
                pc_{ 0 }, reg_seg_{ 0 },
                flag_c_(false), flag_z_(false), halt_(false),
                reg_a_{ 0 }, reg_b_{ 0 }, reg_c_{ 0 }, reg_d_{ 0 }, reg_o_{ 0 } {
            std::memset(memory_.get(), 0, memory_size_);
        }

        Machine(std::shared_ptr<uint8_t[]> memory_init, size_t memory_init_size) : Machine() {
            std::memcpy(memory_.get(), memory_init.get(), std::min(memory_size_, memory_init_size));
        }

        ~Machine() {

        }

        void print_dump() {
            print_dump(0, memory_size_);
        }

        void print_dump(size_t start, size_t end);
        void print_status();

        bool running() {
            return !halt_;
        }
        void step();

    private:
        void instr_alu_add();
        void instr_alu_sub();
        void instr_jfc();
        void instr_jfz(); 
        void instr_jmpm();
        void instr_load_reg_immediate();
        void instr_out();

        const size_t memory_size_ = 32768;
        std::shared_ptr<uint8_t[]> memory_;

        uint8_t pc_;
        uint8_t reg_seg_;

        bool flag_c_;
        bool flag_z_;
        bool halt_;

        Opcode reg_instr_;

        uint8_t reg_a_;
        uint8_t reg_b_;
        uint16_t reg_c_;
        uint16_t reg_d_;
        uint8_t reg_o_;
    };

};
