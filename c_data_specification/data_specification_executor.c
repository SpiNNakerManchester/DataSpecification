/*!
 *  \file data_specification_executor_functions.c
 *  \brief Functions to execute the commands in the data sequence.
 */
#include "data_specification_executor.h"
#include "data_specification_stack.h"
#include "struct.h"

#include <math.h>

// Load external variables defined in data_specification_executor.c
extern struct MemoryRegion *memory_regions[MAX_MEM_REGIONS];

//! The current memory region.
//! Initialised with -1, since no context switch has been performed.
int current_region = -1;

//! The array of registers.
uint64_t registers[MAX_REGISTERS];

//! Pointer to the next command to be analysed.
address_t command_pointer;

struct Struct *structs[MAX_STRUCTS];
struct Constructor constructors[MAX_CONSTRUCTORS];

//! \brief Find the length of a command (bits 29:28).
//! \param[in] The command word (the first word of a command).
//! \return The length of the command (integer from 0 to 3, as stated in the
//!         data spec documentation.
uint8_t command_get_length(uint32_t command) {
    return (command & 0x30000000) >> 28;
}

//! \brief Find the operation code of a command (bits 27:20).
//! \param[in] The command word (the first word of a command).
//! \return The command's opcode.
enum OpCode command_get_opcode(uint32_t command) {
    return (command & 0x0FF00000) >> 20;
}

//! \brief Function to find the field usage of a command (bits 18:16).
//! \param[in] The command word (the first word of a command).
//! \return The command's field usage, 3 one-hot encoded bits at the end of the
//!         returned byte.
uint8_t command_get_fieldUsage(uint32_t command) {
    return (command & 0x00070000) >> 16;
}

//! \brief Find the destination register used by a command (bits 15:12).
//! \param[in] The command word (the first word of a command).
//! \return The register used as destination by the given command.
uint8_t command_get_destReg(uint32_t command) {
    return (command & 0x0000F000) >> 12;
}

//! \brief Find the source1 register used by a command (bits 11:8).
//! \param[in] The command word (the first word of a command).
//! \return The register used as source1 by the given command.
uint8_t command_get_src1Reg(uint32_t command) {
    return (command & 0x00000F00) >> 8;
}

//! \brief Find the source2 register used by a command (bits 7:4).
//! \param[in] The command word (the first word of a command).
//! \return The register used as source2 by the given command.
uint8_t command_get_src2Reg(uint32_t command) {
    return (command & 0x000000F0) >> 4;
}

//! \brief Check if a command uses a register as destination.
//! \param[in] The command word (the first word of a command).
//! \return 1 if the destination register is used by the given command,
//!         0 otherwise.
int command_dest_in_use(uint32_t command) {
    return (command_get_fieldUsage(command) & 0x4) >> 2;
}

//! \brief Check if a command uses a register as source1.
//! \param[in] The command word (the first word of a command).
//! \return 1 if the source1 register is used by the given command,
//!         0 otherwise.
int command_src1_in_use(uint32_t command) {
    return (command_get_fieldUsage(command) & 0x2) >> 1;
}

//! \brief Check if a command uses a register as source2.
//! \param[in] The command word (the first word of a command).
//! \return 1 if the source2 register is used by the given command,
//!         0 otherwise.
int command_src2_in_use(uint32_t command) {
    return command_get_fieldUsage(command) & 0x1;
}

//! \brief Read the next command from the memory and update the command_pointer
//!        accordingly.
//! \return A Command object storing the command.
struct Command get_next_command() {

    // The command object.
    struct Command cmd;

    // Get the command word (the first word of the command).
    uint32_t cmd_word = *command_pointer;
    command_pointer++;

    // Get the command fields.
    cmd.opCode         = command_get_opcode(cmd_word);
    cmd.cmdWord        = cmd_word;
    cmd.dataLength     = command_get_length(cmd_word);

    // Get the data words.
    for (int index = 0; index < command_get_length(cmd_word); index++) {
        cmd.dataWords[index] = *(command_pointer++);
    }

    return cmd;
}

