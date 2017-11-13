#include <cutter.h>
#include "data_specification_executor.h"
#include "struct.h"

uint8_t command_get_length(uint32_t command);
OpCode command_get_opcode(uint32_t command);
uint8_t command_get_fieldUsage(uint32_t command);
uint8_t command_get_destReg(uint32_t command);
uint8_t command_get_src1Reg(uint32_t command);
uint8_t command_get_src2Reg(uint32_t command);
int command_dest_in_use(uint32_t command);
int command_src1_in_use(uint32_t command);
int command_src2_in_use(uint32_t command);
Command get_next_command();

extern address_t command_pointer;
extern MemoryRegion *memory_regions[MAX_MEM_REGIONS];
extern int current_region;
extern uint64_t registers[MAX_REGISTERS];
extern Struct *structs[MAX_STRUCTS];

void execute_reserve(Command cmd);
void execute_free(Command cmd);
void execute_switch_focus(Command cmd);
void execute_write(Command cmd);
void execute_write_array(Command cmd);
void execute_get_wr_ptr(Command cmd);
void execute_set_wr_ptr(Command cmd);
void execute_read(Command cmd);
void execute_reset_wr_ptr(Command cmd);
void execute_logic_op(Command cmd);
void execute_start_struct(Command cmd);
void execute_mv(Command cmd);
void execute_arith_op(Command cmd);
void execute_if(Command cmd);
void execute_copy_param(Command cmd);
void execute_print_text(Command cmd);
void execute_print_val(Command cmd);
void execute_read_param(Command cmd);
void execute_write_param(Command cmd);
void execute_loop(Command cmd);
void execute_write_struct(Command cmd);
void execute_print_struct(Command cmd);
void execute_copy_struct(Command cmd);
void execute_align_wr_ptr(Command cmd);
void execute_block_copy(Command cmd);

void cut_teardown() {
    for (int i = 0; i < MAX_MEM_REGIONS; i++) {
        if (memory_regions[i] != NULL) {
            free(memory_regions[i]->start_address);
            free(memory_regions[i]);
            memory_regions[i] = NULL;
        }
    }
    for (int i = 0; i < MAX_STRUCTS; i++) {
        if (structs[i] != NULL) {
            free(structs[i]->elements);
            free(structs[i]);
            structs[i] = NULL;
        }
    }
}

void test_command_get_length() {
    cut_assert_equal_int(0x00, command_get_length(0x01333567));
    cut_assert_equal_int(0x01, command_get_length(0x53234567));
    cut_assert_equal_int(0x02, command_get_length(0x23234567));
    cut_assert_equal_int(0x03, command_get_length(0x74444567));
    cut_assert_equal_int(0x03, command_get_length(0xF3784922));
}

void test_command_get_opcode() {
    cut_assert_equal_int(0x23, command_get_opcode(0x12345678));
    cut_assert_equal_int(0x45, command_get_opcode(0x04500000));
    cut_assert_equal_int(0x55, command_get_opcode(0x15511111));
    cut_assert_equal_int(0xFA, command_get_opcode(0x0FA12345));
    cut_assert_equal_int(0x99, command_get_opcode(0xF9912345));
}

void test_command_get_fieldUsage() {
    cut_assert_equal_int(0x04, command_get_fieldUsage(0x12345678));
    cut_assert_equal_int(0x00, command_get_fieldUsage(0x04500000));
    cut_assert_equal_int(0x01, command_get_fieldUsage(0x15511111));
    cut_assert_equal_int(0x05, command_get_fieldUsage(0x0FA52345));
    cut_assert_equal_int(0x02, command_get_fieldUsage(0xF9922345));
    cut_assert_equal_int(0x06, command_get_fieldUsage(0x0FA62345));
    cut_assert_equal_int(0x07, command_get_fieldUsage(0xF9972345));
    cut_assert_equal_int(0x07, command_get_fieldUsage(0xF99F2345));
}

void test_command_get_destReg() {
    cut_assert_equal_int(0x00, command_get_destReg(0xB7A20FF0));
    cut_assert_equal_int(0x01, command_get_destReg(0xE1031E85));
    cut_assert_equal_int(0x02, command_get_destReg(0x2C2422DF));
    cut_assert_equal_int(0x03, command_get_destReg(0x32E23480));
    cut_assert_equal_int(0x04, command_get_destReg(0x78954325));
    cut_assert_equal_int(0x05, command_get_destReg(0xBF225F65));
    cut_assert_equal_int(0x06, command_get_destReg(0x379661AB));
    cut_assert_equal_int(0x07, command_get_destReg(0x9340719C));
    cut_assert_equal_int(0x08, command_get_destReg(0x59F2860C));
    cut_assert_equal_int(0x09, command_get_destReg(0xCEB19A7F));
    cut_assert_equal_int(0x0A, command_get_destReg(0xDB82A5D2));
    cut_assert_equal_int(0x0B, command_get_destReg(0x7567BD0F));
    cut_assert_equal_int(0x0C, command_get_destReg(0x0522CDF5));
    cut_assert_equal_int(0x0D, command_get_destReg(0x10E2D183));
    cut_assert_equal_int(0x0E, command_get_destReg(0xEB02E275));
    cut_assert_equal_int(0x0F, command_get_destReg(0x2E02F56F));
}

void test_command_get_src1Reg() {
    cut_assert_equal_int(0x00, command_get_src1Reg(0xB7A2F0F0));
    cut_assert_equal_int(0x01, command_get_src1Reg(0xE103E185));
    cut_assert_equal_int(0x02, command_get_src1Reg(0x2C2422DF));
    cut_assert_equal_int(0x03, command_get_src1Reg(0x32E24380));
    cut_assert_equal_int(0x04, command_get_src1Reg(0x78953425));
    cut_assert_equal_int(0x05, command_get_src1Reg(0xBF22F565));
    cut_assert_equal_int(0x06, command_get_src1Reg(0x379616AB));
    cut_assert_equal_int(0x07, command_get_src1Reg(0x9340179C));
    cut_assert_equal_int(0x08, command_get_src1Reg(0x59F2680C));
    cut_assert_equal_int(0x09, command_get_src1Reg(0xCEB1A97F));
    cut_assert_equal_int(0x0A, command_get_src1Reg(0xDB825AD2));
    cut_assert_equal_int(0x0B, command_get_src1Reg(0x7567DB0F));
    cut_assert_equal_int(0x0C, command_get_src1Reg(0x0522DCF5));
    cut_assert_equal_int(0x0D, command_get_src1Reg(0x10E21D83));
    cut_assert_equal_int(0x0E, command_get_src1Reg(0xEB022E75));
    cut_assert_equal_int(0x0F, command_get_src1Reg(0x2E025F6F));
}

