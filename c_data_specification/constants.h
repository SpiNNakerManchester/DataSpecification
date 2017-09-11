/*! \file constants.h
 *  \brief Define some constants used by the DSE.
 */
#ifndef _DATA_SPECIFICATION_CONSTANTS
#define _DATA_SPECIFICATION_CONSTANTS

// The address of the data sequence.
#define DS_ADDRESS		0x60000000

// MAGIC Numbers:
// ==============
// Data spec magic number
#define DSG_MAGIC_NUM		0x5B7CA17E

// Application datafile magic number
#define APPDATA_MAGIC_NUM	0xAD130AD6

// Version of the file produced by the DSE
#define DSE_VERSION		0x00010000

// =============

// The number of registers.
#define MAX_REGISTERS		16

// The number of memory regions.
#define MAX_MEM_REGIONS		16

// The size of the pointer table, computed from the number of memory regions.
#define POINTER_TABLE_SIZE	MAX_MEM_REGIONS
#define POINTER_TABLE_SIZE_BYTES  POINTER_TABLE_SIZE * 4

// The start address of the header table.
#define HEADER_START_ADDRESS	SDRAM_TOP

// The start address of the pointer table.
#define POINTER_TABLE_START_ADDRESS  \
    (HEADER_START_ADDRESS + APP_PTR_TABLE_HEADER_BYTE_SIZE)

#define HEADER_SIZE		2
#define HEADER_SIZE_BYTES	(HEADER_SIZE * 4)

// The start address of the stack.
#define STACK_START_ADDRESS \
    (POINTER_TABLE_START_ADDRESS + POINTER_TABLE_SIZE)


#define MAX_STRUCTS		32
#define MAX_CONSTRUCTORS	15
#define MAX_STRUCT_ARGS		5

#define PRINT_TEXT_MAX_CHARACTERS  11

#endif
