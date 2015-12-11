/*! \file data_specification_executor.c
 *
 *  \brief The implementation of the on-chip Data Specification Executor (DSG).
 */

#include "commands.h"
#include "constants.h"
// data_specification_executor.h includes all the required headers if are
// needed
#include "data_specification_executor.h"

//! Array to keep track of allocated memory regions.
//! Initialised with 0 (NULL) by default.
struct MemoryRegion *memory_regions[MAX_MEM_REGIONS];

#ifndef EMULATE
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

//! \brief The app identifier of the current executable.
uint8_t current_app_id;

//! \brief The app identifier of the following executable for which the 
//!        data is being prepared.
uint8_t future_app_id;

//! \brief Pre-computed identifier for memory allocation for 
//         current executable
uint32_t current_sark_xalloc_flags;

//! \brief Pre-computed identifier for memory allocation for 
//         following application for which the data is being prepared
uint32_t future_sark_xalloc_flags;

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
    sdp_msg_t *msg = (sdp_msg_t *)mailbox;

    if (get_core_state() == CORE_BUSY)
    {
        io_printf (IO_BUF, "packet dropped - cpu state %d\n", get_core_state());
        spin1_msg_free(msg);
        return;
    }
    
    // Go in a busy state while executing.
    set_core_state(CORE_BUSY);
    log_info("Processing received packet");
    
    if (execRegion == NULL) {
        // Allocate memory of a data spec chunk and go in the WAITING_FOR_DATA
        // state.
        log_info("Allocating memory to receive dataSpec");
        currentBlock_size = ((int*)&(msg->cmd_rc))[0];
	future_app_id = (uint8_t) ((int*)&(msg->cmd_rc))[1];
	future_sark_xalloc_flags = (future_app_id << 8) | ALLOC_ID | ALLOC_LOCK;

	pointer_table_header_alloc();
	
//        execRegion = sark_alloc(1, currentBlock_size);
        log_info("Allocating %d bytes", currentBlock_size);
        execRegion = sark_xalloc(sv->sdram_heap, 
				 currentBlock_size,
				 0,
				 current_sark_xalloc_flags);

        if (execRegion == NULL) {
            log_error("Could not allocate memory for the execution of an "
                      "instruction block of %d words.", currentBlock_size);
            spin1_exit(-1);
        }
        
	set_user2_value((uint32_t)execRegion);

        // free the message to stop overload
        spin1_msg_free(msg);

        set_core_state(WAITING_FOR_DATA);
    } else {
        // Execute the data spec, free memory and go in the READY_TO_RECEIVE
        // state.
        log_info("Executing dataSpec");
        data_specification_executor(execRegion, currentBlock_size);

        //sark_xfree(sv->sdram_heap, execRegion, 0x01);
        execRegion = NULL;
        currentBlock_size = 0;

        // free the message to stop overload
        spin1_msg_free(msg);

        set_core_state(READY_TO_RECEIVE);
    }
}

//! \brief Allocate memory for the header and the pointer table.
void pointer_table_header_alloc() {
    log_info("Allocating memory for pointer table");
    void *header_start = sark_xalloc(sv->sdram_heap,
                                     HEADER_SIZE + POINTER_TABLE_SIZE,
                                     0x00,                       // tag
                                     future_sark_xalloc_flags);  // flag
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

    log_info("Header address 0x%08x", header_writer);

    // Write the headers.
    *header_writer       = APPDATA_MAGIC_NUM;
    *(header_writer + 1) = DSE_VERSION;
}

//! \brief Write the pointer table in the memory region specified by user0.
//! Must be called after the DSE has finished its execution so that the memory
//! regions are allocated.
void write_pointer_table() {
  
    // Pointer to write the pointer table.
    address_t base_ptr = (address_t)(((vcpu_t*)SV_VCPU)[spin1_get_core_id()].user0);
    address_t pt_writer = base_ptr + HEADER_SIZE;

    // Iterate over the memory regions and write their start address in the
    // memory location pointed at by the pt_writer.
    // If a memory region has not been defined, 0 is written.
    for (int i = 0; i < MAX_MEM_REGIONS; i++, pt_writer++) {
        if (memory_regions[i] != NULL) {
            *pt_writer = (uint32_t) memory_regions[i]->start_address;

            log_info("Region %d address 0x%08x size %d bytes, %s", i,
                     *pt_writer,
                     memory_regions[i]->size,
                     memory_regions[i]->unfilled ? "unfilled" : "filled");
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
    current_app_id = sark_app_id();
    current_sark_xalloc_flags = (current_app_id << 8) | ALLOC_ID | ALLOC_LOCK;

    spin1_callback_on(SDP_PACKET_RX, sdp_packet_callback, 1);
    set_core_state(READY_TO_RECEIVE);
    
    log_info("DSE ready to receive specs");
    spin1_start(FALSE);

    write_header();
    write_pointer_table();

    free_mem_region_info();
}

#endif