void test_command_get_src2Reg() {
    cut_assert_equal_int(0x00, command_get_src2Reg(0xB7A2FF00));
    cut_assert_equal_int(0x01, command_get_src2Reg(0xE103E815));
    cut_assert_equal_int(0x02, command_get_src2Reg(0x2C242D2F));
    cut_assert_equal_int(0x03, command_get_src2Reg(0x32E24830));
    cut_assert_equal_int(0x04, command_get_src2Reg(0x78953245));
    cut_assert_equal_int(0x05, command_get_src2Reg(0xBF22F655));
    cut_assert_equal_int(0x06, command_get_src2Reg(0x37961A6B));
    cut_assert_equal_int(0x07, command_get_src2Reg(0x9340197C));
    cut_assert_equal_int(0x08, command_get_src2Reg(0x59F2608C));
    cut_assert_equal_int(0x09, command_get_src2Reg(0xCEB1A79F));
    cut_assert_equal_int(0x0A, command_get_src2Reg(0xDB825DA2));
    cut_assert_equal_int(0x0B, command_get_src2Reg(0x7567D0BF));
    cut_assert_equal_int(0x0C, command_get_src2Reg(0x0522DFC5));
    cut_assert_equal_int(0x0D, command_get_src2Reg(0x10E218D3));
    cut_assert_equal_int(0x0E, command_get_src2Reg(0xEB0227E5));
    cut_assert_equal_int(0x0F, command_get_src2Reg(0x2E0256FF));
}

void test_command_dest_in_use() {
    cut_assert_equal_int(0x01, command_dest_in_use(0x12345678));
    cut_assert_equal_int(0x00, command_dest_in_use(0x04500000));
    cut_assert_equal_int(0x00, command_dest_in_use(0x15511111));
    cut_assert_equal_int(0x01, command_dest_in_use(0x0FA52345));
    cut_assert_equal_int(0x00, command_dest_in_use(0xF9922345));
    cut_assert_equal_int(0x01, command_dest_in_use(0x0FA62345));
    cut_assert_equal_int(0x01, command_dest_in_use(0xF9972345));
    cut_assert_equal_int(0x01, command_dest_in_use(0xF99F2345));
}

void test_command_src1_in_use() {
    cut_assert_equal_int(0x00, command_src1_in_use(0x12345678));
    cut_assert_equal_int(0x00, command_src1_in_use(0x04500000));
    cut_assert_equal_int(0x00, command_src1_in_use(0x15511111));
    cut_assert_equal_int(0x00, command_src1_in_use(0x0FA52345));
    cut_assert_equal_int(0x01, command_src1_in_use(0xF9922345));
    cut_assert_equal_int(0x01, command_src1_in_use(0x0FA62345));
    cut_assert_equal_int(0x01, command_src1_in_use(0xF9972345));
    cut_assert_equal_int(0x01, command_src1_in_use(0xF99F2345));
}

void test_command_src2_in_use() {
    cut_assert_equal_int(0x00, command_src2_in_use(0x12345678));
    cut_assert_equal_int(0x00, command_src2_in_use(0x04500000));
    cut_assert_equal_int(0x01, command_src2_in_use(0x15511111));
    cut_assert_equal_int(0x01, command_src2_in_use(0x0FA52345));
    cut_assert_equal_int(0x00, command_src2_in_use(0xF9922345));
    cut_assert_equal_int(0x00, command_src2_in_use(0x0FA62345));
    cut_assert_equal_int(0x01, command_src2_in_use(0xF9972345));
    cut_assert_equal_int(0x01, command_src2_in_use(0xF99F2345));
}

void test_get_next_command() {
    static uint32_t commands[] = {
	    0x9DB703A7, 0x2B52EA07,
	    0xA6AA233C, 0x343A207B, 0x6BD67CE5,
	    0x58FE1B19, 0x263CBFCD,
	    0x920A1C38, 0x6BC65B04,
	    0x5C84BE6A, 0x05E2FC3B,
	    0xF7CD26BE, 0xC5C94996, 0x21ABFBBC, 0x000000F0};

    command_pointer = commands;

    Command cmd;

    cmd = get_next_command();
    cut_assert_equal_int(0x01, cmd.dataLength);
    cut_assert_equal_int(0xDB, cmd.opCode);
    cut_assert_equal_int(0x9DB703A7, cmd.cmdWord);
    cut_assert_equal_int(0x2B52EA07, cmd.dataWords[0]);

    cmd = get_next_command();
    cut_assert_equal_int(0x02, cmd.dataLength);
    cut_assert_equal_int(0x6A, cmd.opCode);
    cut_assert_equal_int(0xA6AA233C, cmd.cmdWord);
    cut_assert_equal_int(0x343A207B, cmd.dataWords[0]);
    cut_assert_equal_int(0x6BD67CE5, cmd.dataWords[1]);

    cmd = get_next_command();
    cut_assert_equal_int(0x01, cmd.dataLength);
    cut_assert_equal_int(0x8F, cmd.opCode);
    cut_assert_equal_int(0x58FE1B19, cmd.cmdWord);
    cut_assert_equal_int(0x263CBFCD, cmd.dataWords[0]);

    cmd = get_next_command();
    cut_assert_equal_int(0x01, cmd.dataLength);
    cut_assert_equal_int(0x20, cmd.opCode);
    cut_assert_equal_int(0x920A1C38, cmd.cmdWord);
    cut_assert_equal_int(0x6BC65B04, cmd.dataWords[0]);

    cmd = get_next_command();
    cut_assert_equal_int(0x01, cmd.dataLength);
    cut_assert_equal_int(0xC8, cmd.opCode);
    cut_assert_equal_int(0x5C84BE6A, cmd.cmdWord);

    cmd = get_next_command();
    cut_assert_equal_int(0x03, cmd.dataLength);
    cut_assert_equal_int(0x7C, cmd.opCode);
    cut_assert_equal_int(0xF7CD26BE, cmd.cmdWord);
    cut_assert_equal_int(0xC5C94996, cmd.dataWords[0]);
    cut_assert_equal_int(0x21ABFBBC, cmd.dataWords[1]);
    cut_assert_equal_int(0x000000F0, cmd.dataWords[2]);
}

