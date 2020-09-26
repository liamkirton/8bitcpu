#pragma once

namespace cpuemu {

    // See eeproms/control.py

    enum class Register {
        A,
        B,
        C,
        DL,
        DH,
        D,
        SG
    };

    enum class Opcode {

        //
        // Basic instructions
        //

        NOP,
        HALT,

        //
        // Instructions to load a register from memory
        //

        LDAM,
        LDBM,
        LDCM,
        LDDLM,
        LDDHM,
        LDDM,
        LDSGM,

        //
        // Instructions to load a register from immediate
        //

        LDAI,
        LDBI,
        LDCI,
        LDDLI,
        LDDHI,
        LDDI,
        LDSGI,

        //
        // Instructions to store a register to memory
        //

        STAM,
        STBM,
        STCM,
        STDLM,
        STDHM,
        STDM,
        STSGM,

        //
        // Instructions to store a register to memory w/ addr in C or D
        //

        STAC,
        STBC,
        STCC,
        STDLC,
        STDHC,
        STDC,
        STSGC,

        STAD,
        STBD,
        STCD,
        STDLD,
        STDHD,
        STDD,
        STSGD,

        //
        // Instructions to move register to register
        //

        MVAA,
        MVAB,
        MVAC,
        MVADL,
        MVADH,
        MVAD,
        MVASG,

        MVBA,
        MVBB,
        MVBC,
        MVBDL,
        MVBDH,
        MVBD,
        MVBSG,

        MVCA,
        MVCB,
        MVCC,
        MVCDL,
        MVCDH,
        MVCD,
        MVCSG,

        MVDA,
        MVDB,
        MVDC,
        MVDDL,
        MVDDH,
        MVDD,
        MVDSG,

        //
        // Instructions for ALU
        //

        ADD,
        SUB,

        //
        // Instructions for Output
        //

        OUT,

        //
        // Instructions to Jmp
        //

        JMPM,

        JMPA,
        JMPB,
        JMPC,
        JMPDL,
        JMPDH,
        JMPD,
        JMPSG,

        //
        // Instructions to Jmp Conditionally
        //

        JC,
        JZ

    };
};