//! \brief Execute a reserve memory command, which allocates a memory region of
//!        a given size on SDRAM.
//! \param[in] The command to be executed.
void execute_reserve(struct Command cmd) {

    // Check if the instruction format is correct.
    if (cmd.dataLength != 1) {
        log_error("Data specification RESERVE requires one word as argument");
        rt_error(RTE_ABORT);
    }

    // Get the region id and perform some checks on it.
    uint8_t region_id = cmd.cmdWord & 0x1F;
    if (region_id > MAX_MEM_REGIONS) {
        log_error("RESERVE memory region id %d out of bounds", region_id);
        rt_error(RTE_ABORT);
    }
    if (memory_regions[region_id] != NULL) {
        log_error("RESERVE region %d already in use", region_id);
        rt_error(RTE_ABORT);
    }

    // Allocate the required memory .
    // int mem_region_size    = ceil((double)cmd.dataWords[0] / 4.) * 4;
    uint32_t mem_region_size = ((cmd.dataWords[0] & 0x03) > 0) ?
                               (((cmd.dataWords[0] >> 2) + 1) << 2) :
                                                    cmd.dataWords[0];

    void *mem_region_start = sark_xalloc(((sv_t*)SV_SV)->sdram_heap,
                                         mem_region_size, 0, 0x01);

    if (mem_region_start == NULL) {
        log_error("RESERVE unable to allocate %d bytes of SDRAM memory.",
                  mem_region_size);
        rt_error(RTE_ABORT);
    }

    memory_regions[region_id] = sark_alloc(1, sizeof(struct MemoryRegion));

    if (memory_regions[region_id] == NULL) {
        log_error("RESERVE unable to allocate memory on DTCM");
        rt_error(RTE_ABORT);
    }

    uint8_t read_only = (cmd.cmdWord >> 7) & 0x1;

    log_debug("RESERVE %smemory region %d of %d bytes",
              read_only ? "read-only " : "", region_id, mem_region_size);

    memory_regions[region_id]->size           = mem_region_size;
    memory_regions[region_id]->start_address   = mem_region_start;
    memory_regions[region_id]->write_pointer  = mem_region_start;
    memory_regions[region_id]->unfilled       = read_only;

    if (memory_regions[region_id]->unfilled) {
        for (int i = 0; i < (memory_regions[region_id]->size >> 2); i++)
            *(memory_regions[region_id]->start_address + i) = 0;
    }
}

//! \brief Execute a FREE command.
//! \param[in] cmd The command to be executed.
void execute_free(struct Command cmd) {

    uint8_t region_id = cmd.cmdWord & 0x0F;

    if (memory_regions[region_id] == NULL) {
        log_error("FREE region %d not allocated.", region_id);
        rt_error(RTE_ABORT);
    }

    log_debug("FREE memory region %d.", region_id);

    sark_xfree(((sv_t*)SV_SV)->sdram_heap,
                memory_regions[region_id]->start_address, 0x01);

    sark_free(memory_regions[region_id]);

    memory_regions[region_id] = NULL;
}

//! \brief Private function to write a value to the specified memory location
//!        and update its write pointer accordingly.
//!        The caller must ensure the selected memory region is valid.
//! \param[in] value Pointer to the data to be written.
//! \param[in] size The size in bytes of the data to be written.
//                  The supported sizes are 1, 2, 4 and 8 bytes.
void write_value(void *value, int size) {

    switch (size) {
        case 1:
            *(memory_regions[current_region]->write_pointer) =
                                                        *((uint8_t*)value);
            break;
        case 2:
            *((uint16_t*)memory_regions[current_region]->write_pointer) =
                                                        *((uint16_t*)value);
            break;
        case 4:
            *((uint32_t*)memory_regions[current_region]->write_pointer) =
                                                        *((uint32_t*)value);
            break;
        case 8:
            *((uint64_t*)memory_regions[current_region]->write_pointer) =
                                                        *((uint64_t*)value);
            break;
        default:
            log_error("write value unknown size");
            rt_error(RTE_ABORT);
    }

    ((memory_regions[current_region]->write_pointer)) += size;
}

//! \brief Execute a WRITE command, which writes 1, 2, 4 or 8 bytes of data from
//!        a parameter to memory, with the possibility of data to be repeated.
//! \param[in] cmd The command to be executed.
void execute_write(struct Command cmd) {

    // The number of repetitions.
    int n_repeats;

    // If the source2 register is in use, it specifies the number or
    // repetitions.
    // Otherwise, the number of repetitions is stored into the last significant
    // byte.
    if (command_src2_in_use(cmd.cmdWord))
        n_repeats = registers[command_get_src2Reg(cmd.cmdWord)];
    else {
        n_repeats = cmd.cmdWord & 0xFF;
    }

    // The length of the data (bits 13:12).
    int data_len = 0x1 << ((cmd.cmdWord >> 12) & 0x3);

    // The value of the data to be written.
    uint64_t data_val;
    if (command_src1_in_use(cmd.cmdWord) && cmd.dataLength == 0) {
        data_val = registers[command_get_src1Reg(cmd.cmdWord)];
    } else if (cmd.dataLength == 1 && data_len != 8) {
        data_val = cmd.dataWords[0];
    } else if (cmd.dataLength == 2 && data_len == 8) {
        data_val = ((uint64_t)cmd.dataWords[0] << 32) | cmd.dataWords[1];
    } else {
        log_error("WRITE format error. DataLength %d data_len %d src1 in use %d",
                  cmd.dataLength, data_len, command_src1_in_use(cmd.cmdWord));
        rt_error(RTE_ABORT);
    }

    // Perform some checks and, if everything is fine, write the data n_repeats
    // times.
    if (current_region == -1) {
        log_error("WRITE the current memory region has not been selected");
        rt_error(RTE_ABORT);
    } else if (memory_regions[current_region] == NULL) {
        log_error("WRITE the current memory region has not been allocated");
        rt_error(RTE_ABORT);
    } else if (memory_regions[current_region]->size - data_len < 0) {
        log_error("WRITE the current memory region is full");
        rt_error(RTE_ABORT);
    } else {
        for (int count = 0; count < n_repeats; count++)
            write_value(&data_val, data_len);
    }
}