void test_execute_reserve() {
    static uint32_t commands[] = {
	    0x10200000, 0x00000100,
	    0x10200001, 0x00000200,
	    0x10200082, 0x00000201,
	    0x10200083, 0x00000022,
	    0x10200084, 0x00000000,
	    0x1020000F, 0x00000011};

    command_pointer = commands;

    for (int i = 0; i < sizeof(commands) / 8; i++) {
        execute_reserve(get_next_command());
    }
    for (int i = 0; i < MAX_MEM_REGIONS; i++) {
        if (i > 4 && i != 0xF) {
            cut_assert_null(memory_regions[i]);
        } else {
            cut_assert_not_null(memory_regions[i]);
        }
    }

    cut_assert_equal_int(memory_regions[0]->size, 0x100);
    cut_assert_equal_int(memory_regions[1]->size, 0x200);
    cut_assert_equal_int(memory_regions[2]->size, 0x204);
    cut_assert_equal_int(memory_regions[3]->size, 0x24);
    cut_assert_equal_int(memory_regions[4]->size, 0x00);
    cut_assert_equal_int(memory_regions[0xF]->size, 0x14);

    cut_assert_equal_int(memory_regions[0]->unfilled, 0);
    cut_assert_equal_int(memory_regions[1]->unfilled, 0);
    cut_assert_equal_int(memory_regions[2]->unfilled, 1);
    cut_assert_equal_int(memory_regions[3]->unfilled, 1);
    cut_assert_equal_int(memory_regions[4]->unfilled, 1);
    cut_assert_equal_int(memory_regions[0xF]->unfilled, 0);

    cut_assert_equal_pointer(memory_regions[0]->start_address,
                             memory_regions[0]->write_pointer);
    cut_assert_equal_pointer(memory_regions[1]->start_address,
                             memory_regions[1]->write_pointer);
    cut_assert_equal_pointer(memory_regions[2]->start_address,
                             memory_regions[2]->write_pointer);
    cut_assert_equal_pointer(memory_regions[3]->start_address,
                             memory_regions[3]->write_pointer);
    cut_assert_equal_pointer(memory_regions[4]->start_address,
                             memory_regions[4]->write_pointer);
    cut_assert_equal_pointer(memory_regions[0xF]->start_address,
                             memory_regions[0xF]->write_pointer);
}

void test_execute_free() {
    static uint32_t reserve_memory_commands[] = {
	    0x10200000, 0x00000100,
	    0x10200001, 0x00000200,
	    0x10200082, 0x00000201,
	    0x10200083, 0x00000022,
	    0x10200084, 0x00000004,
	    0x1020000F, 0x00000011};

    command_pointer = reserve_memory_commands;

    for (int i = 0; i < sizeof(reserve_memory_commands) / 8; i++) {
        execute_reserve(get_next_command());
    }

    static uint32_t free_memory_commands[] = {
	    0x03000000,
	    0x03000001,
	    0x03000002,
	    0x03000003,
	    0x03000004,
	    0x0300000F};

    command_pointer = free_memory_commands;

    for (int i = 0; i < sizeof(free_memory_commands) / 4; i++) {
        execute_free(get_next_command());
    }
    for (int i = 0; i < MAX_MEM_REGIONS; i++) {
        cut_assert_null(memory_regions[i]);
    }
}

void test_execute_switch_focus() {
    static uint32_t reserve_memory_commands[] = {
	    0x10200000, 0x00000100,
	    0x10200001, 0x00000200,
	    0x10200082, 0x00000201,
	    0x10200083, 0x00000022,
	    0x10200084, 0x00000004,
	    0x1020000F, 0x00000011};

    command_pointer = reserve_memory_commands;

    for (int i = 0; i < sizeof(reserve_memory_commands) / 8; i++) {
        execute_reserve(get_next_command());
    }

    static uint32_t switch_focus_commands[] = {
	    0x05000000,
	    0x05000100,
	    0x05000200,
	    0x05000300,
	    0x05000400,
	    0x05000F00};

    command_pointer = switch_focus_commands;

    for (int i = 0; i < sizeof(switch_focus_commands) / 4; i++) {
        execute_switch_focus(get_next_command());
        cut_assert_equal_int((switch_focus_commands[i] & 0xF00) >> 8,
        	current_region);
    }

    registers[5] = 0;
    registers[6] = 1;
    registers[7] = 2;
    registers[8] = 3;
    registers[9] = 4;
    registers[10] = 0xF;

    static uint32_t switch_focus_register_commands[] = {
	    0x05020500,
	    0x05020600,
	    0x05020700,
	    0x05020800,
	    0x05020900,
	    0x05020A00};

    command_pointer = switch_focus_register_commands;

    for (int i = 5; i <= 10; i++) {
        execute_switch_focus(get_next_command());
        cut_assert_equal_int(registers[i], current_region);
    }
}

