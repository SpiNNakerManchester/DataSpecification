/*! \file commands.h
 *  \brief Define the supported commands.
 */

#ifndef _DATA_SPECIFICATION_COMMANDS
#define _DATA_SPECIFICATION_COMMANDS

//! The op-codes of the supported commands.
enum OpCode {
    BREAK                 = 0x00,
    NOP                   = 0x01,
    RESERVE               = 0x02,
    FREE                  = 0x03,
    DECLARE_RNG           = 0x05,
    DECLARE_RANDOM_DIST   = 0x06,
    GET_RANDOM_NUMBER     = 0x07,
    START_STRUCT          = 0x10,
    STRUCT_ELEM           = 0x11,
    END_STRUCT            = 0x12,
    START_PACKSPEC        = 0x1A,
    PACK_PARAM            = 0x1B,
    END_PACKSPEC          = 0x1C,
    START_CONSTRUCTOR     = 0x20,
    END_CONSTRUCTOR       = 0x25,
    CONSTRUCT             = 0x40,
    READ                  = 0x41,
    WRITE                 = 0x42,
    WRITE_ARRAY           = 0x43,
    WRITE_STRUCT          = 0x44,
    BLOCK_COPY            = 0x45,
    SWITCH_FOCUS          = 0x50,
    LOOP                  = 0x51,
    BREAK_LOOP            = 0x52,
    END_LOOP              = 0x53,
    IF                    = 0x55,
    ELSE                  = 0x56,
    END_IF                = 0x57,
    MV                    = 0x60,
    GET_WR_PTR            = 0x63,
    SET_WR_PTR            = 0x64,
    RESET_WR_PTR          = 0x65,
    ALIGN_WR_PTR          = 0x66,
    ARITH_OP              = 0x67,
    LOGIC_OP              = 0x68,
    REFORMAT              = 0x6A,
    COPY_STRUCT           = 0x70,
    COPY_PARAM            = 0x71,
    WRITE_PARAM           = 0x72,
    READ_PARAM            = 0x73,
    WRITE_PARAM_COMPONENT = 0x74,
    PRINT_VAL             = 0x80,
    PRINT_TXT             = 0x81,
    PRINT_STRUCT          = 0x82,
    END_SPEC              = 0xFF
};

#endif