//! \brief Execute a WRITE_ARRAY command, which writes an array of 32 bit words
//!        to memory.
//! \param[in] cmd The command to be executed.
void execute_write_array(struct Command cmd) {

    // The length of the array is specified in the second word of the command.
    int length        = cmd.dataWords[0];
    uint8_t data_size = cmd.cmdWord & 0x0F;

    // Perform some checks and, if everything is fine, write the array to
    // memory.
    if (current_region == -1) {
        log_error("WRITE_ARRAY the current memory region has not been selected");
        rt_error(RTE_ABORT);
    } else if (memory_regions[current_region] == NULL) {
        log_error("WRITE_ARRAY the current memory region has not been allocated");
        rt_error(RTE_ABORT);
    } else if (memory_regions[current_region]->size - length * data_size < 0) {
        log_error("WRITE_ARRAY the current memory region is full");
        rt_error(RTE_ABORT);
    } else {

        uint8_t *array_writer = (uint8_t*)command_pointer;
        for (int count = 0; count < length; count++) {
            write_value(array_writer, data_size);
            array_writer += data_size;
        }

        command_pointer = ((long)array_writer & 0x03)
                         ? (uint32_t*)((((long)array_writer >> 2) + 1) << 2)
                         : (uint32_t*)array_writer;
    }
}

//! \brief Execute a SWITCH_FOCUS command, which changes the selected memory
//!        region.
//! \param[in] cmd The command to be executed.
void execute_switch_focus(struct Command cmd) {

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
        log_error("SWITCH_FOCUS unallocated memory region");
        rt_error(RTE_ABORT);
    } else {
        current_region = region;
    }
}

extern int stack_size;

//! \brief Execute a LOOP command.
//! \param[in] cmd The command to be executed.
void execute_loop(struct Command cmd) {

    int used_data_words = 0;

    // The start value of the loop counter.
    int loop_start;
    if (command_dest_in_use(cmd.cmdWord))
        loop_start = registers[command_get_destReg(cmd.cmdWord)];
    else
        loop_start = cmd.dataWords[used_data_words++];

    // The end value of the loop counter.
    int loop_end;
    if (command_src1_in_use(cmd.cmdWord))
        loop_end = registers[command_get_src1Reg(cmd.cmdWord)];
    else
        loop_end = cmd.dataWords[used_data_words++];

    // The step of the loop counter.
    int increment;
    if (command_src2_in_use(cmd.cmdWord))
        increment = registers[command_get_src2Reg(cmd.cmdWord)];
    else
        increment = cmd.dataWords[used_data_words++];

    // The register used to store the counter.
    int count_reg = cmd.cmdWord & 0xFF;

    // If the loop is not going to have any iteration, skip to the first
    // END_LOOP. Otherwise, start iterating.
    if (loop_start >= loop_end) {
        struct Command command;
        while((command = get_next_command()).opCode != END_LOOP);
    } else {
        // Push the return value of the command pointer on the stack.
        stack_push(command_pointer);

        for (registers[count_reg] = loop_start;
             registers[count_reg] < loop_end;
             registers[count_reg] += increment) {
            data_specification_executor(stack_top(), 0);
        }
        // Pop the return value of the command pointer from the stack.
        stack_pop();
    }
}