void test_execute_write() {
    static uint32_t commands[] = {
	    0x10200000, 0x00000100,
	    0x05000000,
	    0x14202001, 0x12345678,
	    0x14201002, 0xABCD,
	    0x14200004, 0xAB,
	    0x24203002, 0x12345678, 0x9ABCDEF0,
	    0x04222102,
	    0x04221102,
	    0x04230230,
	    0x04230230};

    command_pointer = commands;

    registers[1] = 0x12345678;
    registers[2] = 0xAB;
    registers[3] = 2;

    execute_reserve(get_next_command());
    execute_switch_focus(get_next_command());
    for (int i = 0; i < 8; i++) {
        execute_write(get_next_command());
    }

    const char *memory =
	    cut_take_memory((void*)(memory_regions[0]->start_address));

    static uint32_t out[] = {
	    0x12345678,
	    0xABCDABCD,
	    0xABABABAB,
	    0x9ABCDEF0, 0x12345678,
	    0x9ABCDEF0, 0x12345678,
	    0x12345678, 0x12345678,
	    0x56785678,
	    0xABABABAB};

    uint32_t *reader = (uint32_t*)memory;

    for (int i = 0; i < sizeof(out) / 4; i++) {
        cut_assert_equal_int(out[i], reader[i]);
    }

    memory_regions[0] = NULL;
}

void test_execute_write_array() {
    static uint32_t commands[] = {
	    0x10200000, 0x00000100,
	    0x05000000,
	    0x14300004, 0x00000004,
	    0x01234567, 0x9ABCDEF0,
	    0xAABBCCDD, 0x11223344,
	    0x14300002, 0x00000004,
	    0x1234ABCD,
	    0xAABB1234};

    command_pointer = commands;

    execute_reserve(get_next_command());
    execute_switch_focus(get_next_command());

    for (int i = 0; i < 2; i++) {
        execute_write_array(get_next_command());
    }

    const char *memory =
	    cut_take_memory((void*)(memory_regions[0]->start_address));

    static uint32_t out[] = {
	    0x01234567,
	    0x9ABCDEF0,
	    0xAABBCCDD,
	    0x11223344,
	    0x1234ABCD,
	    0xAABB1234};

    uint32_t *reader = (uint32_t*)memory;

    for (int i = 0; i < 6; i++) {
        cut_assert_equal_int(out[i], reader[i]);
    }

    memory_regions[0] = NULL;
}

void test_execute_get_wr_ptr() {
    static uint32_t commands[] = {
	    0x10200000, 0x00000100,
	    0x05000000,
	    0x14202004, 0x12345678,
	    0x06340000,
	    0x14201004, 0xABCD,
	    0x06341000,
	    0x14200004, 0xAB,
	    0x06342000,
	    0x24203004, 0x12345678, 0x9ABCDEF0,
	    0x06343000};

    command_pointer = commands;

    execute_reserve(get_next_command());
    execute_switch_focus(get_next_command());

    static int out[] = {16, 24, 28, 60};

    for (int i = 0; i < 4; i++) {
        execute_write(get_next_command());
        execute_get_wr_ptr(get_next_command());
        cut_assert_equal_int(out[i], registers[i]);
    }
}

void test_execute_set_wr_ptr() {
    static uint32_t commands[] = {
	    0x10200000, 0x00000100,
	    0x05000000,
	    0x16400000, 5,
	    0x16400000, 99,
	    0x16400001, -99,
	    0x06420300,
	    0x06420401};

    registers[3] = 10;
    registers[4] = -10;

    command_pointer = commands;

    execute_reserve(get_next_command());
    execute_switch_focus(get_next_command());

    static int out[] = {5, 99, 0, 10, 0};

    for (int i = 0; i < 5; i++) {
        execute_set_wr_ptr(get_next_command());
        int diff = memory_regions[current_region]->write_pointer
                 - memory_regions[current_region]->start_address;
        cut_assert_equal_int(out[i], diff);
    }
}

void test_execute_read() {
    static uint32_t commands[] = {
	    0x10200000, 0x00000100,
	    0x05000000,
	    0x14202003, 0x12345678,
	    0x14201002, 0xABCD,
	    0x14200004, 0xAB,
	    0x16400000, 0,
	    0x04140008,
	    0x04141004,
	    0x04142002,
	    0x04143001,
	    0x04144001,
	    0x04145004};

    command_pointer = commands;

    execute_reserve(get_next_command());
    execute_switch_focus(get_next_command());
    execute_write(get_next_command());
    execute_write(get_next_command());
    execute_write(get_next_command());
    execute_set_wr_ptr(get_next_command());

    static long long out[] = {
	    0x1234567812345678LL, 0x12345678, 0xABCD, 0xCD, 0xAB,
	    0xABABABAB};

    for (int i = 0; i < 6; i++) {
        execute_read(get_next_command());
        cut_assert_equal_int(out[i], registers[i]);
    }
}

void test_execute_logic_op() {
    static uint32_t commands[] = {
	    0x2684F000, 0xFF, 4,
	    0x2684F001, 0xFF, 4,
	    0x2684F002, 0xF0, 4,
	    0x2684F003, 0xFE, 5,
	    0x2684F004, 0xFE, 5,
	    0x1684F005, 0xFF,

	    0x1686F100, 4,
	    0x1686F101, 4,
	    0x1686F002, 0xFF,
	    0x1686F003, 0xFF,
	    0x1686F004, 0xFF,
	    0x0686F005,

	    0x1685F030, 0xFF,
	    0x1685F031, 0xFF,
	    0x1685F032, 0xF0,
	    0x1685F043, 0xFE,
	    0x1685F044, 0xFE,

	    0x0687F131,
	    0x0687F132,
	    0x0687F052,
	    0x0687F053,
	    0x0687F054};

    registers[0] = 0x12345678;
    registers[1] = 0xFFFFFFFF;
    registers[2] = 0x00000000;
    registers[3] = 0x00000004;
    registers[4] = 0x00000005;
    registers[5] = 0x000000FF;

    command_pointer = commands;

    static long long int out[] = {
	    0xFF0, 0xF, 0xF4, 0x4, 0xFB, ~0xFF,
	    0xFFFFFFFF0, 0x0FFFFFFF, 0x123456FF, 0x78, 0x12345687,
	    0xFF0, 0xF, 0xF4, 0x5, 0x1, ~0xFF,
	    0xFFFFFFF0, 0x0FFFFFFF, 0x123456FF, 0x78, 0x12345687};

    for (int i = 0; i < 7; i++) {
        execute_logic_op(get_next_command());
        cut_assert_equal_int(out[i], registers[15]);
    }
}

