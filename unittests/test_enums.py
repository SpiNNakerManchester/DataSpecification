# Copyright (c) 2014 The University of Manchester
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
import decimal
from data_specification.config_setup import unittest_setup
from data_specification.enums import (
    ArithmeticOperation, Commands, Condition, DataType, LogicOperation,
    RandomNumberGenerator)


class TestingEnums(unittest.TestCase):

    def setUp(self):
        unittest_setup()

    def test_arithmetic_operation_enum(self):
        self.assertEqual(ArithmeticOperation.ADD.value, 0)
        self.assertEqual(ArithmeticOperation.SUBTRACT.value, 1)
        self.assertEqual(ArithmeticOperation.MULTIPLY.value, 2)

    def test_condition_enum(self):
        self.assertEqual(Condition.EQUAL.value, 0)
        self.assertEqual(Condition.NOT_EQUAL.value, 1)
        self.assertEqual(Condition.LESS_THAN_OR_EQUAL.value, 2)
        self.assertEqual(Condition.LESS_THAN.value, 3)
        self.assertEqual(Condition.GREATER_THAN_OR_EQUAL.value, 4)
        self.assertEqual(Condition.GREATER_THAN.value, 5)

    def test_rng_enum(self):
        self.assertEqual(RandomNumberGenerator.MERSENNE_TWISTER.value, 0)

    def test_logic_operation_enum(self):
        self.assertEqual(LogicOperation.LEFT_SHIFT.value, 0)
        self.assertEqual(LogicOperation.RIGHT_SHIFT.value, 1)
        self.assertEqual(LogicOperation.OR.value, 2)
        self.assertEqual(LogicOperation.AND.value, 3)
        self.assertEqual(LogicOperation.XOR.value, 4)
        self.assertEqual(LogicOperation.NOT.value, 5)

    def test_commands_enum(self):
        self.assertEqual(Commands.BREAK.value, 0x00)
        self.assertEqual(Commands.NOP.value, 0x01)
        self.assertEqual(Commands.RESERVE.value, 0x02)
        self.assertEqual(Commands.FREE.value, 0x03)
        self.assertEqual(Commands.DECLARE_RNG.value, 0x05)

        self.assertEqual(Commands.DECLARE_RANDOM_DIST.value, 0x06)
        self.assertEqual(Commands.GET_RANDOM_NUMBER.value, 0x07)
        self.assertEqual(Commands.START_STRUCT.value, 0x10)
        self.assertEqual(Commands.STRUCT_ELEM.value, 0x11)
        self.assertEqual(Commands.END_STRUCT.value, 0x12)

        self.assertEqual(Commands.START_CONSTRUCTOR.value, 0x20)
        self.assertEqual(Commands.END_CONSTRUCTOR.value, 0x25)
        self.assertEqual(Commands.CONSTRUCT.value, 0x40)
        self.assertEqual(Commands.READ.value, 0x41)
        self.assertEqual(Commands.WRITE.value, 0x42)

        self.assertEqual(Commands.WRITE_ARRAY.value, 0x43)
        self.assertEqual(Commands.WRITE_STRUCT.value, 0x44)
        self.assertEqual(Commands.BLOCK_COPY.value, 0x45)
        self.assertEqual(Commands.SWITCH_FOCUS.value, 0x50)
        self.assertEqual(Commands.LOOP.value, 0x51)

        self.assertEqual(Commands.BREAK_LOOP.value, 0x52)
        self.assertEqual(Commands.END_LOOP.value, 0x53)
        self.assertEqual(Commands.IF.value, 0x55)
        self.assertEqual(Commands.ELSE.value, 0x56)
        self.assertEqual(Commands.END_IF.value, 0x57)

        self.assertEqual(Commands.MV.value, 0x60)
        self.assertEqual(Commands.GET_WR_PTR.value, 0x63)
        self.assertEqual(Commands.SET_WR_PTR.value, 0x64)
        self.assertEqual(Commands.ALIGN_WR_PTR.value, 0x65)

        self.assertEqual(Commands.ARITH_OP.value, 0x67)
        self.assertEqual(Commands.LOGIC_OP.value, 0x68)
        self.assertEqual(Commands.REFORMAT.value, 0x6A)
        self.assertEqual(Commands.COPY_STRUCT.value, 0x70)
        self.assertEqual(Commands.COPY_PARAM.value, 0x71)

        self.assertEqual(Commands.WRITE_PARAM.value, 0x72)
        self.assertEqual(Commands.READ_PARAM.value, 0x73)
        self.assertEqual(Commands.WRITE_PARAM_COMPONENT.value, 0x74)
        self.assertEqual(Commands.PRINT_VAL.value, 0x80)
        self.assertEqual(Commands.PRINT_TXT.value, 0X81)

        self.assertEqual(Commands.PRINT_STRUCT.value, 0x82)
        self.assertEqual(Commands.END_SPEC.value, 0XFF)

    def test_data_type_enum(self):
        self.assertEqual(DataType.UINT8.value, 0)
        self.assertEqual(DataType.UINT8.size, 1)
        self.assertEqual(DataType.UINT8.min, 0)
        self.assertEqual(DataType.UINT8.max, 255)

        self.assertEqual(DataType.UINT16.value, 1)
        self.assertEqual(DataType.UINT16.size, 2)
        self.assertEqual(DataType.UINT16.min, 0)
        self.assertEqual(DataType.UINT16.max, 0xFFFF)

        self.assertEqual(DataType.UINT32.value, 2)
        self.assertEqual(DataType.UINT32.size, 4)
        self.assertEqual(DataType.UINT32.min, 0)
        self.assertEqual(DataType.UINT32.max, 0xFFFFFFFF)

        self.assertEqual(DataType.UINT64.value, 3)
        self.assertEqual(DataType.UINT64.size, 8)
        self.assertEqual(DataType.UINT64.min, 0)
        self.assertEqual(DataType.UINT64.max, 0xFFFFFFFFFFFFFFFF)

        self.assertEqual(DataType.INT8.value, 4)
        self.assertEqual(DataType.INT8.size, 1)
        self.assertEqual(DataType.INT8.min, -128)
        self.assertEqual(DataType.INT8.max, 127)

        self.assertEqual(DataType.INT16.value, 5)
        self.assertEqual(DataType.INT16.size, 2)
        self.assertEqual(DataType.INT16.min, -32768)
        self.assertEqual(DataType.INT16.max, 32767)

        self.assertEqual(DataType.INT32.value, 6)
        self.assertEqual(DataType.INT32.size, 4)
        self.assertEqual(DataType.INT32.min, -2147483648)
        self.assertEqual(DataType.INT32.max, 2147483647)

        self.assertEqual(DataType.INT64.value, 7)
        self.assertEqual(DataType.INT64.size, 8)
        self.assertEqual(DataType.INT64.min, -9223372036854775808)
        self.assertEqual(DataType.INT64.max, 9223372036854775807)

        self.assertEqual(DataType.U88.value, 8)
        self.assertEqual(DataType.U88.size, 2)
        self.assertEqual(DataType.U88.min, decimal.Decimal("0"))
        self.assertEqual(DataType.U88.max, decimal.Decimal("255.99609375"))

        self.assertEqual(DataType.U1616.value, 9)
        self.assertEqual(DataType.U1616.size, 4)
        self.assertEqual(DataType.U1616.min, decimal.Decimal("0"))
        self.assertEqual(DataType.U1616.max, decimal.Decimal("65535.9999847"))

        self.assertEqual(DataType.U3232.value, 10)
        self.assertEqual(DataType.U3232.size, 8)
        self.assertEqual(DataType.U3232.min, decimal.Decimal("0"))
        self.assertEqual(
            DataType.U3232.max,
            decimal.Decimal("4294967295.99999999976716935634613037109375"))

        self.assertEqual(DataType.S87.value, 11)
        self.assertEqual(DataType.S87.size, 2)
        self.assertEqual(DataType.S87.min, decimal.Decimal("-256"))
        self.assertEqual(DataType.S87.max, decimal.Decimal("255.9921875"))

        self.assertEqual(DataType.S1615.value, 12)
        self.assertEqual(DataType.S1615.size, 4)
        self.assertEqual(DataType.S1615.min, decimal.Decimal("-65536"))
        self.assertEqual(
            DataType.S1615.max, decimal.Decimal("65535.999969482421875"))

        self.assertEqual(
            DataType.S1615.closest_representable_value(1.00001), 1.0)
        self.assertEqual(
            DataType.S1615.closest_representable_value_above(0.99997), 1.0)

        self.assertEqual(DataType.S3231.value, 13)
        self.assertEqual(DataType.S3231.size, 8)
        self.assertEqual(DataType.S3231.min, decimal.Decimal("-4294967296"))
        self.assertEqual(
            DataType.S3231.max,
            decimal.Decimal("4294967295.9999999995343387126922607421875"))

        self.assertEqual(DataType.U08.value, 16)
        self.assertEqual(DataType.U08.size, 1)
        self.assertEqual(DataType.U08.min, decimal.Decimal("0"))
        self.assertEqual(DataType.U08.max, decimal.Decimal("0.99609375"))

        self.assertEqual(DataType.U016.value, 17)
        self.assertEqual(DataType.U016.size, 2)
        self.assertEqual(DataType.U016.min, decimal.Decimal("0"))
        self.assertEqual(DataType.U016.max, decimal.Decimal("0.999984741211"))

        self.assertEqual(DataType.U032.value, 18)
        self.assertEqual(DataType.U032.size, 4)
        self.assertEqual(DataType.U032.min, decimal.Decimal("0"))
        self.assertEqual(
            DataType.U032.max,
            decimal.Decimal("0.99999999976716935634613037109375"))

        self.assertEqual(DataType.U064.value, 19)
        self.assertEqual(DataType.U064.size, 8)
        self.assertEqual(DataType.U064.min, decimal.Decimal("0"))
        self.assertEqual(
            DataType.U064.max,
            decimal.Decimal("0.999999999999999999945789891375724"
                            "7782996273599565029"))

        self.assertEqual(DataType.S07.value, 20)
        self.assertEqual(DataType.S07.size, 1)
        self.assertEqual(DataType.S07.min, decimal.Decimal("-1"))
        self.assertEqual(DataType.S07.max, decimal.Decimal("0.9921875"))

        self.assertEqual(DataType.S015.value, 21)
        self.assertEqual(DataType.S015.size, 2)
        self.assertEqual(DataType.S015.min, decimal.Decimal("-1"))
        self.assertEqual(
            DataType.S015.max,
            decimal.Decimal("0.999969482421875"))

        self.assertEqual(DataType.S031.value, 22)
        self.assertEqual(DataType.S031.size, 4)
        self.assertEqual(DataType.S031.min, decimal.Decimal("-1"))
        self.assertEqual(
            DataType.S031.max,
            decimal.Decimal("0.99999999976716935634613037109375"))

        self.assertEqual(DataType.S063.value, 23)
        self.assertEqual(DataType.S063.size, 8)
        self.assertEqual(DataType.S063.min, decimal.Decimal("-1"))
        self.assertEqual(
            DataType.S063.max,
            decimal.Decimal("0.99999999999999999989157978275144"
                            "95565992547199130058"))


if __name__ == '__main__':
    unittest.main()