//! \brief Execute a START_STRUCT (structure definition) command.
//!        Reads the entire structure definition, up to the END_STRUCT command.
//! \param[in] cmd The command to be executed.
void execute_start_struct(struct Command cmd) {
    // The id of the new struct.
    int struct_id = cmd.cmdWord & 0x1F;

    log_debug("START STRUCT %d", struct_id);

    // Save the command pointer.
    stack_push(command_pointer);

    // Count the number of struct elements.
    struct Command command;
    int no_of_elements = 0;
    while ((command = get_next_command()).opCode != END_STRUCT)
        no_of_elements++;

    // Restore the command pointer.
    command_pointer = stack_pop();

    // Allocate memory for the new struct definition.
    struct Struct *str = struct_new(no_of_elements);

    // Read all the entries in the struct definition and create the requested
    // structure.
    struct Command structEntry;
    int current_element_id = 0;
    while ((structEntry = get_next_command()).opCode != END_STRUCT) {
        if (structEntry.opCode != STRUCT_ELEM) {
            log_error("A struct definition must contain only struct elements");
            rt_error(RTE_ABORT);
        }
        int elem_type = structEntry.cmdWord & 0x1F;

        uint64_t value = 0;
        if (structEntry.dataLength == 1)
            value = structEntry.dataWords[0];
        else if (structEntry.dataLength == 2)
            value = ((uint64_t)structEntry.dataWords[0] << 32)
                  | structEntry.dataWords[1];

        log_debug("STRUCT_ELEM type %d value %08x", elem_type, value);

        struct_set_element_type(str, current_element_id, elem_type);
        struct_set_element_value(str, current_element_id, value);

        current_element_id++;
    }

    // Store a pointer to the newly created struct.
    structs[struct_id] = str;
}

//! \brief Execute a WRITE_STRUCT command, which writes a struct to the current
//!        memory region.
//! \param[in] cmd The command to be executed.
void execute_write_struct(struct Command cmd) {

    // The number of repetitions of the same struct.
    log_info("WRITE STRUCT in region %d", current_region);
    uint8_t n_repeats;
    if (command_src1_in_use(cmd.cmdWord)) {
        n_repeats = registers[command_get_src1Reg(cmd.cmdWord)];
    } else {
        n_repeats = (cmd.cmdWord & 0xF00) >> 8;
    }

    // The id of the struct to be printed.
    uint8_t struct_id = cmd.cmdWord & 0xF;

    if (structs[struct_id] == NULL) {
        log_error("WRITE_STRUCT structure %d has not been defined", struct_id);
        rt_error(RTE_ABORT);
    }

    // Iterate over all elements of the struct n times and print all the
    // defined elements.
    for (int count = 0; count < n_repeats; count++) {
        for (int elem_id = 0; elem_id < structs[struct_id]->size; elem_id++)
                write_value(&(structs[struct_id]->elements[elem_id].data),
                            data_type_get_size(
                                structs[struct_id]->elements[elem_id].type));
    }
}

//! \brief Execute a MV instruction.
//! \param[in] cmd The command to be executed.
void execute_mv(struct Command cmd) {

    // The id of the destination register.
    uint8_t dest_id = command_get_destReg(cmd.cmdWord);

    // The data to be moved.
    uint64_t data;
    if (command_src1_in_use(cmd.cmdWord))
        data = registers[command_get_src1Reg(cmd.cmdWord)];
    else if (cmd.dataLength == 1)
        data = cmd.dataWords[0];
    else
        data = ((uint64_t)cmd.dataWords[0] << 32) | cmd.dataWords[1];

    // Perform the actual data move.
    registers[dest_id] = data;
}

//! \brief Execute a LOGIC_OP instruction.
//! \param[in] cmd The command to be executed.
void execute_logic_op(struct Command cmd) {

    // The operation to be performend.
    uint8_t operation = cmd.cmdWord & 0xF;

    // The first operand.
    uint64_t source1;
    if (command_src1_in_use(cmd.cmdWord)) {
        source1 = registers[command_get_src1Reg(cmd.cmdWord)];
    } else {
        source1 = cmd.dataWords[0];
    }

    // The second operand.
    uint64_t source2;
    if (operation != 0x5 && command_src2_in_use(cmd.cmdWord)) {
        source2 = registers[command_get_src2Reg(cmd.cmdWord)];
    } else {
        if (command_src1_in_use(cmd.cmdWord))
            source2 = cmd.dataWords[0];
        else
            source2 = cmd.dataWords[1];
    }

    // The id of the destination register.
    uint8_t dest_id = command_get_destReg(cmd.cmdWord);

    switch (operation) {
        case 0x0: registers[dest_id] = source1 << source2; break;
        case 0x1: registers[dest_id] = source1 >> source2; break;
        case 0x2: registers[dest_id] = source1 |  source2; break;
        case 0x3: registers[dest_id] = source1 &  source2; break;
        case 0x4: registers[dest_id] = source1 ^  source2; break;
        case 0x5: registers[dest_id] =~source1; break;
        default:
            log_error("Undefined logic operation %d", operation);
            rt_error(RTE_ABORT);
    }
}