void test_execute_start_struct() {
    static uint32_t commands[] = {
	    0x01000004,
	    0x01200000,
	    0x01000008,
	    0x11100000, 0x12,
	    0x11100001, 0x1234,
	    0x11100002, 0x12345678,
	    0x21100003, 0x12345678, 0x90ABCDEF,
	    0x11100004, -1,
	    0x11100005, -1,
	    0x11100006, -1,
	    0x01100007,
	    0x01100008,
	    0x01100009,
	    0x0110000A,
	    0x0110000B,
	    0x01200000};

    command_pointer = commands;

    execute_start_struct(get_next_command());
    execute_start_struct(get_next_command());

    cut_assert_equal_int(0, structs[4]->size);
    cut_assert_equal_int(12, structs[8]->size);

    for (int i = 0; i < 12; i++) {
        cut_assert_equal_int(i, structs[8]->elements[i].type);
    }

    cut_assert_equal_int(0x12, structs[8]->elements[0].data);
    cut_assert_equal_int(0x1234, structs[8]->elements[1].data);
    cut_assert_equal_int(0x12345678, structs[8]->elements[2].data);
    cut_assert_equal_int(0x1234567890ABCDEFLL, structs[8]->elements[3].data);
    cut_assert_equal_int(0xFF, structs[8]->elements[4].data);
    cut_assert_equal_int(0xFFFF, structs[8]->elements[5].data);
    cut_assert_equal_int(0xFFFFFFFF, structs[8]->elements[6].data);
    cut_assert_equal_int(0, structs[8]->elements[7].data);
    cut_assert_equal_int(0, structs[8]->elements[8].data);
    cut_assert_equal_int(0, structs[8]->elements[9].data);
    cut_assert_equal_int(0, structs[8]->elements[10].data);
}

void test_execute_mv() {
    static uint32_t commands[] = {
	    0x26040000, 0xABCDEF12, 0x12345678,
	    0x16048000, 0x11223344,
	    0x16045000, 0x12,
	    0x06062000,
	    0x06063800,
	    0x06064500};

    command_pointer = commands;

    for (int i = 0; i < 6; i++) {
        execute_mv(get_next_command());
    }

    cut_assert_equal_int(0xABCDEF1212345678LL, registers[0]);
    cut_assert_equal_int(0xABCDEF1212345678LL, registers[2]);

    cut_assert_equal_int(0x11223344, registers[8]);
    cut_assert_equal_int(0x11223344, registers[3]);

    cut_assert_equal_int(0x12, registers[4]);
    cut_assert_equal_int(0x12, registers[5]);
}

void test_execute_arith_op() {
    static uint32_t commands[] = {
	    0x2674F000, 0xFF, 4,
	    0x2674F001, 0xFF, 4,
	    0x2674F002, 0xF0, 4,
	    0x267CF000, 0xFE, -1,
	    0x267CF001, 0xFE, -1,
	    0x267CF002, 0xFF, -1,

	    0x1676F100, 4,       //6
	    0x1676F101, -1,
	    0x1676F002, 0xFF,
	    0x167EF000, -1,
	    0x167EF001, 1,
	    0x167EF002, 0,

	    0x1675F030, 0xFF,    //12
	    0x1675F031, 0xFF,
	    0x1675F032, 0xF0,
	    0x167DF040, 1,
	    0x167DF041, -3,
	    0x167DF042, -10,

	    0x0677F130,          //18
	    0x0677F131,
	    0x0677F132,
	    0x0677F050,
	    0x067FF051,
	    0x067FF052};

    command_pointer = commands;

    registers[0] = 0xFF;
    registers[1] = 0x1;
    registers[2] = -1;
    registers[3] = 0x24;
    registers[4] = 0x100;
    registers[5] = -5;

    static long long int out[] = {
	    0xFF + 4,
	    0xFF - 4,
	    0xF0 * 4,
	    0xFD,
	    0xFF,
	    (uint64_t)((int64_t)0xFF * -1LL),
	    5,
	    2,
	    0xFF * 0xFF,
	    (uint64_t)((int64_t)0xFF + -1LL),
	    0xFE,
	    0,
	    0x24 + 0xFF,
	    0xFF - 0x24,
	    0x24 * 0xF0,
	    0x101,
	    -0x103,
	    0x100LL * (-10LL),
	    0x25,
	    (uint64_t)1 - (uint64_t)0x24,
	    0x24,
	    0xFF + (-5),
	    0xFF - (-5),
	    0xFF * (-5)};

    for (int i = 0; i < 24; i++) {
        execute_arith_op(get_next_command());
        cut_assert_equal_int(out[i], registers[15]);
    }
}

