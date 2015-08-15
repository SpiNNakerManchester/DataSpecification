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