//! \brief Execute a WRITE_PARAM instruction.
//! \param[in] cmd The command to be executed.
void execute_write_param(struct Command cmd) {

    // The value to be written.
    uint32_t value;
    if (command_src1_in_use(cmd.cmdWord)) {
        value = registers[command_get_src1Reg(cmd.cmdWord)];
    } else {
        value = cmd.dataWords[0];
    }

    uint8_t struct_id = (cmd.cmdWord & 0xF000) >> 12;
    uint8_t elem_id   = cmd.cmdWord & 0xFF;

    if (structs[struct_id] == NULL) {
        log_error("WRITE_PARAM structure %d has not been defined", struct_id);
        rt_error(RTE_ABORT);
    }
    if (structs[struct_id]->size <= elem_id) {
        log_error("WRITE_PARAM %d is not a valid element id in structure %d",
                  struct_id, elem_id);
        rt_error(RTE_ABORT);
    }

    log_debug("Setting element %d of struct %d to %08x", elem_id, struct_id,
                                                        value);
    struct_set_element_value(structs[struct_id], elem_id, value);
}

//! \brief Execute a READ_PARAM instruction.
//! \param[in] cmd The command to be executed.
void execute_read_param(struct Command cmd) {
    //log_info("READ_PARAM %08x", cmd.cmdWord);
    uint8_t dest_reg = command_get_destReg(cmd.cmdWord);
    uint8_t struct_id = cmd.cmdWord & 0xF;
    uint8_t elem_id;
    if (command_src1_in_use(cmd.cmdWord))
        elem_id = registers[command_get_src1Reg(cmd.cmdWord)];
    else
        elem_id = (cmd.cmdWord & 0xFF0) >> 4;

    registers[dest_reg] = structs[struct_id]->elements[elem_id].data;
}

//! \brief Execute a COPY_PARAM instruction.
//! \param[in] cmd The command to be executed.
void execute_copy_param(struct Command cmd) {

    uint8_t dest_id = (cmd.cmdWord & 0xF000) >> 12;
    uint8_t src_struct_id  = (cmd.cmdWord & 0x0F00) >> 8;

    uint8_t dest_elem_id  = (cmd.dataWords[0] & 0xFF00) >> 8;
    uint8_t src_elem_id   = (cmd.dataWords[0] & 0x00FF);

    if (structs[src_struct_id] == NULL) {
        log_error("COPY_PARAM source structure %d not defined.", src_struct_id);
        rt_error(RTE_ABORT);
    }
    if (structs[src_struct_id]->size <= src_elem_id) {
        log_error("COPY_PARAM source element %d of structure %d not defined.",
                  dest_elem_id, dest_id);
        rt_error(RTE_ABORT);
    }

    if (command_dest_in_use(cmd.cmdWord)) {
        registers[dest_id] = structs[src_struct_id]->elements[src_elem_id].data;
    } else {

        if (structs[src_struct_id] == NULL) {
            log_error("COPY_PARAM destination structure %d not defined.",
                      dest_id);
            rt_error(RTE_ABORT);
        }
        if (structs[src_struct_id]->size <= dest_elem_id) {
            log_error("COPY_PARAM destination element %d of structure %d "
                      "not defined.", dest_elem_id, dest_id);
            rt_error(RTE_ABORT);
        }

        structs[dest_id]->elements[dest_elem_id].data =
                            structs[src_struct_id]->elements[src_elem_id].data;
    }
}

//! \brief Execute a PRINT_TEXT command.
//! \param[in] cmd The command to be executed.
void execute_print_text(struct Command cmd) {

    // The number of characters to be printed.
    uint8_t n_characters = cmd.cmdWord & 0xFF;

    if (n_characters > PRINT_TEXT_MAX_CHARACTERS) {
        log_error("PRINT_TEXT too many characters: %d", n_characters);
        rt_error(RTE_ABORT);
    }

    char *reader = (char*)cmd.dataWords;

    // Temporary storage for the text to be printed.
    char temp[PRINT_TEXT_MAX_CHARACTERS];

    // Read the characters and copy them to the temporary storage.
    for (int count = 0; count <= n_characters; count++, reader++)
        temp[count] = *reader;

    temp[n_characters + 1] = '\0';
    log_info("Print text: %s", temp);
}

