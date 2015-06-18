#include "commands.h"
#include "constants.h"
#include <stdint.h>
#include <sark.h>
#include <debug.h>
#include <spinnaker.h>

// Stores the details of a command.
struct Command {
    enum OpCode opCode;
    uint8_t dataLength;
    uint8_t fieldUsage;
    uint32_t cmdWord;
    uint32_t dataWords[3];
};

uint8_t get_command_length(uint32_t command) {
    return (command & 0x30000000) >> 28;
}

uint8_t get_command_opcode(uint32_t command) {
    return (command & 0x0FF00000) >> 20;
}

uint8_t get_command_fieldUsage(uint32_t command) {
    return (command & 0x00070000) >> 16;
}

uint8_t get_command_destReg(uint32_t command) {
    return (command & 0x0000F000) >> 12;
}

uint8_t get_command_src1Reg(uint32_t command) {
    return (command & 0x00000F00) >> 8;
}

uint8_t get_command_src2Reg(uint32_t command) {
    return (command & 0x000000F0) >> 4;
}

int command_dest_in_use(uint32_t command) {
    return get_command_fieldUsage(command) & 0x4;
}

int command_src1_in_use(uint32_t command) {
    return get_command_fieldUsage(command) & 0x2;
}

int command_src2_in_use(uint32_t command) {
    return get_command_fieldUsage(command) & 0x1;
}

// Returns a Commmand object storing the command pointed at by the command
// pointer and updates its value to point to the next command.
struct Command get_next_command(uint32_t **command_pointer) {

    // The command object.
    struct Command cmd;

    // Get the command word (the first word of the command).
    uint32_t cmd_word = **command_pointer;
    (*command_pointer)++;

    // Get the command fields.
    cmd.dataLength     = get_command_length(cmd_word);
    cmd.opCode         = get_command_opcode(cmd_word);
    cmd.fieldUsage     = get_command_fieldUsage(cmd_word);
    cmd.cmdWord        = cmd_word;

    // Get the data words.
    for (int index = 0; index < cmd.dataLength; index++, (*command_pointer)++)
        cmd.dataWords[index] = **command_pointer;
    log_info("Read %x opcode %x", cmd_word, cmd.opCode);

    return cmd;
}

struct MemoryRegion {
    void *startAddress;
    int size;
    int unfilled;
    int free;
    uint8_t *currentAddress;
};

// Array to keep track of allocated memory regions.
// Initialised with 0 (NULL) by default.
struct MemoryRegion *memory_regions[32];

// Points to the first unallocated memory region of the SDRAM stack to
// be used by the DSE.
void *memory_pointer = (void *)SDRAM_TOP;

// The current memory region.
int current_region = -1;

uint32_t registers[32];

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

    // TODO: take into account the data spec.
    if ((int)(memory_pointer - cmd.dataWords[0]) < SDRAM_BASE) {
        log_error("Data specification RESERVE unable to allocate memory: SDRAM is full");
        return -1;
    }

    memory_regions[region] = sark_alloc(1, sizeof(struct MemoryRegion));

    if (memory_regions[region] == NULL) {
        log_error("Data specification RESERVE unable to allocate memory: DTCM is full");
        return -1;
    }

    memory_regions[region]->startAddress   = memory_pointer;
    memory_regions[region]->currentAddress = memory_pointer;
    memory_regions[region]->size           = cmd.dataWords[0];
    memory_regions[region]->unfilled       = (cmd.cmdWord >> 7) & 0x1;

    memory_pointer -= cmd.dataWords[0];

    return 0;
}

int execute_write(struct Command cmd) {

    int n_repeats;
    if (command_src2_in_use(cmd.cmdWord))
        n_repeats = get_command_src2Reg(cmd.cmdWord);
    else
        n_repeats = cmd.cmdWord & 0xFF;

    int data_len = (cmd.cmdWord >> 22) & 0x3;
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

    uint64_t data_val;
    if (command_src1_in_use(cmd.cmdWord) && cmd.dataLength == 0) {
        data_val = registers[get_command_src1Reg(cmd.cmdWord)];
    } else if (cmd.dataLength == 1 && data_len != 8) {
        data_val = cmd.dataWords[0];
    } else if (cmd.dataLength == 2 && data_len == 8) {
        data_val = ((uint64_t)cmd.dataWords[0] << 32) | cmd.dataWords[1];
    } else {
        log_error("Data specification WRITE bad format");
    }

    if (current_region == -1) {
        log_error("Data specification WRITE the current memory region has not been selected");
        return -1;
    } else if (memory_regions[current_region] == NULL) {
        log_error("Data specification WRITE the current memory region has not been allocated");
        return -1;
    } else if (memory_regions[current_region]->size - data_len < 0) {
        log_error("Data specification WRITE the current memory region is full");
        return -1;
    } else {
        for (int count = 0; count < n_repeats; count++) {
            uint8_t *writer = (uint8_t*)&data_val;
            for (int byte = 0; byte < data_len; byte++) {
                *(memory_regions[current_region]->currentAddress++) = *writer;
                writer++;
            }
        }
    }

    return 0;

}

