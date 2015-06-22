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
    address_t startAddress;
    int size;
    int unfilled;
    int free;
    address_t currentAddress;
};




//! \brief Find the length of a command (bits 29:28).
//! \param[in] The command word (the first word of a command).
//! \return The length of the command (integer from 0 to 3, as stated in the
//!         data spec documentation.
uint8_t command_get_length(uint32_t command);

//! \brief Find the operation code of a command (bits 27:20).
//! \param[in] The command word (the first word of a command).
//! \return The command's opcode.
enum OpCode command_get_opcode(uint32_t command);

//! \brief Find the destination register used by a command.
//! \param[in] The command word (the first word of a command).
//! \return The register used as destination by the given command.
uint8_t command_get_destReg(uint32_t command);


//! \brief Find the source1 register used by a command.
//! \param[in] The command word (the first word of a command).
//! \return The register used as source1 by the given command.
uint8_t command_get_src1Reg(uint32_t command);


//! \brief Find the source2 register used by a command.
//! \param[in] The command word (the first word of a command).
//! \return The register used as source2 by the given command.
uint8_t command_get_src2Reg(uint32_t command);


//! \brief Check if the destination register is used by a command.
//! \param[in] The command word (the first word of a command).
//! \return 1 if the destination register is used by the given command,
//!         0 otherwise.
int command_dest_in_use(uint32_t command);

//! \brief Check if the source1 register is used by a command.
//! \param[in] The command word (the first word of a command).
//! \return 1 if the source1 register is used by the given command,
//!         0 otherwise.
int command_src1_in_use(uint32_t command);

//! \brief Check if the source2 register is used by a command.
//! \param[in] The command word (the first word of a command).
//! \return 1 if the source2 register is used by the given command,
//!         0 otherwise.
int command_src2_in_use(uint32_t command);


//! \brief Execute a reserve memory command.
//! \param[in] The command to be executed.
//! \return 0 on success, other value on failure.
int execute_reserve(struct Command cmd);

//! \brief Execute a WRITE command, which writes 1, 2, 4 or 8 byte data from a
//!        parameter to memory, with the possibility of data to be repeated.
//! \param[in] cmd The command to be executed.
//! \return 0 on success, other value on failure.
int execute_write(struct Command cmd);

//! \brief Execute a WRITE_ARRAY command, which writes an array of 32 bit words
//!        to memory.
//! \param[in] cmd The command to be executed.
//! \return 0 on success, other value on failure.
int execute_write_array(struct Command cmd);

//! \brief Execute a SWITCH_FOCUS command, which changes the selected memory
//!        region.
//! \param[in] cmd The command to be executed.
//! \return 0 on success, other value on failure.
int execute_switch_focus(struct Command cmd);

#endif