//! \brief Execute a PRINT_STRUCT command.
//! \param[in] cmd The command to be executed.
void execute_print_struct(struct Command cmd) {

    uint8_t struct_id;
    if (command_src1_in_use(cmd.cmdWord))
        struct_id = registers[command_get_src1Reg(cmd.cmdWord)];
    else
        struct_id = cmd.cmdWord & 0xF;

    if (structs[struct_id] == NULL) {
        log_error("PRINT_STRUCT struct %d has not been defined", struct_id);
        rt_error(RTE_ABORT);
    }

    log_info("Printing structure %d", struct_id);
    for (int elem_id = 0; elem_id < structs[struct_id]->size; elem_id++) {
        log_info("\t%08X%08X",
                 (structs[struct_id]->elements[elem_id].data & 0xFFFFFFFF00000000LL) >> 32,
                 structs[struct_id]->elements[elem_id].data & 0xFFFFFFFF);
    }
}

//! \brief Check if a parameter of a constructor is read-only.
//! \param[in] constructor_id The id of the constructor whose parameter is
//!                           being checked.
//! \param[in] param_id The id of the parameter being checked.
//! \return 1, if the parameter param_id of the constructor constructor_id
//!            is read only,
//!         0, otherwise
int param_read_only(int constructor_id, int param_id) {
    return !!(constructors[constructor_id].arg_read_only & (1 << param_id));
}

//! \brief Get the id of a specific structure parameter from a CONSTRUCT
//!        command.
//! \param[in] cmd The command to be analysed.
//! \param[in] param_n The id of the parameter to be returned.
//!
//! \return The id of the structure used as the nth parameter in this
//!         constructor.
int get_nth_struct_arg(struct Command cmd, int param_n) {
    return (cmd.dataWords[0] & (0x1F << (6 * param_n))) >> (6 * param_n);
}

//! \brief Execute a START_CONSTRUCTOR command.
//! \param[in] cmd The command to be executed.
void execute_start_constructor(struct Command cmd) {

    int constructor_id = (cmd.cmdWord & 0xF800) >> 11;
    int arg_count      = (cmd.cmdWord & 0x0700) >> 8;
    int read_only_mask = (cmd.cmdWord & 0x001F);

    constructors[constructor_id].start_address  = command_pointer;
    constructors[constructor_id].arg_count     = arg_count;
    constructors[constructor_id].arg_read_only = read_only_mask;

    // Skip all instructions up to END_CONSTRUCTOR.
    struct Command constructorEntry;
    while ((constructorEntry = get_next_command()).opCode != END_CONSTRUCTOR);
}


//! \brief Execute a CONSTRUCT command.
//! \param[in] cmd The command to be executed.
void execute_construct(struct Command cmd) {

    int constructor_id = (cmd.cmdWord & 0x1F00) >> 8;

    // Space to temporarly save the read only structs.
    struct Struct *temp[MAX_STRUCT_ARGS];

    // Save read only structs and swap struct ids such that the first
    // 5 elements of the structs array point to the arguments of the
    // constructor.
    for (int struct_arg_id = 0;
             struct_arg_id < constructors[constructor_id].arg_count;
             struct_arg_id++) {
        int struct_id = get_nth_struct_arg(cmd, struct_arg_id);
        if (param_read_only(constructor_id, struct_arg_id)) {
            temp[struct_arg_id] = struct_create_copy(structs[struct_id]);
        }
        struct Struct *tmp     = structs[struct_id];
        structs[struct_id]     = structs[struct_arg_id];
        structs[struct_arg_id] = tmp;
    }

    // Save the return address.
    stack_push(command_pointer);

    data_specification_executor(constructors[constructor_id].start_address, 0);

    // Restore the return address.
    command_pointer = stack_pop();

    // Restore context.
    for (int struct_arg_id = 0;
             struct_arg_id < constructors[constructor_id].arg_count;
             struct_arg_id++) {
        int struct_id = get_nth_struct_arg(cmd, struct_arg_id);
        if (param_read_only(constructor_id, struct_arg_id)) {
            structs[struct_arg_id] = temp[struct_arg_id];
        }
        struct Struct *tmp     = structs[struct_id];
        structs[struct_id]     = structs[struct_arg_id];
        structs[struct_arg_id] = tmp;
    }
}

//! \brief Execute a READ command.
//! \param[in] cmd The command to be executed.
void execute_read(struct Command cmd) {

    int dest_id = command_get_destReg(cmd.cmdWord);

    int data_len = cmd.cmdWord & 0xF;

    switch (data_len) {
        case 1:
            registers[dest_id]
                  = *((uint8_t*)memory_regions[current_region]->write_pointer);
            break;
        case 2:
            registers[dest_id]
                  = *((uint16_t*)memory_regions[current_region]->write_pointer);
            break;
        case 4:
            registers[dest_id]
                  = *((uint32_t*)memory_regions[current_region]->write_pointer);
            break;
        case 8:
            registers[dest_id]
                  = *((uint64_t*)memory_regions[current_region]->write_pointer);
            break;
        default:
            log_error("READ unsupported size %d", data_len);
            rt_error(RTE_ABORT);
    }

    memory_regions[current_region]->write_pointer += data_len;
}

