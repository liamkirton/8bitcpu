#include "cpuemu.h"

void cpuemu::Machine::print_dump(size_t start, size_t end) {
    std::cout << std::hex << std::setfill('0') << std::endl;

    if (end > start) {
        start = start - start % 16;
        end = end + 16 - (end % 16);
        if (end > memory_size_) {
            end = memory_size_;
        }

        for (size_t i = start; i < end; i += 16) {
            std::cout << "[" << std::setw(4) << i << "]";
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

    std::cout
        << "[P ]: " << std::setw(2) << static_cast<uint16_t>(reg_seg_) << ":"
        << std::setw(2) << static_cast<uint16_t>(pc_) << "    "
        << "[I ]: " << std::setw(2) << static_cast<uint16_t>(reg_instr_) << "  "
        << "[FC]: " << std::setw(2) << (flag_c_ ? 1 : 0) << "  "
        << "[FZ]: " << std::setw(2) << (flag_z_ ? 1 : 0) << "  "
        << "[H ]: " << std::setw(2) << (halt_ ? 1 : 0) << std::endl
        << "[RA]: " << std::setw(2) << static_cast<uint16_t>(reg_a_) << "       "
        << "[RB]: " << std::setw(2) << static_cast<uint16_t>(reg_b_) << "  "
        << "[RC]: " << std::setw(4) << reg_c_ << "  "
        << "[RD]: " << std::setw(4) << reg_d_ << std::endl
        << "[RO]: " << std::setw(2) << static_cast<uint16_t>(reg_o_) << " ("
        << std::dec << std::setw(3) << static_cast<uint16_t>(reg_o_) << ")" << std::hex << std::endl
        << std::endl;
}

void cpuemu::Machine::print_status() {
    std::cout
        << "\r"
        << std::setfill('0')
        << "[P ]: " << std::setw(2) << static_cast<uint16_t>(reg_seg_) << ":"
        << std::setw(2) << static_cast<uint16_t>(pc_) << "  "
        << "[RO]: " << std::setw(2) << static_cast<uint16_t>(reg_o_) << " ("
        << std::dec << std::setw(3) << static_cast<uint16_t>(reg_o_) << ")" << std::hex
        << std::flush;
}

void cpuemu::Machine::step() {
    reg_instr_ = static_cast<Opcode>(memory_[static_cast<size_t>(reg_seg_) * 16 + pc_]);

    //print_dump(0, 0);
    print_status();

    switch (reg_instr_) {
    case Opcode::NOP:
        pc_++;
        break;

    case Opcode::HALT:
        halt_ = true;
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

    case Opcode::JC:
        instr_jfc();
        break;

    case Opcode::JZ:
        instr_jfz();
        break;

    default:
        halt_ = true;
        break;
    }
}

void cpuemu::Machine::instr_alu_add() {
    uint16_t sum = reg_a_ + reg_b_;
    flag_c_ = (sum & 0xff00) != 0;
    flag_z_ = sum == 0;
    reg_a_ = sum & 0xff;

    pc_++;
}

void cpuemu::Machine::instr_alu_sub() {
    /*uint16_t sum = reg_a_ + reg_b_;
    flag_c_ = (sum & 0xff00) != 0;
    flag_z_ = sum == 0;
    reg_a_ = sum & 0xff;*/

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
    uint8_t dest = memory_[static_cast<size_t>(reg_seg_) * 16 + (pc_ + 1)];
    pc_ = dest;
    reg_seg_ = 0;
}

void cpuemu::Machine::instr_load_reg_immediate() {
    Register target = static_cast<Register>(static_cast<uint16_t>(reg_instr_) - static_cast<uint16_t>(Opcode::LDAI));
    uint8_t immediate = memory_[static_cast<size_t>(reg_seg_) * 16 + (pc_ + 1)];

    switch (target) {
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

void cpuemu::Machine::instr_out() {
    reg_d_ = reg_d_ & 0xff00 | reg_a_;
    reg_o_ = reg_d_ & 0xff;
    pc_++;
}
