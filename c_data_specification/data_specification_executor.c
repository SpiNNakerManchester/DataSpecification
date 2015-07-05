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

//! The current memory region.
//! Initialised with -1, since no context switch has been performed.
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

//! \brief Execute a part of a data specification.
//!        Assumes the given slice of data specification is atomic and
//!        valid.
//! \param[in] ds_start The start address of the data spec.
//! \param[in] ds_size  The size of the data spec. Must be divisible by 4.
void data_specification_executor(address_t ds_start, uint32_t ds_size) {

    // Pointer to the next command to be executed.
    command_pointer = ds_start;

    // Pointer to the end of the data spec memory region.
    address_t ds_end = ds_start + ds_size / 4;

    struct Command cmd;

    // Dummy value of the opCode.
    cmd.opCode = 0x00;

    while (command_pointer < ds_end && cmd.opCode != END_SPEC) {
        cmd = get_next_command();
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
                spin1_exit(0);
                break;
            default:
                log_error("Not a DSE command: %x", cmd.opCode);
        }
    }
}

//! \brief Set the header's start address.
void set_header_start_address() {
    vcpu_t *sark_virtual_processor_info = (vcpu_t*) SV_VCPU;
    sark_virtual_processor_info[spin1_get_core_id()].user0 = HEADER_START_ADDRESS;
}

//! \brief Set the current core's state.
void set_core_state(enum Core_states core_state) {
    ((vcpu_t*)SV_VCPU)[spin1_get_core_id()].user1 = core_state;
}

//! \brief Get the current core's state.
//!
//! \return The state of the current core (the value of user1).
int get_core_state() {
    return ((vcpu_t*)SV_VCPU)[spin1_get_core_id()].user1;
}

//! \brief Set the value of user2 register.
//!
//! \param[in] value The new value of user2.
int set_user2_value(uint32_t value) {
    ((vcpu_t*)SV_VCPU)[spin1_get_core_id()].user2 = value;
}

//! \brief Pointer to a memory region that contains the currently executing
//!        data spec.
address_t execRegion = NULL;

//! \brief The size of the execRegion memory block.
int currentBlock_size = 0;

//! \brief Callback for sdp packets.
//! 
//! The data spec is passed to the DSE in atomic chunks (the smallest chunks
//! that can be executed on their own).
//! By default, the DSE is in a READY_TO_RECEIVE state.
//! In order to send a packet to be executed, the specification sender must
//! send a sdp packet that contains the length of the next chunk. Then, the
//! DSE allocates memory for that chunk, puts memory address in user2 and goes
//! in the WAITING_FOR_DATA state. The sender must then read user2, put data in
//! the indicated address and send a trigger packet (any sdp packet), which
//! will trigger the execution of the chunk.
//!
//! \param[in] mailbox The mailbox where the packet is received.
//! \param[in] mailbox The packet's port.
void sdp_packet_callback(uint mailbox, uint port) {

    // Go in a busy state while executing.
    set_core_state(CORE_BUSY);

    sdp_msg_t *msg = (sdp_msg_t *)mailbox;

    if (execRegion == NULL) {
        // Allocate memory of a data spec chunk and go in the WAITING_FOR_DATA
        // state.
        currentBlock_size = ((int*)&(msg->cmd_rc))[0];

        execRegion = sark_alloc(1, currentBlock_size);
        set_user2_value((uint32_t)execRegion);

        if (execRegion == NULL) {
            log_error("Could not allocate memory for the execution of an "
                      "instruction block of %d words.", currentBlock_size);
            spin1_exit(-1);
        }

        // free the message to stop overload
        spin1_msg_free(msg);

        set_core_state(WAITING_FOR_DATA);
    } else {
        // Execute the data spec, free memory and go in the READY_TO_RECEIVE
        // state.
        data_specification_executor(execRegion, currentBlock_size);

        sark_free(execRegion);
        execRegion = NULL;
        currentBlock_size = 0;

        // free the message to stop overload
        spin1_msg_free(msg);

        set_core_state(READY_TO_RECEIVE);
    }
}

//! \brief Allocate memory for the header and the pointer table.
void pointer_table_header_alloc() {
    void *header_start = sark_xalloc(((sv_t*)SV_SV)->sdram_heap,
                                     HEADER_SIZE + POINTER_TABLE_SIZE,
                                     0x00,                // tag
                                     0x01);               // flag
    if (header_start == NULL) {
        log_error("Could not allocate memory for the header and pointer table");
        spin1_exit(-1);
    }

    ((vcpu_t*)SV_VCPU)[spin1_get_core_id()].user0 = (uint)header_start;
}

//! \brief Write the DSE headers in the memory region specified by user0.
void write_header() {
    // Pointer to write the headers.
    address_t header_writer =
                     (address_t)((vcpu_t*)SV_VCPU)[spin1_get_core_id()].user0;

    log_info("Header address %x", header_writer);

    // Write the headers.
    *header_writer       = APPDATA_MAGIC_NUM;
    *(header_writer + 1) = DSE_VERSION;
}

//! \brief Write the pointer table in the memory region specified by user0.
//! Must be called after the DSE has finished its execution so that the memory
//! regions are allocated.
void write_pointer_table() {

    // Pointer to write the pointer table.
    address_t pt_writer =
       (address_t)(((vcpu_t*)SV_VCPU)[spin1_get_core_id()].user0) + HEADER_SIZE;

    // Iterate over the memory regions and write their start address in the
    // memory location pointed at by the pt_writer.
    // If a memory region has not been defined, 0 is written.
    for (int i = 0; i < MAX_MEM_REGIONS; i++, pt_writer++) {
        if (memory_regions[i] != NULL) {
            *pt_writer = (uint32_t)memory_regions[i]->startAddress;

            log_info("Region %d address %x %s", i, 
                     (uint32_t)memory_regions[i]->startAddress,
                     memory_regions[i]->unfilled ? "unfilled" : "");
        } else {
            *pt_writer = 0;
        }
    }
}

//! \brief Free all the allocated structures in the memory_regions array, used
//!        to store information about the allocated memory regions.
void free_mem_region_info() {
    for (int index = 0; index < MAX_MEM_REGIONS; index++)
        if (memory_regions[index] != NULL)
            sark_free(memory_regions[index]);
}

void c_main(void) {
    pointer_table_header_alloc();

    spin1_callback_on(SDP_PACKET_RX, sdp_packet_callback, 1);
    set_core_state(READY_TO_RECEIVE);
    spin1_start(FALSE);

    write_header();
    write_pointer_table();

    free_mem_region_info();
}


