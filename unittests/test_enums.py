import unittest
import decimal
from data_specification.enums import (
    ArithmeticOperation, Commands, Condition, DataType, LogicOperation,
    RandomNumberGenerator)


class TestingEnums(unittest.TestCase):
    def test_arithmetic_operation_enum(self):
        self.assertEquals(ArithmeticOperation.ADD.value, 0)
        self.assertEquals(ArithmeticOperation.SUBTRACT.value, 1)
        self.assertEquals(ArithmeticOperation.MULTIPLY.value, 2)

    def test_condition_enum(self):
        self.assertEquals(Condition.EQUAL.value, 0)
        self.assertEquals(Condition.NOT_EQUAL.value, 1)
        self.assertEquals(Condition.LESS_THAN_OR_EQUAL.value, 2)
        self.assertEquals(Condition.LESS_THAN.value, 3)
        self.assertEquals(Condition.GREATER_THAN_OR_EQUAL.value, 4)
        self.assertEquals(Condition.GREATER_THAN.value, 5)

    def test_rng_enum(self):
        self.assertEquals(RandomNumberGenerator.MERSENNE_TWISTER.value, 0)

    def test_logic_operation_enum(self):
        self.assertEquals(LogicOperation.LEFT_SHIFT.value, 0)
        self.assertEquals(LogicOperation.RIGHT_SHIFT.value, 1)
        self.assertEquals(LogicOperation.OR.value, 2)
        self.assertEquals(LogicOperation.AND.value, 3)
        self.assertEquals(LogicOperation.XOR.value, 4)
        self.assertEquals(LogicOperation.NOT.value, 5)

    def test_commands_enum(self):
        self.assertEquals(Commands.BREAK.value, 0x00)
        self.assertEquals(Commands.NOP.value, 0x01)
        self.assertEquals(Commands.RESERVE.value, 0x02)
        self.assertEquals(Commands.FREE.value, 0x03)
        self.assertEquals(Commands.DECLARE_RNG.value, 0x05)

        self.assertEquals(Commands.DECLARE_RANDOM_DIST.value, 0x06)
        self.assertEquals(Commands.GET_RANDOM_NUMBER.value, 0x07)
        self.assertEquals(Commands.START_STRUCT.value, 0x10)
        self.assertEquals(Commands.STRUCT_ELEM.value, 0x11)
        self.assertEquals(Commands.END_STRUCT.value, 0x12)

        self.assertEquals(Commands.START_CONSTRUCTOR.value, 0x20)
        self.assertEquals(Commands.END_CONSTRUCTOR.value, 0x25)
        self.assertEquals(Commands.CONSTRUCT.value, 0x40)
        self.assertEquals(Commands.READ.value, 0x41)
        self.assertEquals(Commands.WRITE.value, 0x42)

        self.assertEquals(Commands.WRITE_ARRAY.value, 0x43)
        self.assertEquals(Commands.WRITE_STRUCT.value, 0x44)
        self.assertEquals(Commands.BLOCK_COPY.value, 0x45)
        self.assertEquals(Commands.SWITCH_FOCUS.value, 0x50)
        self.assertEquals(Commands.LOOP.value, 0x51)

        self.assertEquals(Commands.BREAK_LOOP.value, 0x52)
        self.assertEquals(Commands.END_LOOP.value, 0x53)
        self.assertEquals(Commands.IF.value, 0x55)
        self.assertEquals(Commands.ELSE.value, 0x56)
        self.assertEquals(Commands.END_IF.value, 0x57)

        self.assertEquals(Commands.MV.value, 0x60)
        self.assertEquals(Commands.GET_WR_PTR.value, 0x63)
        self.assertEquals(Commands.SET_WR_PTR.value, 0x64)
        self.assertEquals(Commands.ALIGN_WR_PTR.value, 0x65)

        self.assertEquals(Commands.ARITH_OP.value, 0x67)
        self.assertEquals(Commands.LOGIC_OP.value, 0x68)
        self.assertEquals(Commands.REFORMAT.value, 0x6A)
        self.assertEquals(Commands.COPY_STRUCT.value, 0x70)
        self.assertEquals(Commands.COPY_PARAM.value, 0x71)

        self.assertEquals(Commands.WRITE_PARAM.value, 0x72)
        self.assertEquals(Commands.READ_PARAM.value, 0x73)
        self.assertEquals(Commands.WRITE_PARAM_COMPONENT.value, 0x74)
        self.assertEquals(Commands.PRINT_VAL.value, 0x80)
        self.assertEquals(Commands.PRINT_TXT.value, 0X81)

        self.assertEquals(Commands.PRINT_STRUCT.value, 0x82)
        self.assertEquals(Commands.END_SPEC.value, 0XFF)

    def test_data_type_enum(self):
        self.assertEquals(DataType.UINT8.value, 0)
        self.assertEquals(DataType.UINT8.size, 1)
        self.assertEquals(DataType.UINT8.min, 0)
        self.assertEquals(DataType.UINT8.max, 255)

        self.assertEquals(DataType.UINT16.value, 1)
        self.assertEquals(DataType.UINT16.size, 2)
        self.assertEquals(DataType.UINT16.min, 0)
        self.assertEquals(DataType.UINT16.max, 0xFFFF)

        self.assertEquals(DataType.UINT32.value, 2)
        self.assertEquals(DataType.UINT32.size, 4)
        self.assertEquals(DataType.UINT32.min, 0)
        self.assertEquals(DataType.UINT32.max, 0xFFFFFFFF)

        self.assertEquals(DataType.UINT64.value, 3)
        self.assertEquals(DataType.UINT64.size, 8)
        self.assertEquals(DataType.UINT64.min, 0)
        self.assertEquals(DataType.UINT64.max, 0xFFFFFFFFFFFFFFFF)

        self.assertEquals(DataType.INT8.value, 4)
        self.assertEquals(DataType.INT8.size, 1)
        self.assertEquals(DataType.INT8.min, -128)
        self.assertEquals(DataType.INT8.max, 127)

        self.assertEquals(DataType.INT16.value, 5)
        self.assertEquals(DataType.INT16.size, 2)
        self.assertEquals(DataType.INT16.min, -32768)
        self.assertEquals(DataType.INT16.max, 32767)

        self.assertEquals(DataType.INT32.value, 6)
        self.assertEquals(DataType.INT32.size, 4)
        self.assertEquals(DataType.INT32.min, -2147483648)
        self.assertEquals(DataType.INT32.max, 2147483647)

        self.assertEquals(DataType.INT64.value, 7)
        self.assertEquals(DataType.INT64.size, 8)
        self.assertEquals(DataType.INT64.min, -9223372036854775808)
        self.assertEquals(DataType.INT64.max, 9223372036854775807)

        self.assertEquals(DataType.U88.value, 8)
        self.assertEquals(DataType.U88.size, 2)
        self.assertEquals(DataType.U88.min, decimal.Decimal("0"))
        self.assertEquals(DataType.U88.max, decimal.Decimal("255.99609375"))

        self.assertEquals(DataType.U1616.value, 9)
        self.assertEquals(DataType.U1616.size, 4)
        self.assertEquals(DataType.U1616.min, decimal.Decimal("0"))
        self.assertEquals(DataType.U1616.max, decimal.Decimal("65535.9999847"))

        self.assertEquals(DataType.U3232.value, 10)
        self.assertEquals(DataType.U3232.size, 8)
        self.assertEquals(DataType.U3232.min, decimal.Decimal("0"))
        self.assertEquals(
            DataType.U3232.max,
            decimal.Decimal("4294967295.99999999976716935634613037109375"))

        self.assertEquals(DataType.S87.value, 11)
        self.assertEquals(DataType.S87.size, 2)
        self.assertEquals(DataType.S87.min, decimal.Decimal("-256"))
        self.assertEquals(DataType.S87.max, decimal.Decimal("255.9921875"))

        self.assertEquals(DataType.S1615.value, 12)
        self.assertEquals(DataType.S1615.size, 4)
        self.assertEquals(DataType.S1615.min, decimal.Decimal("-65536"))
        self.assertEquals(
            DataType.S1615.max, decimal.Decimal("65535.999969482421875"))

        self.assertEquals(DataType.S3231.value, 13)
        self.assertEquals(DataType.S3231.size, 8)
        self.assertEquals(DataType.S3231.min, decimal.Decimal("-4294967296"))
        self.assertEquals(
            DataType.S3231.max,
            decimal.Decimal("4294967295.9999999995343387126922607421875"))

        self.assertEquals(DataType.U08.value, 16)
        self.assertEquals(DataType.U08.size, 1)
        self.assertEquals(DataType.U08.min, decimal.Decimal("0"))
        self.assertEquals(DataType.U08.max, decimal.Decimal("0.99609375"))

        self.assertEquals(DataType.U016.value, 17)
        self.assertEquals(DataType.U016.size, 2)
        self.assertEquals(DataType.U016.min, decimal.Decimal("0"))
        self.assertEquals(DataType.U016.max, decimal.Decimal("0.999984741211"))

        self.assertEquals(DataType.U032.value, 18)
        self.assertEquals(DataType.U032.size, 4)
        self.assertEquals(DataType.U032.min, decimal.Decimal("0"))
        self.assertEquals(
            DataType.U032.max,
            decimal.Decimal("0.99999999976716935634613037109375"))

        self.assertEquals(DataType.U064.value, 19)
        self.assertEquals(DataType.U064.size, 8)
        self.assertEquals(DataType.U064.min, decimal.Decimal("0"))
        self.assertEquals(
            DataType.U064.max,
            decimal.Decimal("0.999999999999999999945789891375724"
                            "7782996273599565029"))

        self.assertEquals(DataType.S07.value, 20)
        self.assertEquals(DataType.S07.size, 1)
        self.assertEquals(DataType.S07.min, decimal.Decimal("-1"))
        self.assertEquals(DataType.S07.max, decimal.Decimal("0.9921875"))

        self.assertEquals(DataType.S015.value, 21)
        self.assertEquals(DataType.S015.size, 2)
        self.assertEquals(DataType.S015.min, decimal.Decimal("-1"))
        self.assertEquals(
            DataType.S015.max,
            decimal.Decimal("0.999969482421875"))

        self.assertEquals(DataType.S031.value, 22)
        self.assertEquals(DataType.S031.size, 4)
        self.assertEquals(DataType.S031.min, decimal.Decimal("-1"))
        self.assertEquals(
            DataType.S031.max,
            decimal.Decimal("0.99999999976716935634613037109375"))

        self.assertEquals(DataType.S063.value, 23)
        self.assertEquals(DataType.S063.size, 8)
        self.assertEquals(DataType.S063.min, decimal.Decimal("-1"))
        self.assertEquals(
            DataType.S063.max,
            decimal.Decimal("0.99999999999999999989157978275144"
                            "95565992547199130058"))


if __name__ == '__main__':
    unittest.main()
