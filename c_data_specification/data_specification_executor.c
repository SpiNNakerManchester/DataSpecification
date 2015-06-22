/*! \file data_specification_executor.c
 *
 *  \brief The implementation of the on-chip Data Specification Executor (DSG).
 */

#include "commands.h"
#include "constants.h"
#include "data_specification_executor_functions.h"
#include <stdint.h>
#include <sark.h>
#include <debug.h>
#include <data_specification.h>
#include <spinnaker.h>
#include <spin1_api.h>

//! Array to keep track of allocated memory regions.
//! Initialised with 0 (NULL) by default.
struct MemoryRegion *memory_regions[MAX_MEM_REGIONS];

//! Points to the first unallocated memory region of the SDRAM stack to
//! be used by the DSE.
void *stack_pointer = (void *)STACK_START_ADDRESS;

//! The current memory region.
//! Initialised with -1, as no context switch has been performed.
int current_region = -1;

//! The array of registers.
uint32_t registers[MAX_REGISTERS];

//! Pointer to the next command to be analysed.
address_t command_pointer;


//! \brief Read the next command from the memory and updates the command_pointer
//! accordingly.
//! \return A Command object storing the command.
struct Command get_next_command() {

    // The command object.
    struct Command cmd;

    // Get the command word (the first word of the command).
    uint32_t cmd_word = *command_pointer;
    command_pointer++;

    // Get the command fields.
    cmd.dataLength     = command_get_length(cmd_word);
    cmd.opCode         = command_get_opcode(cmd_word);
    cmd.fieldUsage     = command_get_fieldUsage(cmd_word);
    cmd.cmdWord        = cmd_word;

    // Get the data words.
    for (int index = 0; index < cmd.dataLength; index++, command_pointer++) {
        cmd.dataWords[index] = *command_pointer;
    }

    return cmd;
}

//! \brief Execute a data specification.
//! \param[in] ds_block_address The address of the data sequence.
void data_specification_executor(uint32_t ds_block_address) {

    // Pointer to the next command to be executed.
    command_pointer = (address_t)ds_block_address;

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
            case WRITE_ARRAY:
                execute_write_array(cmd);
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
    write_pointer_table();
    write_header();
}

//! \brief Write the DSE headers.
void write_header() {
    j
    // Pointer to write the headers.
    address_t header_writer   = stack_pointer;

    // Write the headers.
    *header_writer       = APPDATA_MAGIC_NUM;
    *(header_writer + 1) = DSE_VERSION;

    // Update the stack pointer.
    stack_pointer += 2;
}

//! \brief Write the pointer table.
//! Must be called after the DSE has finished its execution so that the memory
//! regions are allocated.
void write_pointer_table() {

    // Pointer to write the pointer table.
    address_t pointer_table_writer = stack_pointer;

    // Iterate over the memory regions and write their start address in the
    // memory location pointed at by the pointer_table_writer.
    for (int i = 0; i < MAX_MEM_REGIONS; i++, pointer_table_writer++) {
        if (memory_regions[i] != NULL) {
            *pointer_table_writer = (uint32_t)memory_regions[i]->startAddress;
        } else {
            *pointer_table_writer = 0;
        }
    }
}

//! \brief Set the header's start address.
void set_header_start_address() {
    vcpu_t *sark_virtual_processor_info = (vcpu_t*) SV_VCPU;
    sark_virtual_processor_info[spin1_get_core_id()].user0 = HEADER_START_ADDRESS;
}

void c_main(void) {

    data_specification_executor(DS_ADDRESS);
    set_header_start_address();
    log_info("Mem pointer %x", stack_pointer);
    log_info("Started at %x", SDRAM_TOP);
    log_info("diff %d", (int)SDRAM_TOP - (int)stack_pointer);
    log_info("Data address %x", data_specification_get_data_address());
}



