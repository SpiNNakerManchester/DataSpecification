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

#ifdef EMULATE
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
typedef uint32_t* address_t;
#define spin1_exit(code) exit(code)
#define spin1_memcpy(destination, source, size) memcpy((destination), (source), (size))
#define rt_error(error_code) exit((error_code))
#define RTE_ABORT -1
#define log_info(message, ...) printf("[INFO]    ", message, ##__VA_ARGS__)
#define log_error(message, ...) printf("[ERROR]    ", message, ##__VA_ARGS__)
#define log_debug(message, ...) printf("[DEBUG]    ", message, ##__VA_ARGS__)
#define sark_xalloc(heap, size, tag, flag) malloc((size))
#define sark_alloc(count, size) malloc((count) * (size))
#define sark_xfree(heap, ptr, flag) free((ptr))
#define sark_free(ptr) free((ptr))
#endif


#ifndef EMULATE
#include <spin1_api.h>
#include <debug.h>
#include <spinnaker.h>
#include <data_specification.h>
#endif

// Stores the details of a command.
struct Command {
    enum OpCode opCode;
    uint8_t dataLength;
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

