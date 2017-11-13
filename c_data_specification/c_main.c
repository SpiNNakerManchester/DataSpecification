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
MemoryRegion *memory_regions[MAX_MEM_REGIONS];

//! \brief Pointer to a memory region that contains the currently executing
//!        data spec.
address_t execRegion = NULL;

//! \brief The parameter structure for the DSE
dse_data *dse_exec_data_struct;

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

//! \brief boolean to identify if the data structure for the memory map
//         report should be produced
uint8_t generate_report;

//! \brief memory are to store info related to the regions, to be used for
//         memory map report
MemoryRegion *report_header_start = NULL;

// -------------------------------------------------------------------------

#ifndef EMULATE

//! \brief Get the value of user2 register.
//!
//! \return The value of user2.
uint32_t get_user2_value() {
    return ((vcpu_t*) SV_VCPU)[spin1_get_core_id()].user2;
}

//! \brief Get the value of user1 register.
//!
//! \return The value of user1.
uint32_t get_user1_value() {
    return ((vcpu_t*) SV_VCPU)[spin1_get_core_id()].user1;
}

//! \brief Get the value of user0 register.
//!
//! \return The value of user0.
uint32_t get_user0_value() {
    return ((vcpu_t*) SV_VCPU)[spin1_get_core_id()].user0;
}

//! \brief Allocate memory for the header and the pointer table.
void pointer_table_header_alloc() {
    log_info("Allocating memory for pointer table");
    address_t header_start = sark_xalloc(sv->sdram_heap,
        HEADER_SIZE_BYTES + POINTER_TABLE_SIZE_BYTES,
        TAG, future_sark_xalloc_flags);

    if (header_start == NULL) {
        log_error("Could not allocate memory for the header and pointer table");
        spin1_exit(-1);
    }

    ((vcpu_t*) SV_VCPU)[spin1_get_core_id()].user0 = (uint) header_start;

    header_start[0] = APPDATA_MAGIC_NUM;
    header_start[1] = DSE_VERSION;

    log_info("Header address 0x%08x", header_start);

    if (generate_report) {
        report_header_start = sark_xalloc(sv->sdram_heap,
            sizeof(MemoryRegion) * MAX_MEM_REGIONS, TAG,
            future_sark_xalloc_flags);

        if (report_header_start == NULL) {
            log_error(
                "Could not allocate memory to store reporting information");
            spin1_exit(-1);
        }
        ((vcpu_t*) SV_VCPU)[spin1_get_core_id()].user1 =
                (uint) report_header_start;
        log_info("Report address 0x%08x", report_header_start);
    }
}

//! \brief Write the pointer table in the memory region specified by user0.
//! Must be called after the DSE has finished its execution so that the memory
//! regions are allocated.
void write_pointer_table() {

    // Pointer to write the pointer table.
    address_t base_ptr = (address_t) get_user0_value();
    address_t pt_writer = base_ptr + HEADER_SIZE;

    // Iterate over the memory regions and write their start address in the
    // memory location pointed at by the pt_writer.
    // If a memory region has not been defined, 0 is written.
    for (int i = 0; i < MAX_MEM_REGIONS; i++, pt_writer++) {
        if (memory_regions[i] != NULL) {
            *pt_writer = (uint32_t) memory_regions[i]->start_address;

            log_info("Region %d address 0x%08x size %d bytes, %s", i,
                *pt_writer, memory_regions[i]->size,
                memory_regions[i]->unfilled ? "unfilled" : "filled");
        } else {
            *pt_writer = 0;
        }
    }
}

void write_memory_structs_for_report() {
    MemoryRegion region_zero;

    region_zero.start_address = NULL;
    region_zero.size = 0;
    region_zero.unfilled = 0;
    region_zero.write_pointer = NULL;

    for (int i = 0; i < MAX_MEM_REGIONS; i++) {
        if (memory_regions[i] != NULL) {
            spin1_memcpy(&report_header_start[i], memory_regions[i],
                sizeof(MemoryRegion));
        } else {
            spin1_memcpy(&report_header_start[i], &region_zero,
                sizeof(MemoryRegion));
        }
    }
}

//! \brief Free all the allocated structures in the memory_regions array, used
//!        to store information about the allocated memory regions.
void free_mem_region_info() {
    for (int index = 0; index < MAX_MEM_REGIONS; index++) {
        if (memory_regions[index] != NULL) {
            sark_free(memory_regions[index]);
        }
    }
}

void c_main(void) {

    // user0 contains the address of the data specification
    //  structure with the relevant parameters
    dse_exec_data_struct = (dse_data *) get_user0_value();

    // address of the data specification to execute
    execRegion = (address_t) dse_exec_data_struct->execRegion;

    // length of the data specification to execute
    currentBlock_size = (uint32_t) dse_exec_data_struct->currentBlock_size;

    // the future application id for which the data
    // specification is currently being executed
    future_app_id = (uint8_t) dse_exec_data_struct->future_app_id;

    // generate data structure for memory map report
    generate_report = (uint8_t) dse_exec_data_struct->generate_report;

    // compute a few constants, valid for the entire DSE
    current_app_id = sark_app_id();
    current_sark_xalloc_flags = (current_app_id << 8) | ALLOC_ID | ALLOC_LOCK;
    future_sark_xalloc_flags = (future_app_id << 8) | ALLOC_ID | ALLOC_LOCK;

    // allocate memory for the table pointer
    pointer_table_header_alloc();

    // executing data specification
    log_info("Executing dataSpec");
    data_specification_executor(execRegion, currentBlock_size);

    // writing the content of the table pointer
    write_pointer_table();

    // write data structure, if required, with the data
    // for the memory map report
    if (generate_report) {
        write_memory_structs_for_report();
    }

    // freeing used memory structures in DTCM
    // this may be discarded if needed: the app_stop on this executable
    // would get rid of the data in DTCM
    free_mem_region_info();
}

#endif // !EMULATE
