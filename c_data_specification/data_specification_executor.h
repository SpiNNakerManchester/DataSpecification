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
#include "system_api.h"

// Stores the details of a command.
typedef struct Command {
    OpCode opCode;
    uint8_t dataLength;
    uint32_t cmdWord;
    uint32_t dataWords[3];
} Command;

typedef struct MemoryRegion {
    uint8_t* start_address;
    uint32_t size;
    uint32_t unfilled;
    uint8_t* write_pointer;
} MemoryRegion;

typedef struct Constructor {
    address_t start_address;
    int arg_count;
    uint8_t arg_read_only;
} Constructor;

typedef struct dse_data {
    address_t execRegion;
    uint32_t currentBlock_size;
    uint32_t future_app_id;
    uint32_t generate_report;
} dse_data;

extern uint8_t	current_app_id;
extern uint8_t	future_app_id;
extern uint32_t	current_sark_xalloc_flags;
extern uint32_t	future_sark_xalloc_flags;

// The tag to give to memory regions reserved
#define TAG 0x00

void data_specification_executor(address_t, uint32_t);

#endif