//! \brief Execute a GET_WR_PTR command.
//! \param[in] cmd The command to be executed.
void execute_get_wr_ptr(struct Command cmd) {
    int dest_reg = (cmd.cmdWord & 0xF000) >> 12;
    registers[dest_reg] = (long)(memory_regions[current_region]->write_pointer
                               - memory_regions[current_region]->start_address);
}

//! \brief Execute a SET_WR_PTR command.
//! \param[in] cmd The command to be executed.
void execute_set_wr_ptr(struct Command cmd) {
    int64_t source;
    if (command_src1_in_use(cmd.cmdWord)) {
        source = registers[command_get_src1Reg(cmd.cmdWord)];
    } else
        source = cmd.dataWords[0];

    uint8_t relative_addressing = cmd.cmdWord & 0x01;

    // If relative addressing is used
    if (relative_addressing)
        memory_regions[current_region]->write_pointer += source;
    else
        memory_regions[current_region]->write_pointer =
            (uint8_t*)(memory_regions[current_region]->start_address + source);
}


//! \brief Execute an IF command.
//! \param[in] cmd The command to be executed.
void execute_if(struct Command cmd) {
    uint8_t operation = cmd.cmdWord & 0x0F;

    uint8_t op_result;

    int64_t source1 = registers[command_get_src1Reg(cmd.cmdWord)];
    int64_t source2 = 0;

    if (command_src2_in_use(cmd.cmdWord))
        source2 = registers[command_get_src2Reg(cmd.cmdWord)];
    else
        source2 = cmd.dataWords[0];

    switch (operation) {
        case 0x00: op_result = source1 == source2; break;
        case 0x01: op_result = source1 != source2; break;
        case 0x02: op_result = source1 <= source2; break;
        case 0x03: op_result = source1 <  source2; break;
        case 0x04: op_result = source1 >= source2; break;
        case 0x05: op_result = source1 >  source2; break;
        case 0x06: op_result = source1 == 0;       break;
        case 0x07: op_result = source1 != 0;       break;
    }

    if (op_result == 0) {
        // Skip all instructions up to ELSE or END_IF.
        struct Command command = get_next_command();
        while (command.opCode != ELSE && command.opCode != END_IF) {
             command = get_next_command();
        }
    }
}

//! \brief Execute an ELSE command.
//! \param[in] cmd The command to be executed.
void execute_else(struct Command cmd) {
    // Skip all instructions up to END_IF.
    struct Command command;
    while ((command = get_next_command()).opCode != END_IF);
}

//! \brief Execute a PRINT_VAL command.
//! \param[in] cmd The command to be executed.
void execute_print_val(struct Command cmd) {
    if (command_src1_in_use(cmd.cmdWord)) {
        uint64_t data = registers[command_get_src1Reg(cmd.cmdWord)];
        log_info("Register %d has value %08X%08X",
                 command_get_src1Reg(cmd.cmdWord),
                 (uint32_t)((data % 0xFFFFFFFF00000000LL) >> 32),
                 (uint32_t)(data & 0xFFFFFFFFF));
    } else if (cmd.dataLength == 1) {
        log_info("Value %08X", cmd.dataWords[0]);
    } else {
        log_info("Value %08X%08X", cmd.dataWords[0], cmd.dataWords[1]);
    }
}

//! \brief Execute a ARITH_OP command.
//! \param[in] cmd The command to be executed.
void execute_arith_op(struct Command cmd) {
    uint8_t sgn = (cmd.cmdWord & (0x1 << 19)) >> 19;

    uint8_t dest_reg = command_get_destReg(cmd.cmdWord);

    uint64_t source1;
    if (command_src1_in_use(cmd.cmdWord))
        source1 = registers[command_get_src1Reg(cmd.cmdWord)];
    else {
        source1 = cmd.dataWords[0];
        source1 |= (source1 & 0x80000000) ? 0xFFFFFFFF00000000LL : 0;
    }

    uint64_t source2;
    if (command_src2_in_use(cmd.cmdWord))
        source2 = registers[command_get_src2Reg(cmd.cmdWord)];
    else if (!command_src1_in_use(cmd.cmdWord)) {
        source2 = cmd.dataWords[1];
        source2 |= (source2 & 0x80000000) ? 0xFFFFFFFF00000000LL : 0;
    } else {
        source2 = cmd.dataWords[0];
        source2 |= (source2 & 0x80000000) ? 0xFFFFFFFF00000000LL : 0;
    }

    uint8_t operation = cmd.cmdWord & 0x0F;

    uint64_t result = 0;
    if (sgn) {
        switch (operation) {
            case 0:
                result = (int64_t)source1 + (int64_t)source2;
                break;
            case 1:
                result = (int64_t)source1 - (int64_t)source2;
                break;
            case 2:
                result = (int64_t)source1 * (int64_t)source2;
                break;
            default:
                log_error("Unknown arithmetic operation");
                rt_error(RTE_ABORT);
        }
    } else {
        switch (operation) {
            case 0:
                result = source1 + source2;
                break;
            case 1:
                result = source1 - source2;
                break;
            case 2:
                result = source1 * source2;
                break;
            default:
                log_error("Unknown arithmetic operation");
                rt_error(RTE_ABORT);
        }
    }
    registers[dest_reg] = result;
}

