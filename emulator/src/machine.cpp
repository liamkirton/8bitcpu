#include "cpuemu.h"

void cpuemu::Machine::print() {
    if ((output_level_ == 4) || ((output_level_ == 3) && halt_) || error_) {
        print_dump(0, memory_limit_);
    }
    else if ((output_level_ >= 2) || ((output_level_ == 1) && (step_ % 100 == 0)) || halt_) {
        print_status();
    }
}

void cpuemu::Machine::print_dump(size_t start, size_t end) {
    std::cout << std::hex << std::setfill('0') << std::endl;

    std::cout
        << "[" << std::setw(8) << step_ << "]  "
        << "[P ]: " << std::setw(2) << static_cast<uint16_t>(reg_seg_) << ":"
        << std::setw(2) << static_cast<uint16_t>(pc_) << "    "
        << "[I ]: " << std::setw(2) << static_cast<uint16_t>(reg_instr_) << "  "
        << "[FC]: " << std::setw(2) << (flag_c_ ? 1 : 0) << "  "
        << "[FZ]: " << std::setw(2) << (flag_z_ ? 1 : 0) << "  "
        << "[H ]: " << std::setw(2) << (halt_ ? 1 : 0) << std::endl
        << "            [RA]: " << std::setw(2) << static_cast<uint16_t>(reg_a_) << "       "
        << "[RB]: " << std::setw(2) << static_cast<uint16_t>(reg_b_) << "  "
        << "[RC]: " << std::setw(4) << reg_c_ << "  "
        << "[RD]: " << std::setw(4) << reg_d_ << std::endl
        << "            [RO]: " << std::setw(2) << static_cast<uint16_t>(reg_o_) << " ("
        << std::dec << std::setw(3) << static_cast<uint16_t>(reg_o_) << ")" << std::hex << std::endl
        << std::endl;

    if (end > start) {
        start = start - start % 16;
        end = end + 16 - (end % 16);
        if (end > memory_size_) {
            end = memory_size_;
        }

        for (size_t i = start; i < end; i += 16) {
            std::cout << "    [" << std::setw(4) << i << "]";
            for (size_t j = 0; j < 16; ++j) {
                std::cout << " " << std::setw(2) << static_cast<uint16_t>(memory_[i + j]);
            }
            std::cout << "    ";
            for (size_t j = 0; j < 16; ++j) {
                char c = static_cast<char>(memory_[i + j]);
                std::cout << (((c >= 0x20) && (c < 0x7f)) ? c : '.');
            }
            std::cout << std::endl;
        }

        std::cout << std::endl;
    }
}

void cpuemu::Machine::print_status() {
    std::cout
        << "\r"
        << std::setfill('0')
        << "[" << std::setw(8) << step_ << "]  "
        << "[P ]: " << std::setw(2) << static_cast<uint16_t>(reg_seg_) << ":"
        << std::setw(2) << static_cast<uint16_t>(pc_) << "  "
        << "[I ]: " << std::setw(2) << static_cast<uint16_t>(reg_instr_) << "  "
        << "[RO]: " << std::setw(2) << static_cast<uint16_t>(reg_o_) << " ("
        << std::dec << std::setw(3) << static_cast<uint16_t>(reg_o_) << ")" << std::hex
        << std::flush;
}

