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
#define spin1_exit(code) return (code);
#define spin1_memcpy(destination, source, size)\
    memcpy((destination), (source), (size))
#define rt_error(error_code) exit((error_code))
#define RTE_ABORT -1
#define log_info(message, ...) printf("[INFO] " message "\n", ##__VA_ARGS__)
#define log_warning(message, ...) \
    printf("[WARNING] " message "\n", ##__VA_ARGS__)
#define log_error(message, ...) printf("[ERROR] " message "\n", ##__VA_ARGS__)
#define log_debug(message, ...) printf("[DEBUG] " message "\n", ##__VA_ARGS__)
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
typedef struct {
    enum OpCode opCode;
    uint8_t dataLength;
    uint32_t cmdWord;
    uint32_t dataWords[3];
} Command;

typedef struct {
    uint8_t* start_address;
    uint32_t size;
    uint32_t unfilled;
    uint8_t* write_pointer;
} MemoryRegion;


typedef struct {
    address_t start_address;
    int arg_count;
    uint8_t arg_read_only;
} Constructor;

typedef struct {
    address_t execRegion;
    uint32_t currentBlock_size;
    uint32_t future_app_id;
    uint32_t generate_report;
} dse_data;

extern uint8_t current_app_id;
extern uint8_t future_app_id;
extern uint32_t current_sark_xalloc_flags;
extern uint32_t future_sark_xalloc_flags;

// The tag to give to memory regions reserved
#define TAG 0x00

void data_specification_executor(address_t, uint32_t);

#endif