void test_execute_if() {
    static uint32_t commands[] = {
	    0x10200000, 0x00000100,
	    0x05000000,

	    0x15520000, 0x12345678,
	    0x14200001, 0x1,
	    0x05700000,
	    0x15520001, 0x12345678,
	    0x14200001, 0x2,
	    0x05700000,
	    0x15520002, 0x12345678,
	    0x14200001, 0x3,
	    0x05700000,
	    0x15520003, 0x12345678,
	    0x14200001, 0x4,
	    0x05700000,
	    0x15520004, 0x12345678,
	    0x14200001, 0x5,
	    0x05700000,
	    0x15520005, 0x12345678,
	    0x14200001, 0x6,
	    0x05700000,

	    0x15520100, 0x12345678,
	    0x14200001, 0x7,
	    0x05700000,
	    0x15520101, 0x12345678,
	    0x14200001, 0x8,
	    0x05700000,
	    0x15520102, 0x12345678,
	    0x14200001, 0x9,
	    0x05700000,
	    0x15520103, 0x12345678,
	    0x14200001, 0xA,
	    0x05700000,
	    0x15520104, 0x12345678,
	    0x14200001, 0xB,
	    0x05700000,
	    0x15520105, 0x12345678,
	    0x14200001, 0xC,
	    0x05700000,

	    0x15520200, 0x12345678,
	    0x14200001, 0x7,
	    0x05700000,
	    0x15520201, 0x12345678,
	    0x14200001, 0x8,
	    0x05700000,
	    0x15520202, 0x12345678,
	    0x14200001, 0x9,
	    0x05700000,
	    0x15520203, 0x12345678,
	    0x14200001, 0xA,
	    0x05700000,
	    0x15520204, 0x12345678,
	    0x14200001, 0xB,
	    0x05700000,
	    0x15522005, 0x12345678,
	    0x14200001, 0xC,
	    0x05700000,

	    0x15520101, 0x12345678,
	    0x14200001, 0xF,
	    0x05600000,
	    0x14200001, 0x10,
	    0x05700000,

	    0x15520102, 0x12345678,
	    0x14200001, 0x11,
	    0x05600000,
	    0x14200001, 0x12,
	    0x05700000,

	    0x15520103, 0x12345678,
	    0x14200001, 0x13,
	    0x05600000,
	    0x14200001, 0x14,
	    0x05700000,

	    0x15520104, 0x12345678,
	    0x14200001, 0x15,
	    0x05600000,
	    0x14200001, 0x16,
	    0x05700000,

	    0x15520105, 0x12345678,
	    0x14200001, 0x18,
	    0x05600000,
	    0x14200001, 0x19,
	    0x05700000,

	    0x15520200, 0x12345678,
	    0x15520200, 0x12345678,
	    0x14200001, 0x20,
	    0x05700000,
	    0x05700000,

	    0x05520006,
	    0x14200001, 0x21,
	    0x05700000,
	    0x05520106,
	    0x14200001, 0x22,
	    0x05700000,
	    0x05520007,
	    0x14200001, 0x23,
	    0x05700000,
	    0x05520107,
	    0x14200001, 0x24,
	    0x05700000,

	    0x05530120,
	    0x14200001, 0x1,
	    0x05700000,
	    0x05530121,
	    0x14200001, 0x2,
	    0x05700000,
	    0x05530122,
	    0x14200001, 0x3,
	    0x05700000,
	    0x05530123,
	    0x14200001, 0x4,
	    0x05700000,
	    0x05530124,
	    0x14200001, 0x5,
	    0x05700000,
	    0x05530125,
	    0x14200001, 0x6,
	    0x05700000,

	    0x0FF00000};

    registers[0] = 0;
    registers[1] = 0xFFFFFFFF;
    registers[2] = 0x12345678;

    data_specification_executor(commands, 0);

    static uint8_t out[] = {
	    0x2, 0x3, 0x4,
	    0x8, 0xB, 0xC,
	    0x7, 0x9, 0xB,
	    0xF, 0x12, 0x14, 0x15, 0x18, 0x20, 0x21, 0x24,
	    0x2, 0x5, 0x6};

    uint8_t *reader = memory_regions[0]->start_address;
    for (int i = 0; i < sizeof(out); i++) {
        cut_assert_equal_int(out[i], *(reader++));
    }
}

void test_execute_copy_param() {
    static uint32_t commands[] = {
	    0x01000004,
	    0x21100003, 0x12345678, 0x90ABCDEF,
	    0x11100002, 0x12345678,
	    0x11100001, 0x1234,
	    0x11100000, 0x12,
	    0x11100004, -1,
	    0x11100005, -1,
	    0x11100006, -1,
	    0x01200000,

	    0x01000008,
	    0x01100006,
	    0x01100005,
	    0x01100004,
	    0x01100000,
	    0x01100001,
	    0x01100002,
	    0x01100003,
	    0x01200000,

	    0x17108400, 0x00000600,
	    0x17108400, 0x00000501,
	    0x17108400, 0x00000402,
	    0x17108400, 0x00000303,
	    0x17108400, 0x00000204,
	    0x17108400, 0x00000105,
	    0x17108400, 0x00000006};

    command_pointer = commands;

    execute_start_struct(get_next_command());
    execute_start_struct(get_next_command());
    for (int i = 0; i < 7; i++) {
        execute_copy_param(get_next_command());
    }

    for (int i = 0; i < 7; i++) {
        cut_assert_equal_int(structs[4]->elements[i].data,
        	structs[8]->elements[6-i].data);
    }
}

void test_execute_print_text() {
    static uint32_t commands[] = {
	    0x17300003, 0x54455354,
	    0x3730000B, 0x44434241, 0x48474645, 0x4C4B4A49};

    command_pointer = commands;

    int pid = cut_fork();
    if (pid==0) {
        execute_print_text(get_next_command());
        execute_print_text(get_next_command());
        exit(EXIT_SUCCESS);
    }

    const char *str = cut_fork_get_stdout_message(pid);
    cut_assert_not_null(strstr(str, "TSET"));
    cut_assert_not_null(strstr(str, "ABCDEFGHIJKL"));
}

void test_execute_print_val() {
    static uint32_t commands[] = {
	    0x18000000, 0x12345678,
	    0x28000000, 0x87654321, 0x90ABCDEF,
	    0x08020300};

    command_pointer = commands;
    registers[3] = 0xF0F0F0F0;

    int pid = cut_fork();
    if (pid==0) {
        execute_print_val(get_next_command());
        execute_print_val(get_next_command());
        execute_print_val(get_next_command());
        exit(EXIT_SUCCESS);
    }

    const char *str = cut_fork_get_stdout_message(pid);
    cut_assert_not_null(strstr(str, "12345678"));
    cut_assert_not_null(strstr(str, "8765432190ABCDEF"));
    cut_assert_not_null(strstr(str, "F0F0F0F0"));
}

void test_execute_print_struct() {
    static uint32_t commands[] = {
	    0x01000004,
	    0x21100003, 0x12345678, 0x90ABCDEF,
	    0x11100002, 0x87654321,
	    0x11100001, 0x8A7B,
	    0x11100000, 0xFF,
	    0x01200000,
	    0x08200004};

    command_pointer = commands;

    execute_start_struct(get_next_command());

    int pid = cut_fork();
    if (pid==0) {
        execute_print_struct(get_next_command());
        exit(EXIT_SUCCESS);
    }

    char *str = cut_fork_get_stdout_message(pid);
    cut_assert_not_null(strstr(str, "1234567890ABCDEF"));
    cut_assert_not_null(strstr(str, "87654321"));
    cut_assert_not_null(strstr(str, "8A7B"));
    cut_assert_not_null(strstr(str, "FF"));
}