void cpuemu::Machine::step() {
    reg_instr_ = static_cast<Opcode>(memory_[static_cast<size_t>(reg_seg_) * 16 + pc_]);

    print();

    switch (reg_instr_) {
    case Opcode::NOP:
        pc_++;
        break;

    case Opcode::HALT:
        halt_ = true;
        print();
        break;

    case Opcode::LDAM:
    case Opcode::LDBM:
    case Opcode::LDCM:
    case Opcode::LDDLM:
    case Opcode::LDDHM:
    case Opcode::LDDM:
    case Opcode::LDSGM:
        instr_load_reg_memory();
        break;

    case Opcode::LDAI:
    case Opcode::LDBI:
    case Opcode::LDCI:
    case Opcode::LDDLI:
    case Opcode::LDDHI:
    case Opcode::LDDI:
    case Opcode::LDSGI:
        instr_load_reg_immediate();
        break;

    case Opcode::STAM:
    case Opcode::STBM:
    case Opcode::STCM:
    case Opcode::STDLM:
    case Opcode::STDHM:
    case Opcode::STDM:
    case Opcode::STSGM:
        instr_store_reg_memory();
        break;

    case Opcode::STAC:
    case Opcode::STBC:
    case Opcode::STCC:
    case Opcode::STDLC:
    case Opcode::STDHC:
    case Opcode::STDC:
    case Opcode::STSGC:
    case Opcode::STAD:
    case Opcode::STBD:
    case Opcode::STCD:
    case Opcode::STDLD:
    case Opcode::STDHD:
    case Opcode::STDD:
    case Opcode::STSGD:
        instr_store_reg_memory_indirect();
        break;

    case Opcode::MVAA:
    case Opcode::MVAB:
    case Opcode::MVAC:
    case Opcode::MVADL:
    case Opcode::MVADH:
    case Opcode::MVAD:
    case Opcode::MVASG:
    case Opcode::MVBA:
    case Opcode::MVBB:
    case Opcode::MVBC:
    case Opcode::MVBDL:
    case Opcode::MVBDH:
    case Opcode::MVBD:
    case Opcode::MVBSG:
    case Opcode::MVCA:
    case Opcode::MVCB:
    case Opcode::MVCC:
    case Opcode::MVCDL:
    case Opcode::MVCDH:
    case Opcode::MVCD:
    case Opcode::MVCSG:
    case Opcode::MVDA:
    case Opcode::MVDB:
    case Opcode::MVDC:
    case Opcode::MVDDL:
    case Opcode::MVDDH:
    case Opcode::MVDD:
    case Opcode::MVDSG:
        instr_move_reg_reg();
        break;

    case Opcode::ADD:
        instr_alu_add();
        break;

    case Opcode::SUB:
        instr_alu_sub();
        break;

    case Opcode::OUT:
        instr_out();
        break;

    case Opcode::JMPM:
        instr_jmpm();
        break;

    case Opcode::JMPA:
    case Opcode::JMPB:
    case Opcode::JMPC:
    case Opcode::JMPDL:
    case Opcode::JMPDH:
    case Opcode::JMPD:
    case Opcode::JMPSG:
        instr_jmpm_indirect();
        break;

    case Opcode::JC:
        instr_jfc();
        break;

    case Opcode::JZ:
        instr_jfz();
        break;

    default:
        error_ = halt_ = true;
        print();
        break;
    }

    step_++;
}

void cpuemu::Machine::instr_alu_add() {
    uint16_t sum = reg_a_ + reg_b_;
    flag_c_ = (sum & 0xff00) != 0;
    flag_z_ = sum == 0;
    reg_a_ = sum & 0xff;

    pc_++;
}

void cpuemu::Machine::instr_alu_sub() {
    uint16_t sum = reg_a_ - reg_b_;
    flag_c_ = (sum & 0xff00) == 0;
    flag_z_ = sum == 0;
    reg_a_ = sum & 0xff;

    pc_++;
}

void cpuemu::Machine::instr_jfc() {
    if (flag_c_) {
        uint8_t dest = memory_[static_cast<size_t>(reg_seg_) * 16 + (pc_ + 1)];
        pc_ = dest;
        reg_seg_ = 0;
    }
    else {
        pc_ += 2;
    }
}

void cpuemu::Machine::instr_jfz() {
    if (flag_z_) {
        uint8_t dest = memory_[static_cast<size_t>(reg_seg_) * 16 + (pc_ + 1)];
        pc_ = dest;
        reg_seg_ = 0;
    }
    else {
        pc_ += 2;
    }
}

void cpuemu::Machine::instr_jmpm() {
    uint8_t addr = memory_[static_cast<size_t>(reg_seg_) * 16 + (pc_ + 1)];
    if (addr > memory_limit_) {
        memory_limit_ = addr;
    }
    pc_ = addr;
    reg_seg_ = 0;
}

void cpuemu::Machine::instr_jmpm_indirect() {
    Register dst = static_cast<Register>(static_cast<uint16_t>(reg_instr_) - static_cast<uint16_t>(Opcode::LDAI));
    uint16_t addr = 0;

    switch (dst) {
    case Register::A:
        addr = reg_a_;
        break;
    case Register::B:
        addr = reg_b_;
        break;
    case Register::C:
        addr = reg_c_ & 0xff;
        break;
    case Register::DL:
        addr = reg_d_ & 0xff;
        break;
    case Register::DH:
        break;
    case Register::D:
        addr = reg_d_;
        break;
    case Register::SG:
        break;
    }

    if (addr > memory_limit_) {
        memory_limit_ = addr;
    }

    pc_ = addr & 0xff;
    reg_seg_ = (addr & 0xff00) >> 8;
}

void cpuemu::Machine::instr_load_reg_immediate() {
    Register dst = static_cast<Register>(static_cast<uint16_t>(reg_instr_) - static_cast<uint16_t>(Opcode::LDAI));
    uint8_t immediate = memory_[static_cast<size_t>(reg_seg_) * 16 + (pc_ + 1)];

    switch (dst) {
    case Register::A:
        reg_a_ = immediate;
        break;
    case Register::B:
        reg_b_ = immediate;
        break;
    case Register::C:
        reg_c_ = immediate;
        break;
    case Register::DL:
    case Register::D:
        reg_d_ = reg_d_ & 0xff00 | immediate;
        break;
    case Register::DH:
        reg_d_ = immediate << 8 | reg_d_ & 0xff;
        break;
    case Register::SG:
        reg_seg_ = immediate;
        break;
    }

    pc_ += 2;
}

