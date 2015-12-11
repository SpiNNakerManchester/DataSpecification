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

//! \brief Get the value of user2 register.
//!
//! \return The value of user2.
uint32_t get_user2_value() {
    return ((vcpu_t*)SV_VCPU)[spin1_get_core_id()].user2;
}

//! \brief Get the value of user1 register.
//!
//! \return The value of user1.
uint32_t get_user1_value() {
    return ((vcpu_t*)SV_VCPU)[spin1_get_core_id()].user1;
}

//! \brief Get the value of user0 register.
//!
//! \return The value of user0.
uint32_t get_user0_value() {
    return ((vcpu_t*)SV_VCPU)[spin1_get_core_id()].user0;
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


//! \brief Allocate memory for the header and the pointer table.
void pointer_table_header_alloc() {
    log_info("Allocating memory for pointer table");
    address_t *header_start = sark_xalloc(sv->sdram_heap,
                                     HEADER_SIZE + POINTER_TABLE_SIZE,
                                     0x00,                       // tag
                                     future_sark_xalloc_flags);  // flag
    if (header_start == NULL) {
        log_error("Could not allocate memory for the header and pointer table");
        spin1_exit(-1);
    }

    ((vcpu_t*)SV_VCPU)[spin1_get_core_id()].user0 = (uint)header_start;
    
    header_start[0] = APPDATA_MAGIC_NUM;
    header_start[1] = DSE_VERSION;
    
    log_info("Header address 0x%08x", header_start);
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
  
    execRegion = (address_t) get_user0_value();
    currentBlock_size = (uint32_t) get_user1_value();
    future_app_id = (uint8_t) get_user2_value();
    
    current_app_id = sark_app_id();
    current_sark_xalloc_flags = (current_app_id << 8) | ALLOC_ID | ALLOC_LOCK;
    future_sark_xalloc_flags = (future_app_id << 8) | ALLOC_ID | ALLOC_LOCK;
    
    pointer_table_header_alloc();
    
    log_info("Executing dataSpec");
    data_specification_executor(execRegion, currentBlock_size);

    write_pointer_table();

    free_mem_region_info();
}