void test_execute_read_param() {
    static uint32_t commands[] = {
	    0x01000004,
	    0x21100003, 0x12345678, 0x90ABCDEF,
	    0x11100002, 0x87654321,
	    0x11100001, 0x8A7B,
	    0x11100000, 0xFF,
	    0x01200000,
	    0x07340034,
	    0x07341024,
	    0x07342014,
	    0x07343004,
	    0x07364F04,
	    0x07365E04};

    registers[0xE] = 0;
    registers[0xF] = 2;

    command_pointer = commands;

    execute_start_struct(get_next_command());
    for (int i = 0; i < 6; i++) {
        execute_read_param(get_next_command());
    }

    cut_assert_equal_int(0x1234567890ABCDEFLL,   registers[3]);
    cut_assert_equal_int(0x87654321,             registers[2]);
    cut_assert_equal_int(0x8A7B,                 registers[1]);
    cut_assert_equal_int(0xFF,                   registers[0]);
    cut_assert_equal_int(0x1234567890ABCDEFLL,   registers[5]);
    cut_assert_equal_int(0x8A7B,                 registers[4]);
}

void test_execute_write_param() {
    static uint32_t commands[] = {
	    0x01000004,
	    0x21100003, 0x12345678, 0x90ABCDEF,
	    0x11100002, 0x87654321,
	    0x11100001, 0x8A7B,
	    0x11100000, 0xFF,
	    0x01200000,
	    0x27204000, 0xFBFBFBFB, 0xFBFBFBFB,
	    0x17204001, 0x12121212,
	    0x17204002, 0x3434,
	    0x17204003, 0x56,
	    0x07224F00,
	    0x07224E01,
	    0x07224D02,
	    0x07224C03};

    registers[0xC] = 0xDB;
    registers[0xD] = 0xEFFE;
    registers[0xE] = 0xABCDEFFF;
    registers[0xF] = 0x1234567812345678LL;

    command_pointer = commands;

    execute_start_struct(get_next_command());
    for (int i = 0; i < 4; i++) {
        execute_write_param(get_next_command());
    }

    cut_assert_equal_int(0xFBFBFBFBFBFBFBFBLL, structs[4]->elements[0].data);
    cut_assert_equal_int(0x12121212,           structs[4]->elements[1].data);
    cut_assert_equal_int(0x3434,               structs[4]->elements[2].data);
    cut_assert_equal_int(0x56,                 structs[4]->elements[3].data);

    for (int i = 0; i < 4; i++) {
        execute_write_param(get_next_command());
    }

    cut_assert_equal_int(0x1234567812345678LL, structs[4]->elements[0].data);
    cut_assert_equal_int(0xABCDEFFF,           structs[4]->elements[1].data);
    cut_assert_equal_int(0xEFFE,               structs[4]->elements[2].data);
    cut_assert_equal_int(0xDB,                 structs[4]->elements[3].data);
}

void test_execute_loop() {
    static uint32_t commands[] = {
	    0x35100001, 0x00000004, 0x00000008, 2,
	    0x08020100,
	    0x05300000,

	    0x25143002, 0x00000004, 0x00000001,
	    0x08020200,
	    0x05300000,

	    0x15165604, 0x00000001,
	    0x08020400,
	    0x05300000,

	    0x051798AB,
	    0x08020B00,
	    0x05300000,

	    0x051789A7,
	    0x08020700,
	    0x05300000};

    registers[3] = 0x1;

    registers[5] = 0xA;
    registers[6] = 0x10;

    registers[8] = 0x11;
    registers[9] = 0x25;
    registers[10] = 10;

    command_pointer = commands;

    int pid = cut_fork();
    if (pid==0) {
        for (int i = 0; i < 5; i++) {
            execute_loop(get_next_command());
        }
        exit(EXIT_SUCCESS);
    }

    char *str = cut_fork_get_stdout_message(pid);

    cut_assert_not_null(strstr(str, "0000000000000004"));
    str = strstr(str, "0000000000000004");

    cut_assert_not_null(strstr(str, "0000000000000006"));
    str = strstr(str, "0000000000000006");

    cut_assert_not_null(strstr(str, "0000000000000001"));
    str = strstr(str, "0000000000000001");

    cut_assert_not_null(strstr(str, "0000000000000002"));
    str = strstr(str, "0000000000000002");

    cut_assert_not_null(strstr(str, "0000000000000003"));
    str = strstr(str, "0000000000000003");

    cut_assert_not_null(strstr(str, "000000000000000A"));
    str = strstr(str, "000000000000000A");

    cut_assert_not_null(strstr(str, "000000000000000B"));
    str = strstr(str, "000000000000000B");

    cut_assert_not_null(strstr(str, "000000000000000C"));
    str = strstr(str, "000000000000000C");

    cut_assert_not_null(strstr(str, "000000000000000D"));
    str = strstr(str, "000000000000000D");

    cut_assert_not_null(strstr(str, "000000000000000E"));
    str = strstr(str, "000000000000000E");

    cut_assert_not_null(strstr(str, "000000000000000F"));
    str = strstr(str, "000000000000000F");

    cut_assert_not_null(strstr(str, "0000000000000011"));
    str = strstr(str, "0000000000000011");

    cut_assert_not_null(strstr(str, "000000000000001B"));
    str = strstr(str, "000000000000001B");
}

