/*! \file constants.h
 *  \brief Define some constants used by the DSE.
 */
#ifndef _DATA_SPECIFICATION_CONSTANTS
#define _DATA_SPECIFICATION_CONSTANTS

// The address of the data sequence.
#define DS_ADDRESS              0x60000000

// MAGIC Numbers:
#define DSG_MAGIC_NUM                  0x5B7CA17E  // Data spec magic number
#define APPDATA_MAGIC_NUM              0xAD130AD6  // Application datafile magic number
#define DSE_VERSION                    0x00010000  // Version of the file produced by the DSE

// The number of registers.
#define MAX_REGISTERS                  16

// The number of memory regions.
#define MAX_MEM_REGIONS                16

// The size of the pointer table, computed from the number of memory regions.
#define POINTER_TABLE_SIZE             4 * MAX_MEM_REGIONS

// The start address of the header table.
#define HEADER_START_ADDRESS           SDRAM_TOP

// The start address of the pointer table.
#define POINTER_TABLE_START_ADDRESS    HEADER_START_ADDRESS +  APP_PTR_TABLE_HEADER_BYTE_SIZE

#define HEADER_SIZE 2

// The start address of the stack.
#define STACK_START_ADDRESS            POINTER_TABLE_START_ADDRESS + POINTER_TABLE_SIZE


#define MAX_STRUCTS 32
#define MAX_CONSTRUCTORS 15
#define MAX_STRUCT_ARGS 5

#define PRINT_TEXT_MAX_CHARACTERS 11

// The states of a core.
//   READY_TO_RECEIVE - The core can receive new information about a data
//                      block.
//   WAITING_FOR_DATA - The core has allocated memory for the new block and
//                      waits for its content.
//   CORE_BUSY        - The core cannot receive any packets.
enum Core_states {
    READY_TO_RECEIVE = 1,
    WAITING_FOR_DATA = 2,
    CORE_BUSY = 3
};


#endif

