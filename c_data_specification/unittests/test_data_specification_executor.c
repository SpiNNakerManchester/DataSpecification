#include <cutter.h>
#include "data_specification_executor.h"

uint8_t command_get_length(uint32_t command);
enum OpCode command_get_opcode(uint32_t command);
uint8_t command_get_fieldUsage(uint32_t command);
uint8_t command_get_destReg(uint32_t command);
uint8_t command_get_src1Reg(uint32_t command);
uint8_t command_get_src2Reg(uint32_t command);
int command_dest_in_use(uint32_t command);
int command_src1_in_use(uint32_t command);
int command_src2_in_use(uint32_t command);
struct Command get_next_command();

extern address_t command_pointer;
extern struct MemoryRegion *memory_regions[MAX_MEM_REGIONS];
extern int current_region;
extern uint64_t registers[MAX_REGISTERS];

void execute_reserve(struct Command cmd);
void execute_free(struct Command cmd);
void execute_switch_focus(struct Command cmd);
void execute_write(struct Command cmd);
void execute_write_array(struct Command cmd);
void execute_get_wr_ptr(struct Command cmd);
void execute_set_wr_ptr(struct Command cmd);
void execute_read(struct Command cmd);
void execute_reset_wr_ptr(struct Command cmd);

void cut_teardown() {
    for (int i = 0; i < MAX_MEM_REGIONS; i++) {
        if (memory_regions[i] != NULL) {
            free(memory_regions[i]->start_address);
            free(memory_regions[i]);
            memory_regions[i] = NULL;
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
    uint32_t commands[] = {0x9DB703A7, 0x2B52EA07,
                           0xA6AA233C, 0x343A207B, 0x6BD67CE5,
                           0x58FE1B19, 0x263CBFCD,
                           0x920A1C38, 0x6BC65B04,
                           0x5C84BE6A, 0x05E2FC3B,
                           0xF7CD26BE, 0xC5C94996, 0x21ABFBBC, 0x000000F0};

    command_pointer = commands;

    struct Command cmd;

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
    uint32_t commands[] = {0x12000000, 0x00000100,
                           0x12000001, 0x00000200,
                           0x12000082, 0x00000201,
                           0x12000083, 0x00000022,
                           0x12000084, 0x00000000,
                           0x1200000F, 0x00000011};

    command_pointer = commands;

    for (int i = 0; i < sizeof(commands) / 8; i++)
        execute_reserve(get_next_command());

    for (int i = 0; i < MAX_MEM_REGIONS; i++)
        if (i > 4 && i != 0xF)
            cut_assert_null(memory_regions[i]);
        else
            cut_assert_not_null(memory_regions[i]);

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
    uint32_t reserve_memory_commands[] = {0x12000000, 0x00000100,
                                          0x12000001, 0x00000200,
                                          0x12000082, 0x00000201,
                                          0x12000083, 0x00000022,
                                          0x12000084, 0x00000004,
                                          0x1200000F, 0x00000011};

    command_pointer = reserve_memory_commands;

    for (int i = 0; i < sizeof(reserve_memory_commands) / 8; i++)
        execute_reserve(get_next_command());

    uint32_t free_memory_commands[] = {0x03000000,
                                       0x03000001,
                                       0x03000002,
                                       0x03000003,
                                       0x03000004,
                                       0x0300000F};

    command_pointer = free_memory_commands;

    for (int i = 0; i < sizeof(free_memory_commands) / 4; i++)
        execute_free(get_next_command());

    for (int i = 0; i < MAX_MEM_REGIONS; i++)
        cut_assert_null(memory_regions[i]);
}

void test_execute_switch_focus() {
    uint32_t reserve_memory_commands[] = {0x12000000, 0x00000100,
                                          0x12000001, 0x00000200,
                                          0x12000082, 0x00000201,
                                          0x12000083, 0x00000022,
                                          0x12000084, 0x00000004,
                                          0x1200000F, 0x00000011};

    command_pointer = reserve_memory_commands;

    for (int i = 0; i < sizeof(reserve_memory_commands) / 8; i++)
        execute_reserve(get_next_command());

    uint32_t switch_focus_commands[] = {0x05000000,
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

    uint32_t switch_focus_register_commands[] = {0x05020500,
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
    uint32_t commands[] = {0x12000000, 0x00000100,
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

    for (int i = 0; i < 8; i++)
        execute_write(get_next_command());

    const char *memory =
                    cut_take_memory((void*)(memory_regions[0]->start_address));

    uint32_t out[] = {0x12345678,
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
    uint32_t commands[] = {0x12000000, 0x00000100,
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

    for (int i = 0; i < 2; i++)
        execute_write_array(get_next_command());

    const char *memory =
                    cut_take_memory((void*)(memory_regions[0]->start_address));

    uint32_t out[] = {0x01234567,
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
    uint32_t commands[] = {0x12000000, 0x00000100,
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

    int out[] = {16, 24, 28, 60};

    for (int i = 0; i < 4; i++) {
        execute_write(get_next_command());
        execute_get_wr_ptr(get_next_command());
        cut_assert_equal_int(out[i], registers[i]);
    }
}

void test_execute_set_wr_ptr(struct Command cmd) {
    uint32_t commands[] = {0x12000000, 0x00000100,
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

    int out[] = {5, 99, 0, 10, 0};

    for (int i = 0; i < 5; i++) {
        execute_set_wr_ptr(get_next_command());
        int diff = memory_regions[current_region]->write_pointer
                 - memory_regions[current_region]->start_address;
        cut_assert_equal_int(out[i], diff);
    }
}

void test_execute_read() {
    uint32_t commands[] = {0x12000000, 0x00000100,
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

    long long out[] = {0x1234567812345678LL, 0x12345678, 0xABCD, 0xCD, 0xAB,
                       0xABABABAB};

    for (int i = 0; i < 6; i++) {
        execute_read(get_next_command());
        cut_assert_equal_int(out[i], registers[i]);
    }
}

void test_execute_logic_op() {
    uint32_t commands[] = {,

    registers[0] = 0x12345678;
    registers[1] = 0xFFFFFFFF;
    registers[2] = 0x00000000;
}