//! \brief Execute a part of a data specification.
//!        Assumes the given slice of data specification is atomic and
//!        valid.
//! \param[in] ds_start The start address of the data spec.
//! \param[in] ds_size  The size of the data spec. Must be divisible by 4.
//!                     If ds_size is 0, DSE will run until a stopping command
//!                     is reached.
void data_specification_executor(address_t ds_start, uint32_t ds_size) {

    // Pointer to the next command to be executed.
    command_pointer = ds_start;

    // Pointer to the end of the data spec memory region.
    address_t ds_end = ds_start + (ds_size >> 2);

    struct Command cmd;

    // Dummy value of the opCode.
    cmd.opCode = 0x00;

    while ((ds_size != 0 ? command_pointer < ds_end : 1) && cmd.opCode != END_SPEC) {
        cmd = get_next_command();
        switch (cmd.opCode) {
            case BREAK:
                // This command stops the execution of the data spec and
                // outputs an error in the log.
                log_error("BREAK encountered");
                rt_error(RTE_ABORT);
                return;
            case NOP:
                // This command executes no operation.
                break;
            case RESERVE:
                execute_reserve(cmd);
                break;
            case FREE:
                execute_free(cmd);
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
                execute_start_struct(cmd);
                break;
            case STRUCT_ELEM:
                break;
            case END_STRUCT:
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
                execute_start_constructor(cmd);
                break;
            case END_CONSTRUCTOR:
                log_debug("Constructor ended");
                return;
            case CONSTRUCT:
                execute_construct(cmd);
                break;
            case READ:
                execute_read(cmd);
                break;
            case WRITE:
                execute_write(cmd);
                break;
            case WRITE_ARRAY:
                execute_write_array(cmd);
                break;
            case WRITE_STRUCT:
                execute_write_struct(cmd);
                break;
            case BLOCK_COPY:
                log_error("Unimplemented DSE command BLOCK_COPY");
                break;
            case SWITCH_FOCUS:
                execute_switch_focus(cmd);
                break;
            case LOOP:
                execute_loop(cmd);
                break;
            case BREAK_LOOP:
                return;
            case END_LOOP:
                return;
            case IF:
                execute_if(cmd);
                break;
            case ELSE:
                execute_else(cmd);
                break;
            case END_IF:
                break;
            case MV:
                execute_mv(cmd);
                break;
            case GET_WR_PTR:
                execute_get_wr_ptr(cmd);
                break;
            case SET_WR_PTR:
                execute_set_wr_ptr(cmd);
                break;
            case ALIGN_WR_PTR:
                log_error("Unimplemented DSE command ALIGN_WR_PTR");
                break;
            case ARITH_OP:
                execute_arith_op(cmd);
                break;
            case LOGIC_OP:
                execute_logic_op(cmd);
                break;
            case REFORMAT:
                log_error("Unimplemented DSE command REFORMAT");
                break;
            case COPY_STRUCT:
                log_error("Unimplemented DSE command COPY_STRUCT");
                break;
            case COPY_PARAM:
                execute_copy_param(cmd);
                break;
            case WRITE_PARAM:
                execute_write_param(cmd);
                break;
            case READ_PARAM:
                execute_read_param(cmd);
                break;
            case WRITE_PARAM_COMPONENT:
                log_error("Unimplemented DSE command WRITE_PARAM_COMPONENT");
                break;
            case PRINT_VAL:
                execute_print_val(cmd);
                break;
            case PRINT_TXT:
                execute_print_text(cmd);
                break;
            case PRINT_STRUCT:
                execute_print_struct(cmd);
                break;
            case END_SPEC:
                log_info("End of spec has been reached");
                spin1_exit(0);
                break;
            default:
                log_error("Not a DSE command: %x", cmd.opCode);
                rt_error(RTE_ABORT);
        }
    }
}

