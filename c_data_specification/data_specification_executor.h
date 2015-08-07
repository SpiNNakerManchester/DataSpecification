/*! \file
 *
 *  \brief DSE Helper Functions Header File
 *
 *  DESCRIPTION
 *      Defines functions used by the Data Specification Executor to execute
 *      the data specification.
 */
#ifndef _DATA_SPECIFICATION_EXECUTOR_FUNCTIONS
#define _DATA_SPECIFICATION_EXECUTOR_FUNCTIONS

#include "constants.h"
#include "commands.h"
#include <stdint.h>
#include <spinnaker.h>
#include <data_specification.h>
#include <spin1_api.h>
#include <debug.h>

// Stores the details of a command.
struct Command {
    enum OpCode opCode;
    uint8_t dataLength;
    uint8_t fieldUsage;
    uint32_t cmdWord;
    uint32_t dataWords[3];
};

struct MemoryRegion {
    uint8_t* start_address;
    int size;
    int unfilled;
    int free;
    uint8_t* write_pointer;
};

struct Constructor {
    address_t start_address;
    int arg_count;
    uint8_t arg_read_only;
};

void data_specification_executor(address_t, uint32_t);

#endif