void test_execute_write_struct() {
    static uint32_t commands[] = {
	    0x10200000, 0x00000100,
	    0x05000000,
	    0x01000004,
	    0x21100003, 0x12345678, 0x90ABCDEF,
	    0x11100002, 0x12345678,
	    0x11100001, 0x1234,
	    0x11100000, 0x12,
	    0x11100004, -1,
	    0x11100005, -1,
	    0x11100006, -1,
	    0x01200000,
	    0x04300204,
	    0x04320304};

    registers[3] = 1;

    command_pointer = commands;

    execute_reserve(get_next_command());
    execute_switch_focus(get_next_command());
    execute_start_struct(get_next_command());

    execute_write_struct(get_next_command());
    execute_write_struct(get_next_command());

    uint8_t *reader = (uint8_t*)memory_regions[0]->start_address;

    for (int i = 0; i < 3; i++) {
        cut_assert_equal_int(0xEF, *(reader++));
        cut_assert_equal_int(0xCD, *(reader++));
        cut_assert_equal_int(0xAB, *(reader++));
        cut_assert_equal_int(0x90, *(reader++));

        cut_assert_equal_int(0x78, *(reader++));
        cut_assert_equal_int(0x56, *(reader++));
        cut_assert_equal_int(0x34, *(reader++));
        cut_assert_equal_int(0x12, *(reader++));

        cut_assert_equal_int(0x78, *(reader++));
        cut_assert_equal_int(0x56, *(reader++));
        cut_assert_equal_int(0x34, *(reader++));
        cut_assert_equal_int(0x12, *(reader++));

        cut_assert_equal_int(0x34, *(reader++));
        cut_assert_equal_int(0x12, *(reader++));

        cut_assert_equal_int(0x12, *(reader++));

        cut_assert_equal_int(0xFF, *(reader++));
        cut_assert_equal_int(0xFF, *(reader++));
        cut_assert_equal_int(0xFF, *(reader++));
        cut_assert_equal_int(0xFF, *(reader++));
        cut_assert_equal_int(0xFF, *(reader++));
        cut_assert_equal_int(0xFF, *(reader++));
        cut_assert_equal_int(0xFF, *(reader++));
    }
}

void test_constructor() {
    static uint32_t commands[] = {
	    0x10200000, 0x00000100,
	    0x05000000,

	    0x01000004,
	    0x11100002, 0xABABABAB,
	    0x01200000,

	    0x01000002,
	    0x11100002, 0x12345678,
	    0x01200000,

	    0x02001A01,

	    0x04400100,
	    0x04400101,

	    0x17200000, 0x11111111,
	    0x17201000, 0x12121212,

	    0x04400100,
	    0x04400101,

	    0x02500000,

	    0x14000300, 0x00000084,

	    0x04400104,
	    0x04400102,
	    0x0FF00000};

    data_specification_executor(commands, 0);

    uint32_t *reader = (uint32_t*)
	    memory_regions[current_region]->start_address;

    cut_assert_equal_int(0xABABABAB, *(reader++));
    cut_assert_equal_int(0x12345678, *(reader++));
    cut_assert_equal_int(0x11111111, *(reader++));
    cut_assert_equal_int(0x12121212, *(reader++));
    cut_assert_equal_int(0xABABABAB, *(reader++));
    cut_assert_equal_int(0x12121212, *(reader++));
}

void test_execute_copy_struct() {
    static uint32_t commands[] = {
	    0x10200000, 0x00000100,
	    0x05000000,

	    0x01000004,
	    0x11100002, 0xABABABAB,
	    0x01200000,

	    0x07001400,
	    0x07041400,
	    0x07023200,
	    0x07063200,

	    0x04400101,
	    0x04400102,
	    0x04400103,
	    0x04400104,
	    0x04400105,
	    0x0FF00000};

    registers[1] = 2;
    registers[2] = 4;
    registers[3] = 5;

    data_specification_executor(commands, 0);

    uint32_t *reader = (uint32_t*)
	    memory_regions[current_region]->start_address;

    for (int i = 0; i < 5; i++) {
        cut_assert_equal_int(0xABABABAB, *(reader++));
    }
}

void test_execute_align_wr_ptr() {
    static uint32_t commands[] = {
	    0x10200000, 0x00004000,
	    0x05000000,

	    0x16400000, 1,
	    0x06500002,

	    0x16400000, 1,
	    0x06543002,

	    0x16400000, 1,
	    0x06564100};

    registers[1] = 1;

    command_pointer = commands;

    execute_reserve(get_next_command());
    execute_switch_focus(get_next_command());

    execute_set_wr_ptr(get_next_command());
    execute_align_wr_ptr(get_next_command());
    cut_assert_equal_int(0,
	    (uint64_t) memory_regions[current_region]->write_pointer & 0x3);

    execute_set_wr_ptr(get_next_command());
    execute_align_wr_ptr(get_next_command());
    cut_assert_equal_int(0,
	    (uint64_t) memory_regions[current_region]->write_pointer & 0x3);
    cut_assert_equal_int(registers[3],
	    (uint64_t) memory_regions[current_region]->write_pointer);

    execute_set_wr_ptr(get_next_command());
    execute_align_wr_ptr(get_next_command());
    cut_assert_equal_int(0,
	    (uint64_t) memory_regions[current_region]->write_pointer & 0x1);
    cut_assert_equal_int(registers[4],
	    (uint64_t) memory_regions[current_region]->write_pointer);
}

void test_execute_block_copy() {
    static uint32_t commands[] = {
	    0x10200000, 0x00004000,
	    0x05000000,
	    0x14202001, 0x12345678,
	    0x14201002, 0xABCD,
	    0x14200004, 0xAB,
	    0x04451C20,
	    0x04473450};

    command_pointer = commands;

    execute_reserve(get_next_command());
    execute_switch_focus(get_next_command());

    execute_write(get_next_command());
    execute_write(get_next_command());
    execute_write(get_next_command());

    registers[1] = (uint64_t)memory_regions[current_region]->write_pointer;
    registers[2] = (uint64_t)memory_regions[current_region]->start_address;

    execute_block_copy(get_next_command());

    memory_regions[current_region]->write_pointer += 12;

    registers[3] = (uint64_t)memory_regions[current_region]->write_pointer;
    registers[4] = 24;
    registers[5] = (uint64_t)memory_regions[current_region]->start_address;

    execute_block_copy(get_next_command());

    uint32_t *reader = (uint32_t*)memory_regions[current_region]->start_address;

    for (int i = 0; i < 3; i++) {
        cut_assert_equal_int(0x12345678, *(reader++));
        cut_assert_equal_int(0xABCDABCD, *(reader++));
        cut_assert_equal_int(0xABABABAB, *(reader++));
    }
}