void cpuemu::Machine::instr_load_reg_memory() {
    Register dst = static_cast<Register>(static_cast<uint16_t>(reg_instr_) - static_cast<uint16_t>(Opcode::LDAM));
    uint8_t addr = memory_[static_cast<size_t>(reg_seg_) * 16 + (pc_ + 1)];
    uint8_t value = memory_[addr];

    if (addr > memory_limit_) {
        memory_limit_ = addr;
    }

    switch (dst) {
    case Register::A:
        reg_a_ = value;
        break;
    case Register::B:
        reg_b_ = value;
        break;
    case Register::C:
        reg_c_ = value;
        break;
    case Register::DL:
    case Register::D:
        reg_d_ = reg_d_ & 0xff00 | value;
        break;
    case Register::DH:
        reg_d_ = value << 8 | reg_d_ & 0xff;
        break;
    case Register::SG:
        reg_seg_ = value;
        break;
    }

    pc_ += 2;
}

void cpuemu::Machine::instr_move_reg_reg() {
    Register src = static_cast<Register>((static_cast<uint16_t>(reg_instr_) - static_cast<uint16_t>(Opcode::MVAA)) / 7);
    Register dst = static_cast<Register>((static_cast<uint16_t>(reg_instr_) - static_cast<uint16_t>(Opcode::MVAA)) % 7);

    if (src >= Register::DL) {
        src = Register::D;
    }

    uint16_t src_val = 0;

    switch (src) {
    case Register::A:
        src_val = reg_a_;
        break;
    case Register::B:
        src_val = reg_b_;
        break;
    case Register::C:
        src_val = reg_c_;
        break;
    case Register::D:
        src_val = reg_d_;
        break;
    }

    switch (dst) {
    case Register::A:
        reg_a_ = src_val & 0xff;
        break;
    case Register::B:
        reg_b_ = src_val & 0xff;
        break;
    case Register::C:
        reg_c_ = src_val;
        break;
    case Register::DL:
        reg_d_ = reg_d_ & 0xff00 | src_val & 0xff;
        break;
    case Register::DH:
        reg_d_ = ((src_val & 0xff) << 8) | reg_d_ & 0xff;
        break;
    case Register::D:
        reg_d_ = src_val;
        break;
    case Register::SG:
        reg_seg_ = src_val & 0xff;
        break;
    }

    pc_++;
}

void cpuemu::Machine::instr_out() {
    reg_d_ = reg_d_ & 0xff00 | reg_a_;
    reg_o_ = reg_d_ & 0xff;
    pc_++;
}

void cpuemu::Machine::instr_store_reg_memory() {
    Register dst = static_cast<Register>(static_cast<uint16_t>(reg_instr_) - static_cast<uint16_t>(Opcode::STAM));
    uint8_t addr = memory_[static_cast<size_t>(reg_seg_) * 16 + (pc_ + 1)];

    if (addr > memory_limit_) {
        memory_limit_ = addr;
    }

    uint8_t value = 0;

    switch (dst) {
    case Register::A:
        value = reg_a_;
        break;
    case Register::B:
        value = reg_b_;
        break;
    case Register::C:
        value = reg_c_ & 0xff;
        break;
    case Register::DL:
    case Register::D:
        value = reg_d_ & 0xff;
        break;
    case Register::DH:
        break;
    case Register::SG:
        break;
    }

    memory_[addr] = value;

    pc_ += 2;
}

void cpuemu::Machine::instr_store_reg_memory_indirect() {
    Register src = static_cast<Register>((static_cast<uint16_t>(reg_instr_) - static_cast<uint16_t>(Opcode::MVAA)) % 7);
    Register dst = static_cast<Register>((static_cast<uint16_t>(reg_instr_) - static_cast<uint16_t>(Opcode::MVAA)) / 7);

    uint16_t addr = 0;
    uint8_t value = 0;

    switch (src) {
    case Register::A:
        value = reg_a_;
        break;
    case Register::B:
        value = reg_b_;
        break;
    case Register::C:
        value = reg_c_ & 0xff;
        break;
    case Register::DL:
    case Register::D:
        value = reg_d_ & 0xff;
        break;
    case Register::DH:
        break;
    case Register::SG:
        break;
    }

    switch (dst) {
    case Register::C:
        addr = reg_c_;
        break;
    case Register::D:
        addr = reg_d_;
        break;
    }

    if (addr > memory_limit_) {
        memory_limit_ = addr;
    }

    memory_[addr] = value;

    pc_++;
}
