#pragma once

namespace cpuemu {

    class Machine {
    public:
        Machine() : 
                output_level_{ 1 },
                memory_(new uint8_t[memory_size_]),
                memory_limit_{ 0 },
                step_{ 0 },
                pc_{ 0 }, reg_seg_{ 0 },
                flag_c_(false), flag_z_(false), error_(false), halt_(false),
                reg_a_{ 0 }, reg_b_{ 0 }, reg_c_{ 0 }, reg_d_{ 0 }, reg_o_{ 0 } {
            std::memset(memory_.get(), 0, memory_size_);
        }

        Machine(std::shared_ptr<uint8_t[]> memory_init, size_t memory_init_size) : Machine() {
            memory_limit_ = std::min(memory_size_, memory_init_size); 
            std::memcpy(memory_.get(), memory_init.get(), memory_limit_);
        }

        ~Machine() {

        }

        void set_output(uint8_t output_level) {
            if (output_level > 4) {
                output_level = 4;
            }
            output_level_ = output_level;
        }

        bool running() {
            return !halt_;
        }

        void step();

    private:
        void print();
        void print_dump(size_t start, size_t end);
        void print_status();

        void instr_alu_add();
        void instr_alu_sub();
        void instr_jfc();
        void instr_jfz(); 
        void instr_jmpm();
        void instr_jmpm_indirect();
        void instr_load_reg_immediate();
        void instr_load_reg_memory();
        void instr_move_reg_reg();
        void instr_out();
        void instr_store_reg_memory();
        void instr_store_reg_memory_indirect();

        uint8_t output_level_;

        const size_t memory_size_ = 32768;
        std::shared_ptr<uint8_t[]> memory_;
        size_t memory_limit_;

        uint32_t step_;

        uint8_t pc_;
        uint8_t reg_seg_;

        bool flag_c_;
        bool flag_z_;
        bool error_;
        bool halt_;

        Opcode reg_instr_;

        uint8_t reg_a_;
        uint8_t reg_b_;
        uint16_t reg_c_;
        uint16_t reg_d_;
        uint8_t reg_o_;
    };

};
