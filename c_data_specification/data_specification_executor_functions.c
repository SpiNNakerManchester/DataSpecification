/*! \file data_specification_executor_functions.c
 *  \brief Functions to execute the commands in the data sequence.
 */
#include "data_specification_executor_functions.h"

// Load external variables defined in data_specification_executor.c
extern address_t command_pointer;
extern uint32_t registers[MAX_REGISTERS];
extern int current_region;
extern void *stack_pointer;
extern struct MemoryRegion *memory_regions[MAX_MEM_REGIONS];

uint8_t command_get_length(uint32_t command) {
    return (command & 0x30000000) >> 28;
}

enum OpCode command_get_opcode(uint32_t command) {
    return (command & 0x0FF00000) >> 20;
}

//! \brief Private function to find the field usage of a command.
//! \param[in] The command word (the first word of a command).
//! \return The command's field usage, 3 one-hot encoded bits at the end of the
//!         returned byte.
uint8_t _command_get_fieldUsage(uint32_t command) {
    return (command & 0x00070000) >> 16;
}

uint8_t command_get_destReg(uint32_t command) {
    return (command & 0x0000F000) >> 12;
}

uint8_t command_get_src1Reg(uint32_t command) {
    return (command & 0x00000F00) >> 8;
}

uint8_t command_get_src2Reg(uint32_t command) {
    return (command & 0x000000F0) >> 4;
}

int command_dest_in_use(uint32_t command) {
    return _command_get_fieldUsage(command) & 0x4;
}

int command_src1_in_use(uint32_t command) {
    return _command_get_fieldUsage(command) & 0x2;
}

int command_src2_in_use(uint32_t command) {
    return _command_get_fieldUsage(command) & 0x1;
}

int execute_reserve(struct Command cmd) {

    if (cmd.dataLength != 1) {
        log_error("Data specification RESERVE requires one word as argument");
        return -1;
    }

    int region = cmd.cmdWord & 0x1F;

    if (memory_regions[region] != NULL) {
        log_error("Data specification RESERVE region %d already in use",
                  region);
        return -1;
    }

    // TODO: be careful with the memory map.
    if ((int)(stack_pointer - cmd.dataWords[0]) < SDRAM_BASE) {
        log_error("Data specification RESERVE unable to allocate memory:
                   SDRAM is full");
        return -1;
    }

    memory_regions[region] = sark_alloc(1, sizeof(struct MemoryRegion));

    if (memory_regions[region] == NULL) {
        log_error("Data specification RESERVE unable to allocate memory:
                   DTCM is full");
        return -1;
    }

    memory_regions[region]->size           = cmd.dataWords[0];
    memory_regions[region]->startAddress   = stack_pointer
                                             - memory_regions[region]->size;
    memory_regions[region]->currentAddress = stack_pointer
                                             - memory_regions[region]->size;
    memory_regions[region]->unfilled       = (cmd.cmdWord >> 7) & 0x1;

    stack_pointer -= cmd.dataWords[0];

    return 0;
}

//! \brief Private function to write a value to the specified memory location.
//!        The caller must ensure the selected memory region is valid.
//! \param[in] value Pointer to the data to be written.
//! \param[in] size The size in bytes of the data to be written.
//                  The supported sizes are 1, 2, 4 and 8 bytes.
void write_value(void *value, int size) {
    if (size == 1)
        *(memory_regions[current_region]->currentAddress++) =
                                                        *((uint8_t*)value);
    else if (size == 2)
        *(memory_regions[current_region]->currentAddress++) =
                                                        *((uint16_t*)value);
    else if (size == 4)
        *(memory_regions[current_region]->currentAddress++) =
                                                        *((uint32_t*)value);
    else if (size == 8)
        *(memory_regions[current_region]->currentAddress++) =
                                                        *((uint64_t*)value);
    else
        log_error("Data specification WRITE unsupported data size");
}

int execute_write(struct Command cmd) {

    // The number of repetitions.
    int n_repeats;

    // If the source2 register is in use, it specifies the number or
    // repetitions.
    // Otherwise, the number of repetitions is stored into the last significant
    // byte.
    if (command_src2_in_use(cmd.cmdWord))
        n_repeats = command_get_src2Reg(cmd.cmdWord);
    else {
        n_repeats = cmd.cmdWord & 0xFF;
    }

    // The length of the data (bits 13:12).
    int data_len = (cmd.cmdWord >> 12) & 0x3;
    switch (data_len) {
        case 0x00:
            data_len = 1;
            break;
        case 0x01:
            data_len = 2;
            break;
        case 0x10:
            data_len = 4;
            break;
        case 0x11:
            data_len = 8;
            break;
    }

    // The value of the data to be written.
    uint64_t data_val;
    if (command_src1_in_use(cmd.cmdWord) && cmd.dataLength == 0) {
        data_val = registers[command_get_src1Reg(cmd.cmdWord)];
    } else if (cmd.dataLength == 1 && data_len != 8) {
        data_val = cmd.dataWords[0];
    } else if (cmd.dataLength == 2 && data_len == 8) {
        data_val = ((uint64_t)cmd.dataWords[0] << 32) | cmd.dataWords[1];
    } else {
        log_error("Data specification WRITE format error");
    }

    // Perform some checks and, if everything is fine, write the data n_repeats
    // times.
    if (current_region == -1) {
        log_error("Data specification WRITE the current memory region has not "
                  "been selected");
        return -1;
    } else if (memory_regions[current_region] == NULL) {
        log_error("Data specification WRITE the current memory region has not "
                  "been allocated");
        return -1;
    } else if (memory_regions[current_region]->size - data_len < 0) {
        log_error("Data specification WRITE the current memory region is full");
        return -1;
    } else {
        for (int count = 0; count < n_repeats; count++) {
            write_value(&data_val, data_len);
        }
    }

    return 0;
}

int execute_write_array(struct Command cmd) {

    // The length of the array is specified in the second word of the command.
    int length = cmd.dataWords[0];

    // Perform some checks and, if everything is fine, write the array to
    // memory.
    if (current_region == -1) {
        log_error("Data specification WRITE the current memory region has not been selected");
        return -1;
    } else if (memory_regions[current_region] == NULL) {
        log_error("Data specification WRITE the current memory region has not been allocated");
        return -1;
    } else if (memory_regions[current_region]->size - length * 4 < 0) {
        log_error("Data specification WRITE the current memory region is full");
        return -1;
    } else {
        for (int count = 0; count < length; count++) {
            write_value(command_pointer++, 4);
        }
    }
}

int execute_switch_focus(struct Command cmd) {

    // The region to be selected.
    int region;

    // Get the region to be selected from the command or from a register.
    if (command_src1_in_use(cmd.cmdWord))
        region = registers[command_get_src1Reg(cmd.cmdWord)];
    else
        region = (cmd.cmdWord >> 8) & 0xF;

    // Perform some checks and, if everything is fine, change the value of
    // current_region.
    if (memory_regions[region] == NULL) {
        log_error("Data specification SWITCH_FOCUS Unallocated memory region");
        return -1;
    } else {
        current_region = region;
    }

    return 0;
}