int execute_switch_focus(struct Command cmd) {
    int region;
    if (command_src1_in_use(cmd.cmdWord))
        region = registers[get_command_src1Reg(cmd.cmdWord)];
    else
        region = (cmd.cmdWord >> 8) & 0xF;
    if (memory_regions[region] == NULL) {
        log_error("Data specification SWITCH_FOCUS Unallocated memory region");
        return -1;
    } else {
        current_region = region;
    }
    return 0;
}

// Execute a data specification stored at address given by parameter.
void data_specification_executor(uint32_t ds_block_address) {

    // Pointer to the next command to be executed.
    uint32_t *command_pointer = (uint32_t *)ds_block_address;

    struct Command cmd;

    // Dummy value of the opCode.
    cmd.opCode = 0x00;

    while (cmd.opCode != END_SPEC) {
        cmd = get_next_command(&command_pointer);
        switch (cmd.opCode) {
            case BREAK:
                // This command stops the execution of the data spec and
                // outputs an error in the log.
                log_error("BREAK encountered");
                return;
            case NOP:
                // This command executes no operation.
                break;
            case RESERVE:
                execute_reserve(cmd);
                break;
            case FREE:
                log_error("Unimplemented DSE command FREE");
                break;
            case DECLARE_RNG:
                log_error("Unimplemented DSE command DECLARE_RNG");
                break;
            case DECLARE_RANDOM_DIST:
                log_error("Unimplemented DSE command DECLARE_RANDOM_DIST");
                break;
            case GET_RANDOM_NUMBER:
                log_error("Unimplemented DSE command GET_RANDOM_NUMBER");
                break;
            case START_STRUCT:
                log_error("Unimplemented DSE command START_STRUCT");
                break;
            case STRUCT_ELEM:
                log_error("Unimplemented DSE command STRUCT_ELEM");
                break;
            case END_STRUCT:
                log_error("Unimplemented DSE command END_STRUCT");
                break;
            case START_PACKSPEC:
                log_error("Unimplemented DSE command START_PACKSPEC");
                break;
            case PACK_PARAM: 
                log_error("Unimplemented DSE command PACK_PARAM");
                break;
            case END_PACKSPEC:
                log_error("Unimplemented DSE command END_PACKSPEC");
                break;
            case START_CONSTRUCTOR:
                log_error("Unimplemented DSE command START_CONSTRUCTOR");
                break;
            case END_CONSTRUCTOR:
                log_error("Unimplemented DSE command END_CONSTRUCTOR");
                break;
            case CONSTRUCT:
                log_error("Unimplemented DSE command CONSTRUCT");
                break;
            case WRITE:
                execute_write(cmd);
                break;
            case WRITE_STRUCT:
                log_error("Unimplemented DSE command WRITE_STRUCT");
                break;
            case BLOCK_COPY:
                log_error("Unimplemented DSE command BLOCK_COPY");
                break;
            case SWITCH_FOCUS:
                execute_switch_focus(cmd);
                break;
            case BREAK_LOOP:
                log_error("Unimplemented DSE command BREAK_LOOP");
                break;
            case END_LOOP:
                log_error("Unimplemented DSE command END_LOOP");
                break;
            case IF:
                log_error("Unimplemented DSE command IF");
                break;
            case ELSE:
                log_error("Unimplemented DSE command ELSE");
                break;
            case END_IF:
                log_error("Unimplemented DSE command END_IF");
                break;
            case MV:
                log_error("Unimplemented DSE command MV");
                break;
            case GET_WR_PTR:
                log_error("Unimplemented DSE command GET_WR_PTR");
                break;
            case SET_WR_PTR:
                log_error("Unimplemented DSE command SET_WR_PTR");
                break;
            case ALIGN_WR_PTR:
                log_error("Unimplemented DSE command ALIGN_WR_PTR");
                break;
            case ARITH_OP:
                log_error("Unimplemented DSE command ARITH_OP");
                break;
            case LOGIC_OP:
                log_error("Unimplemented DSE command LOGIC_OP");
                break;
            case REFORMAT:
                log_error("Unimplemented DSE command REFORMAT");
                break;
            case COPY_STRUCT:
                log_error("Unimplemented DSE command COPY_STRUCT");
                break;
            case COPY_PARAM:
                log_error("Unimplemented DSE command COPY_PARAM");
                break;
            case WRITE_PARAM:
                log_error("Unimplemented DSE command WRITE_PARAM");
                break;
            case WRITE_PARAM_COMPONENT:
                log_error("Unimplemented DSE command WRITE_PARAM_COMPONENT");
                break;
            case PRINT_VAL:
                log_error("Unimplemented DSE command PRINT_VAL");
                break;
            case PRINT_TXT:
                log_error("Unimplemented DSE command PRINT_TXT");
                break;
            case PRINT_STRUCT:
                log_error("Unimplemented DSE command PRINT_STRUCT");
                break;
            case END_SPEC:
                log_info("End of spec has been reached");
                break;
            default:
                log_error("Not a DSE command: %x", cmd.opCode);
        }
    }

//    for (int i = 0; i < 3; i++, p++) {
//        log_info("OK");
//        log_info("Char : %d", *p);
//    }
}


void c_main(void) {
    data_specification_executor(DS_ADDRESS);
    log_info("Mem pointer %x", memory_pointer);
    log_info("Started at %x", SDRAM_TOP);
    log_info("diff %d", (int)SDRAM_TOP - (int)memory_pointer);
}



