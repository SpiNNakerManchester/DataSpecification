import unittest
import struct
from io import BytesIO
from StringIO import StringIO

from data_specification import constants, exceptions
from data_specification.enums.condition import Condition
from data_specification.enums.data_type import DataType
from data_specification.enums.arithemetic_operation import ArithmeticOperation
from data_specification.enums.logic_operation import LogicOperation
from data_specification.data_specification_generator \
                                              import DataSpecificationGenerator


class TestDataSpecGeneration(unittest.TestCase):

    def setUp(self):
        # Indicate if there has been a previous read
        self.previous_read = False

        self.spec_writer = BytesIO()
        self.report_writer = StringIO()
        self.dsg = DataSpecificationGenerator(self.spec_writer,
                                              self.report_writer)

    def tearDown(self):
        pass

    def get_next_word(self):
        if not self.previous_read:
            self.spec_writer.seek(0)
            self.previous_read = True
        return struct.unpack("<I", self.spec_writer.read(4))[0]

    def skip_words(self, words):
        if not self.previous_read:
            self.spec_writer.seek(0)
            self.previous_read = True
        self.spec_writer.read(4 * words)

    def test_new_data_spec_generator(self):
        self.assertEqual(self.dsg.spec_writer, self.spec_writer,
                         "DSG spec writer not initialized correctly")
        self.assertEqual(self.dsg.report_writer, self.report_writer,
                         "DSG report writer not initialized correctly")
        self.assertEqual(self.dsg.instruction_counter, 0,
                         "DSG instruction counter not initialized correctly")
        self.assertEqual(self.dsg.mem_slot, constants.MAX_MEM_REGIONS * [0],
                         "DSG memory slots not initialized correctly")
        self.assertEqual(self.dsg.function, constants.MAX_CONSTRUCTORS * [0],
                         "DSG constructor slots not initialized correctly")

    def test_define_break(self):
        self.dsg.define_break()

        command = self.get_next_word()

        self.assertEqual(command, 0x00000000, "BREAK wrong command word")

        command = self.spec_writer.read(1)
        self.assertEqual(command, "", "BREAK added more words")

    def test_no_operation(self):
        self.dsg.no_operation()

        command = self.get_next_word()
        self.assertEqual(command, 0x00100000, "NOP wrong command word")

        command = self.spec_writer.read(1)
        self.assertEqual(command, "", "NOP added more words")

    def test_reserve_memory_region(self):
        self.dsg.reserve_memory_region(1, 0x111)
        self.dsg.reserve_memory_region(2, 0x1122)
        self.dsg.reserve_memory_region(3, 0x1122, empty=True)
        self.dsg.reserve_memory_region(4, 0x3344, label='test')

        self.assertRaises(
            exceptions.DataSpecificationParameterOutOfBoundsException,
            self.dsg.reserve_memory_region, -1, 0x100)
        self.assertRaises(
            exceptions.DataSpecificationParameterOutOfBoundsException,
            self.dsg.reserve_memory_region, constants.MAX_MEM_REGIONS, 0x100)
        self.assertRaises(
            exceptions.DataSpecificationRegionInUseException,
            self.dsg.reserve_memory_region, 1, 0x100)

        command = self.get_next_word()
        self.assertEqual(command, 0x10200001,
                         "RESERVE wrong command word for memory region 1")
        command = self.get_next_word()
        self.assertEqual(command, 0x111,
                         "RESERVE size word wrong for memory region 1")
        command = self.get_next_word()
        self.assertEqual(command, 0x10200002,
                         "RESERVE wrong command word for memory region 2")
        command = self.get_next_word()
        self.assertEqual(command, 0x1122,
                         "RESERVE size word wrong for memory region 2")
        command = self.get_next_word()
        self.assertEqual(command, 0x10200083,
                         "RESERVE wrong command word for memory region 3")
        command = self.get_next_word()
        self.assertEqual(command, 0x1122,
                         "RESERVE size word wrong for memory region 3")
        command = self.get_next_word()
        self.assertEqual(command, 0x10200004,
                         "RESERVE wrong command word for memory region 4")
        command = self.get_next_word()
        self.assertEqual(command, 0x3344,
                         "RESERVE size word wrong for memory region 4")

        self.assertEqual(self.dsg.mem_slot[1], [0x111, None, False],
                         "Memory region 0 DSG data wrong")
        self.assertEqual(self.dsg.mem_slot[2], [0x1122, None, False],
                         "Memory region 1 DSG data wrong")
        self.assertEqual(self.dsg.mem_slot[3], [0x1122, None, True],
                         "Memory region 2 DSG data wrong")
        self.assertEqual(self.dsg.mem_slot[4], [0x3344, "test", False],
                         "Memory region 3 DSG data wrong")

    def test_free_memory_region(self):
        self.dsg.reserve_memory_region(1, 0x111)
        self.dsg.free_memory_region(1)

        self.skip_words(2)

        command = self.get_next_word()
        self.assertEqual(command, 0x00300001, "FREE wrong command word")

        self.assertRaises(
            exceptions.DataSpecificationParameterOutOfBoundsException,
            self.dsg.free_memory_region, -1)
        self.assertRaises(
            exceptions.DataSpecificationParameterOutOfBoundsException,
            self.dsg.free_memory_region, constants.MAX_MEM_REGIONS)
        self.assertRaises(
            exceptions.DataSpecificationNotAllocatedException,
            self.dsg.free_memory_region, 2)
        self.assertRaises(
            exceptions.DataSpecificationNotAllocatedException,
            self.dsg.free_memory_region, 1)
        self.assertEqual(self.dsg.mem_slot[1], 0,
                         "FREE not cleared mem slot entry")

    def test_define_structure(self):
        self.dsg.define_structure(0, [("first", DataType.UINT8, 0xAB)])
        self.dsg.define_structure(1, [("first", DataType.UINT8, 0xAB),
                                      ("second", DataType.UINT32, 0x12345679),
                                      ("third", DataType.INT16, None),
                                      ("fourth", DataType.UINT64,
                                       0x123456789ABCDEFL)])
        self.assertRaises(
            exceptions.DataSpecificationParameterOutOfBoundsException,
            self.dsg.define_structure, -1, [("first", DataType.UINT8, 0xAB)])
        self.assertRaises(
            exceptions.DataSpecificationParameterOutOfBoundsException,
            self.dsg.define_structure, constants.MAX_STRUCT_SLOTS,
            [("first", DataType.UINT8, 0xAB)])
        self.assertRaises(
            exceptions.DataSpecificationParameterOutOfBoundsException,
            self.dsg.define_structure, 1, [])
        self.assertRaises(exceptions.DataSpecificationStructureInUseException,
            self.dsg.define_structure, 0, [("first", DataType.UINT8, 0xAB)])

        command = self.get_next_word()
        self.assertEqual(command, 0x01000000, "START_STRUCT wrong command word")

        command = self.get_next_word()
        self.assertEqual(command, 0x11100000, "STRUCT_ELEM wrong command word")
        command = self.get_next_word()
        self.assertEqual(command, 0x000000AB, "STRUCT_ELEM value wrong")

        command = self.get_next_word()
        self.assertEqual(command, 0x01200000, "END_STRUCT wrong command word")


        command = self.get_next_word()
        self.assertEqual(command, 0x01000001, "START_STRUCT wrong command word")

        command = self.get_next_word()
        self.assertEqual(command, 0x11100000, "STRUCT_ELEM wrong command word")
        command = self.get_next_word()
        self.assertEqual(command, 0x000000AB, "STRUCT_ELEM value wrong")

        command = self.get_next_word()
        self.assertEqual(command, 0x11100002, "STRUCT_ELEM wrong command word")
        command = self.get_next_word()
        self.assertEqual(command, 0x12345679, "STRUCT_ELEM value wrong")

        command = self.get_next_word()
        self.assertEqual(command, 0x01100005, "STRUCT_ELEM wrong command word")

        command = self.get_next_word()
        self.assertEqual(command, 0x21100003, "STRUCT_ELEM wrong command word")
        command = self.get_next_word()
        self.assertEqual(command, 0x89ABCDEF, "STRUCT_ELEM value wrong")
        command = self.get_next_word()
        self.assertEqual(command, 0x01234567, "STRUCT_ELEM value wrong")

        command = self.get_next_word()
        self.assertEqual(command, 0x01200000, "END_STRUCT wrong command word")

    def test_call_arithmetic_operation(self):
        # Call addition signed and unsigned
        self.dsg.call_arithmetic_operation(2, 0x12, ArithmeticOperation.ADD,
                                           0x34, False, False, False)
        self.dsg.call_arithmetic_operation(2, 0x1234, ArithmeticOperation.ADD,
                                           0x5678, True, False, False)

        # Call subtraction signed and unsigned
        self.dsg.call_arithmetic_operation(3, 0x1234,
                                           ArithmeticOperation.SUBTRACT,
                                           0x3456, False, False, False)
        self.dsg.call_arithmetic_operation(3, 0x1234,
                                           ArithmeticOperation.SUBTRACT,
                                           0x3456, True, False, False)

        # Call multiplication signed and unsigned
        self.dsg.call_arithmetic_operation(3, 0x12345678,
                                           ArithmeticOperation.MULTIPLY,
                                           0x3456, False, False, False)
        self.dsg.call_arithmetic_operation(3, 0x1234,
                                           ArithmeticOperation.MULTIPLY,
                                           0x3456ABCD, True, False, False)

        # Call with register arguments
        self.dsg.call_arithmetic_operation(3, 1, ArithmeticOperation.ADD,
                                           0x3456, False, True, False)
        self.dsg.call_arithmetic_operation(3, 1, ArithmeticOperation.ADD,
                                           2, False, False, True)
        self.dsg.call_arithmetic_operation(3, 3, ArithmeticOperation.ADD,
                                           4, False, True, True)
        self.dsg.call_arithmetic_operation(3, 3, ArithmeticOperation.MULTIPLY,
                                           4, False, True, True)
        self.dsg.call_arithmetic_operation(3, 3, ArithmeticOperation.MULTIPLY,
                                           4, True, True, True)

        # Call exception raise for register values out of bounds
        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.call_arithmetic_operation, -1, 0x12,
                ArithmeticOperation.ADD, 0x34, True, True, False)

        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.call_arithmetic_operation, constants.MAX_REGISTERS,
                0x12, ArithmeticOperation.ADD, 0x34, True, True, False)

        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.call_arithmetic_operation, 1, -1,
                ArithmeticOperation.ADD, 0x34, True, True, False)

        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.call_arithmetic_operation, 1, constants.MAX_REGISTERS,
                ArithmeticOperation.ADD, 2, False, True, False)

        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.call_arithmetic_operation, 1, 5,
                ArithmeticOperation.SUBTRACT, -1, False, False, True)

        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.call_arithmetic_operation, 1, 1,
                ArithmeticOperation.SUBTRACT, constants.MAX_REGISTERS,
                False, True, True)

        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.call_arithmetic_operation, 1, 0x1,
                ArithmeticOperation.SUBTRACT, -1, False, False, True)

        # Test unknown type exception raise
        self.assertRaises(
                exceptions.DataSpecificationInvalidOperationException,
                self.dsg.call_arithmetic_operation, 1, 1, LogicOperation.OR,
                2, 1, False)

        # Test addition signed and unsigned
        command = self.get_next_word()
        self.assertEqual(command, 0x26742000, "ARITH_OP wrong command word")

        data = self.get_next_word()
        self.assertEqual(data, 0x12, "ARITH_OP wrong data word")
        data = self.get_next_word()
        self.assertEqual(data, 0x34, "ARITH_OP wrong data word")

        command = self.get_next_word()
        self.assertEqual(command, 0x267C2000, "ARITH_OP wrong command word")

        data = self.get_next_word()
        self.assertEqual(data, 0x1234, "ARITH_OP wrong data word")
        data = self.get_next_word()
        self.assertEqual(data, 0x5678, "ARITH_OP wrong data word")

        # Test subtraction signed and unsigned
        command = self.get_next_word()
        self.assertEqual(command, 0x26743001, "ARITH_OP wrong command word")

        data = self.get_next_word()
        self.assertEqual(data, 0x1234, "ARITH_OP wrong data word")
        data = self.get_next_word()
        self.assertEqual(data, 0x3456, "ARITH_OP wrong data word")

        command = self.get_next_word()
        self.assertEqual(command, 0x267C3001, "ARITH_OP wrong command word")

        data = self.get_next_word()
        self.assertEqual(data, 0x1234, "ARITH_OP wrong data word")
        data = self.get_next_word()
        self.assertEqual(data, 0x3456, "ARITH_OP wrong data word")

        # Test multiplication signed and unsigned
        command = self.get_next_word()
        self.assertEqual(command, 0x26743002, "ARITH_OP wrong command word")

        data = self.get_next_word()
        self.assertEqual(data, 0x12345678, "ARITH_OP wrong data word")
        data = self.get_next_word()
        self.assertEqual(data, 0x3456, "ARITH_OP wrong data word")

        command = self.get_next_word()
        self.assertEqual(command, 0x267C3002, "ARITH_OP wrong command word")

        data = self.get_next_word()
        self.assertEqual(data, 0x1234, "ARITH_OP wrong data word")
        data = self.get_next_word()
        self.assertEqual(data, 0x3456ABCD, "ARITH_OP wrong data word")

        # Test register arguments
        command = self.get_next_word()
        self.assertEqual(command, 0x16763100, "ARITH_OP wrong command word")
        data = self.get_next_word()
        self.assertEqual(data, 0x3456, "ARITH_OP wrong data word")

        command = self.get_next_word()
        self.assertEqual(command, 0x16753020, "ARITH_OP wrong command word")
        data = self.get_next_word()
        self.assertEqual(data, 0x1, "ARITH_OP wrong data word")

        command = self.get_next_word()
        self.assertEqual(command, 0x06773340, "ARITH_OP wrong command word")

        command = self.get_next_word()
        self.assertEqual(command, 0x06773342, "ARITH_OP wrong command word")

        command = self.get_next_word()
        self.assertEqual(command, 0x067F3342, "ARITH_OP wrong command word")



    def test_align_write_pointer(self):
        # Test DataSpecificationNoRegionSelectedException raise
        self.assertRaises(
            exceptions.DataSpecificationNoRegionSelectedException,
            self.dsg.align_write_pointer, 1)

        # Define a memory region and switch focus to it
        self.dsg.reserve_memory_region(1, 100)
        self.dsg.switch_write_focus(1)

        # Call align_write_pointer with different parameters
        self.dsg.align_write_pointer(1, False, None)
        self.dsg.align_write_pointer(31, False,  None)
        self.dsg.align_write_pointer(5, True,  None)

        self.dsg.align_write_pointer(1, False, 2)
        self.dsg.align_write_pointer(5, True, 3)

        # Test DataSpecificationOutOfBoundsException raise
        self.assertRaises(
            exceptions.DataSpecificationParameterOutOfBoundsException,
            self.dsg.align_write_pointer, -1)
        self.assertRaises(
            exceptions.DataSpecificationParameterOutOfBoundsException,
            self.dsg.align_write_pointer, 33)

        self.assertRaises(
            exceptions.DataSpecificationParameterOutOfBoundsException,
            self.dsg.align_write_pointer, -1, True)
        self.assertRaises(
            exceptions.DataSpecificationParameterOutOfBoundsException,
            self.dsg.align_write_pointer, constants.MAX_REGISTERS, True)

        self.assertRaises(
            exceptions.DataSpecificationParameterOutOfBoundsException,
            self.dsg.align_write_pointer, 1, False, -1)
        self.assertRaises(
            exceptions.DataSpecificationParameterOutOfBoundsException,
            self.dsg.align_write_pointer, 1, False, constants.MAX_REGISTERS)

        self.skip_words(3)

        command = self.get_next_word()
        self.assertEqual(command, 0x06600001,
                         "WRITE_POINTER wrong command word")

        command = self.get_next_word()
        self.assertEqual(command, 0x0660001F,
                         "WRITE_POINTER wrong command word")

        command = self.get_next_word()
        self.assertEqual(command, 0x06620500,
                         "WRITE_POINTER wrong command word")

        command = self.get_next_word()
        self.assertEqual(command, 0x06642001,
                         "WRITE_POINTER wrong command word")

        command = self.get_next_word()
        self.assertEqual(command, 0x06663500,
                         "WRITE_POINTER wrong command word")

    def test_break_loop(self):
        self.assertRaises(exceptions.DataSpecificationInvalidCommandException,
                          self.dsg.break_loop)

        self.dsg.start_loop(0, 0, 0, True, True, True)
        self.dsg.break_loop()

        self.skip_words(2)

        command = self.get_next_word()

        self.assertEqual(command, 0x05200000, "BREAK_LOOP wrong command word")

    def test_call_function(self):

        self.dsg.start_function(0, [])
        self.dsg.end_function()

        self.dsg.start_function(1, [True, True, False])
        self.dsg.end_function()

        self.dsg.define_structure(0, [("test", DataType.U08, 0)])
        self.dsg.define_structure(1, [("test", DataType.U08, 0)])
        self.dsg.define_structure(2, [("test", DataType.U08, 0)])

        self.dsg.call_function(0, [])
        self.dsg.call_function(1, [0, 1, 2])

        self.assertRaises(exceptions.DataSpecificationNotAllocatedException,
                          self.dsg.call_function, 2, [])
        self.assertRaises(
                exceptions.DataSpecificationWrongParameterNumberException,
                self.dsg.call_function, 1, [])
        self.assertRaises(
                exceptions.DataSpecificationWrongParameterNumberException,
                self.dsg.call_function, 1, [0, 1])
        self.assertRaises(
                exceptions.DataSpecificationWrongParameterNumberException,
                self.dsg.call_function, 1, [0, 1, 2, 3])
        self.assertRaises(
                exceptions.DataSpecificationDuplicateParameterException,
                self.dsg.call_function, 1, [1, 1, 2])
        self.assertRaises(exceptions.DataSpecificationNotAllocatedException,
                          self.dsg.call_function, 1, [1, 2, 3])
        self.assertRaises(exceptions.DataSpecificationNotAllocatedException,
                          self.dsg.call_function, 1, [3, 2, 1])
        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.call_function, -1, [0, 1, 2])
        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.call_function, constants.MAX_CONSTRUCTORS, [0, 1])
        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.call_function, 1, [0, -1, 2])
        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.call_function, 1, [-1,  1, 2])
        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.call_function, 1, [0, 2, constants.MAX_STRUCT_SLOTS])

        self.skip_words(16)

        command = self.get_next_word()
        self.assertEqual(command, 0x04000000, "CONSTRUCT wrong command word")

        command = self.get_next_word()
        self.assertEqual(command, 0x14000100, "CONSTRUCT wrong command word")

        command = self.get_next_word()
        self.assertEqual(command, 0x00002040, "CONSTRUCT command data wrong")

    def test_start_function(self):

        self.dsg.start_function(0, [])
        self.dsg.no_operation()
        self.dsg.end_function()

        self.dsg.start_function(1, [True, True, False])
        self.dsg.no_operation()
        self.dsg.end_function()

        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.start_function, -1, [True])
        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.start_function, constants.MAX_CONSTRUCTORS, [True])
        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.start_function, 2,
                [True, True, True, True, True, True])
        self.assertRaises(exceptions.DataSpecificationFunctionInUse,
                          self.dsg.start_function, 0, [])

        self.dsg.start_function(2, [False])

        self.assertRaises(exceptions.DataSpecificationInvalidCommandException,
                          self.dsg.start_function, 3, [])

        self.dsg.end_function()

        command = self.get_next_word()
        self.assertEqual(command, 0x02000000,
                         "START_CONSTRUCTOR wrong command word")

        self.skip_words(2)

        command = self.get_next_word()
        self.assertEqual(command, 0x02000B03,
                         "START_CONSTRUCTOR wrong command word")

        self.skip_words(2)

    def test_end_function(self):
        self.assertRaises(exceptions.DataSpecificationInvalidCommandException,
                          self.dsg.end_function)

        self.dsg.start_function(0, [])
        self.dsg.end_function()

        self.skip_words(1)

        command = self.get_next_word()
        self.assertEquals(command, 0x02500000,
                          "END_CONSTRUCTOR wrong command word")

    def test_logical_and(self):
        self.dsg.logical_and(0, 0x12, 0x34, False, False)
        self.dsg.logical_and(1, 0x12345678, 0xABCDEF14, False, False)

        self.dsg.logical_and(3, 2, 0xABCDEF14, True, False)
        self.dsg.logical_and(4, 0x12345678, 5, False, True)

        self.dsg.logical_and(4, 3, 5, True, True)
        self.dsg.logical_and(3, 3, 3, True, True)

        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.logical_and, -1, 0x12, 0x34, False, False)
        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.logical_and, constants.MAX_REGISTERS, 0x12, 0x34,
                False, False)
        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.logical_and, 1, -1, 0x34, True, False)
        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.logical_and, 1, constants.MAX_REGISTERS, 0x34,
                True, False)
        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.logical_and, 1, 0x12, -1, False, True)
        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.logical_and, 1, 0x34, constants.MAX_REGISTERS,
                False, True)

        command = self.get_next_word()
        self.assertEquals(command, 0x26840003,
                          "Logical AND wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x00000012, "Logical AND wrong data word")
        data = self.get_next_word()
        self.assertEquals(data, 0x00000034, "Logical AND wrong data word")

        command = self.get_next_word()
        self.assertEquals(command, 0x26841003,
                          "Logical AND wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x12345678, "Logical AND wrong data word")
        data = self.get_next_word()
        self.assertEquals(data, 0xABCDEF14, "Logical AND wrong data word")

        command = self.get_next_word()
        self.assertEquals(command, 0x16863203,
                          "Logical AND wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0xABCDEF14, "Logical AND wrong data word")

        command = self.get_next_word()
        self.assertEquals(command, 0x16854053,
                          "Logical AND wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x12345678, "Logical AND wrong data word")

        command = self.get_next_word()
        self.assertEquals(command, 0x06874353,
                          "Logical AND wrong command word")

        command = self.get_next_word()
        self.assertEquals(command, 0x06873333,
                          "Logical AND wrong command word")

    def test_logical_or(self):
        self.dsg.logical_or(0, 0x12, 0x34, False, False)
        self.dsg.logical_or(1, 0x12345678, 0xABCDEF14, False, False)

        self.dsg.logical_or(3, 2, 0xABCDEF14, True, False)
        self.dsg.logical_or(4, 0x12345678, 5, False, True)

        self.dsg.logical_or(4, 3, 5, True, True)
        self.dsg.logical_or(3, 3, 3, True, True)

        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.logical_or, -1, 0x12, 0x34, False, False)
        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.logical_or, constants.MAX_REGISTERS, 0x12, 0x34,
                False, False)
        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.logical_or, 1, -1, 0x34, True, False)
        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.logical_or, 1, constants.MAX_REGISTERS, 0x34,
                True, False)
        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.logical_or, 1, 0x12, -1, False, True)
        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.logical_or, 1, 0x34, constants.MAX_REGISTERS,
                False, True)

        command = self.get_next_word()
        self.assertEquals(command, 0x26840002,
                          "Logical OR wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x00000012, "Logical OR wrong data word")
        data = self.get_next_word()
        self.assertEquals(data, 0x00000034, "Logical OR wrong data word")

        command = self.get_next_word()
        self.assertEquals(command, 0x26841002,
                          "Logical OR wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x12345678, "Logical OR wrong data word")
        data = self.get_next_word()
        self.assertEquals(data, 0xABCDEF14, "Logical OR wrong data word")

        command = self.get_next_word()
        self.assertEquals(command, 0x16863202,
                          "Logical OR wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0xABCDEF14, "Logical OR wrong data word")

        command = self.get_next_word()
        self.assertEquals(command, 0x16854052,
                          "Logical OR wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x12345678, "Logical OR wrong data word")

        command = self.get_next_word()
        self.assertEquals(command, 0x06874352,
                          "Logical OR wrong command word")

        command = self.get_next_word()
        self.assertEquals(command, 0x06873332,
                          "Logical OR wrong command word")

    def test_logical_or(self):
        self.dsg.logical_or(0, 0x12, 0x34, False, False)
        self.dsg.logical_or(1, 0x12345678, 0xABCDEF14, False, False)

        self.dsg.logical_or(3, 2, 0xABCDEF14, True, False)
        self.dsg.logical_or(4, 0x12345678, 5, False, True)

        self.dsg.logical_or(4, 3, 5, True, True)
        self.dsg.logical_or(3, 3, 3, True, True)

        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.logical_or, -1, 0x12, 0x34, False, False)
        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.logical_or, constants.MAX_REGISTERS, 0x12, 0x34,
                False, False)
        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.logical_or, 1, -1, 0x34, True, False)
        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.logical_or, 1, constants.MAX_REGISTERS, 0x34,
                True, False)
        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.logical_or, 1, 0x12, -1, False, True)
        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.logical_or, 1, 0x34, constants.MAX_REGISTERS,
                False, True)

        command = self.get_next_word()
        self.assertEquals(command, 0x26840002,
                          "Logical OR wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x00000012, "Logical OR wrong data word")
        data = self.get_next_word()
        self.assertEquals(data, 0x00000034, "Logical OR wrong data word")

        command = self.get_next_word()
        self.assertEquals(command, 0x26841002,
                          "Logical OR wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x12345678, "Logical OR wrong data word")
        data = self.get_next_word()
        self.assertEquals(data, 0xABCDEF14, "Logical OR wrong data word")

        command = self.get_next_word()
        self.assertEquals(command, 0x16863202,
                          "Logical OR wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0xABCDEF14, "Logical OR wrong data word")

        command = self.get_next_word()
        self.assertEquals(command, 0x16854052,
                          "Logical OR wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x12345678, "Logical OR wrong data word")

        command = self.get_next_word()
        self.assertEquals(command, 0x06874352,
                          "Logical OR wrong command word")

        command = self.get_next_word()
        self.assertEquals(command, 0x06873332,
                          "Logical OR wrong command word")

    def test_logical_xor(self):
        self.dsg.logical_xor(0, 0x12, 0x34, False, False)
        self.dsg.logical_xor(1, 0x12345678, 0xABCDEF14, False, False)

        self.dsg.logical_xor(3, 2, 0xABCDEF14, True, False)
        self.dsg.logical_xor(4, 0x12345678, 5, False, True)

        self.dsg.logical_xor(4, 3, 5, True, True)
        self.dsg.logical_xor(3, 3, 3, True, True)

        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.logical_xor, -1, 0x12, 0x34, False, False)
        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.logical_xor, constants.MAX_REGISTERS, 0x12, 0x34,
                False, False)
        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.logical_xor, 1, -1, 0x34, True, False)
        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.logical_xor, 1, constants.MAX_REGISTERS, 0x34,
                True, False)
        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.logical_xor, 1, 0x12, -1, False, True)
        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.logical_xor, 1, 0x34, constants.MAX_REGISTERS,
                False, True)

        command = self.get_next_word()
        self.assertEquals(command, 0x26840004,
                          "Logical XOR wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x00000012, "Logical XOR wrong data word")
        data = self.get_next_word()
        self.assertEquals(data, 0x00000034, "Logical XOR wrong data word")

        command = self.get_next_word()
        self.assertEquals(command, 0x26841004,
                          "Logical XOR wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x12345678, "Logical XOR wrong data word")
        data = self.get_next_word()
        self.assertEquals(data, 0xABCDEF14, "Logical XOR wrong data word")

        command = self.get_next_word()
        self.assertEquals(command, 0x16863204,
                          "Logical XOR wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0xABCDEF14, "Logical XOR wrong data word")

        command = self.get_next_word()
        self.assertEquals(command, 0x16854054,
                          "Logical XOR wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x12345678, "Logical XOR wrong data word")

        command = self.get_next_word()
        self.assertEquals(command, 0x06874354,
                          "Logical XOR wrong command word")

        command = self.get_next_word()
        self.assertEquals(command, 0x06873334,
                          "Logical XOR wrong command word")

    def test_logical_left_shift(self):
        self.dsg.logical_left_shift(0, 0x12, 0x34, False, False)
        self.dsg.logical_left_shift(1, 0x12345678, 0xABCDEF14, False, False)

        self.dsg.logical_left_shift(3, 2, 0xABCDEF14, True, False)
        self.dsg.logical_left_shift(4, 0x12345678, 5, False, True)

        self.dsg.logical_left_shift(4, 3, 5, True, True)
        self.dsg.logical_left_shift(3, 3, 3, True, True)

        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.logical_left_shift, -1, 0x12, 0x34, False, False)
        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.logical_left_shift, constants.MAX_REGISTERS, 0x12, 0x34,
                False, False)
        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.logical_left_shift, 1, -1, 0x34, True, False)
        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.logical_left_shift, 1, constants.MAX_REGISTERS, 0x34,
                True, False)
        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.logical_left_shift, 1, 0x12, -1, False, True)
        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.logical_left_shift, 1, 0x34, constants.MAX_REGISTERS,
                False, True)

        command = self.get_next_word()
        self.assertEquals(command, 0x26840000,
                          "Logical LEFT_SHIFT wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x00000012,
                          "Logical LEFT_SHIFT wrong data word")
        data = self.get_next_word()
        self.assertEquals(data, 0x00000034,
                          "Logical LEFT_SHIFT wrong data word")

        command = self.get_next_word()
        self.assertEquals(command, 0x26841000,
                          "Logical LEFT_SHIFT wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x12345678,
                          "Logical LEFT_SHIFT wrong data word")
        data = self.get_next_word()
        self.assertEquals(data, 0xABCDEF14,
                          "Logical LEFT_SHIFT wrong data word")

        command = self.get_next_word()
        self.assertEquals(command, 0x16863200,
                          "Logical LEFT_SHIFT wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0xABCDEF14,
                          "Logical LEFT_SHIFT wrong data word")

        command = self.get_next_word()
        self.assertEquals(command, 0x16854050,
                          "Logical LEFT_SHIFT wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x12345678,
                          "Logical LEFT_SHIFT wrong data word")

        command = self.get_next_word()
        self.assertEquals(command, 0x06874350,
                          "Logical LEFT_SHIFT wrong command word")

        command = self.get_next_word()
        self.assertEquals(command, 0x06873330,
                          "Logical LEFT_SHIFT wrong command word")

    def test_logical_not(self):
        self.dsg.logical_not(1, 0x12345678, False)

        self.dsg.logical_not(3, 2, True)

        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.logical_not, -1, 0x12, False)
        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.logical_not, constants.MAX_REGISTERS, 0x12, False)
        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.logical_not, 1, -1, True)
        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.logical_not, 1, constants.MAX_REGISTERS, True)

        command = self.get_next_word()
        self.assertEquals(command, 0x16841005,
                          "Logical NOT wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x12345678,
                          "Logical NOT wrong data word")

        command = self.get_next_word()
        self.assertEquals(command, 0x06863205,
                          "Logical NOT wrong command word")

    def test_logical_right_shift(self):
        self.dsg.logical_right_shift(0, 0x12, 0x34, False, False)
        self.dsg.logical_right_shift(1, 0x12345678, 0xABCDEF14, False, False)

        self.dsg.logical_right_shift(3, 2, 0xABCDEF14, True, False)
        self.dsg.logical_right_shift(4, 0x12345678, 5, False, True)

        self.dsg.logical_right_shift(4, 3, 5, True, True)
        self.dsg.logical_right_shift(3, 3, 3, True, True)

        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.logical_right_shift, -1, 0x12, 0x34, False, False)
        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.logical_right_shift, constants.MAX_REGISTERS, 0x12, 0x34,
                False, False)
        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.logical_right_shift, 1, -1, 0x34, True, False)
        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.logical_right_shift, 1, constants.MAX_REGISTERS, 0x34,
                True, False)
        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.logical_right_shift, 1, 0x12, -1, False, True)
        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.logical_right_shift, 1, 0x34, constants.MAX_REGISTERS,
                False, True)

        command = self.get_next_word()
        self.assertEquals(command, 0x26840001,
                          "Logical RIGHT_SHIFT wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x00000012,
                          "Logical RIGHT_SHIFT wrong data word")
        data = self.get_next_word()
        self.assertEquals(data, 0x00000034,
                          "Logical RIGHT_SHIFT wrong data word")

        command = self.get_next_word()
        self.assertEquals(command, 0x26841001,
                          "Logical RIGHT_SHIFT wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x12345678,
                          "Logical RIGHT_SHIFT wrong data word")
        data = self.get_next_word()
        self.assertEquals(data, 0xABCDEF14,
                          "Logical RIGHT_SHIFT wrong data word")

        command = self.get_next_word()
        self.assertEquals(command, 0x16863201,
                          "Logical RIGHT_SHIFT wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0xABCDEF14,
                          "Logical RIGHT_SHIFT wrong data word")

        command = self.get_next_word()
        self.assertEquals(command, 0x16854051,
                          "Logical RIGHT_SHIFT wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x12345678,
                          "Logical RIGHT_SHIFT wrong data word")

        command = self.get_next_word()
        self.assertEquals(command, 0x06874351,
                          "Logical RIGHT_SHIFT wrong command word")

        command = self.get_next_word()
        self.assertEquals(command, 0x06873331,
                          "Logical RIGHT_SHIFT wrong command word")

    def test_comment(self):
        self.dsg.comment("test")

        self.assertEquals(self.spec_writer.tell(), 0,
                          "Comment generated data specification")
        self.assertEquals(self.report_writer.getvalue(), "test\n")

    def test_copy_structure(self):
        self.dsg.define_structure(0, [("first", DataType.UINT8, 0xAB)])
        self.dsg.define_structure(1, [("first", DataType.UINT8, 0xAB),
                                      ("second", DataType.UINT32, 0x12345679),
                                      ("third", DataType.INT16, None)])

        self.dsg.copy_structure(0, 2, False, False)
        self.dsg.copy_structure(1, 3, False, False)
        self.dsg.copy_structure(1, 4, True, False)
        self.dsg.copy_structure(0, 3, False, True)
        self.dsg.copy_structure(3, 4, True, True)

        self.assertRaises(exceptions.DataSpecificationNotAllocatedException,
                          self.dsg.copy_structure, 2, 3)
        self.assertRaises(
                exceptions.DataSpecificationDuplicateParameterException,
                self.dsg.copy_structure, 2, 2)
        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.copy_structure, -1, 2, True, False)
        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.copy_structure, constants.MAX_REGISTERS, 2, True,
                False)
        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.copy_structure, 1, -1, False, True)
        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.copy_structure, 1, constants.MAX_REGISTERS, False,
                True)
        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.copy_structure, -1, 2, False, False)
        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.copy_structure, constants.MAX_STRUCT_SLOTS, 2, False,
                False)
        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.copy_structure, 1, -1, False, False)
        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.copy_structure, 1, constants.MAX_STRUCT_SLOTS, False,
                True)

        self.skip_words(11)

        command = self.get_next_word()
        self.assertEquals(command, 0x07002000,
                          "COPY_STRUCT wrong command word")

        command = self.get_next_word()
        self.assertEquals(command, 0x07003100,
                          "COPY_STRUCT wrong command word")

        command = self.get_next_word()
        self.assertEquals(command, 0x07024100,
                          "COPY_STRUCT wrong command word")

        command = self.get_next_word()
        self.assertEquals(command, 0x07043000,
                          "COPY_STRUCT wrong command word")

        command = self.get_next_word()
        self.assertEquals(command, 0x07064300,
                          "COPY_STRUCT wrong command word")

    def test_copy_structure_parameter(self):
        self.dsg.define_structure(0, [("first", DataType.UINT8, 0xAB),
                                      ("second", DataType.INT16, 0xBC)])
        self.dsg.define_structure(1, [("first", DataType.UINT8, 0xAB),
                                      ("second", DataType.UINT32, 0x12345679),
                                      ("third", DataType.INT16, None)])

        self.dsg.copy_structure_parameter(0, 0, 1, 0, False)
        self.dsg.copy_structure_parameter(0, 0, 0, 0, True)
        self.dsg.copy_structure_parameter(0, 1, 1, 2, False)
        self.dsg.copy_structure_parameter(0, 1, 2,
                                          destination_is_register=True)
        self.dsg.copy_structure_parameter(1, 0, 3,
                                          destination_is_register=True)
        self.dsg.copy_structure_parameter(1, 2, 2, -1,
                                          destination_is_register=True)

        self.assertRaises(
            exceptions.DataSpecificationParameterOutOfBoundsException,
            self.dsg.copy_structure_parameter, -1, 0, 1, 0, False)
        self.assertRaises(
            exceptions.DataSpecificationParameterOutOfBoundsException,
            self.dsg.copy_structure_parameter,
            constants.MAX_STRUCT_SLOTS, 0, 1, 0, False)

        self.assertRaises(
            exceptions.DataSpecificationParameterOutOfBoundsException,
            self.dsg.copy_structure_parameter, 0, 0, -1, 0, False)
        self.assertRaises(
            exceptions.DataSpecificationParameterOutOfBoundsException,
            self.dsg.copy_structure_parameter,
            0, 0, constants.MAX_STRUCT_SLOTS, 0, False)
        self.assertRaises(
            exceptions.DataSpecificationParameterOutOfBoundsException,
            self.dsg.copy_structure_parameter, 0, 0, -1, 0, True)
        self.assertRaises(
            exceptions.DataSpecificationParameterOutOfBoundsException,
            self.dsg.copy_structure_parameter,
            0, 0, constants.MAX_REGISTERS, 0, True)

        self.assertRaises(
            exceptions.DataSpecificationParameterOutOfBoundsException,
            self.dsg.copy_structure_parameter, 0, -1, 1, 0, False)
        self.assertRaises(
            exceptions.DataSpecificationParameterOutOfBoundsException,
            self.dsg.copy_structure_parameter, 0,
            constants.MAX_STRUCT_ELEMENTS, 1, 0, False)
        self.assertRaises(
            exceptions.DataSpecificationParameterOutOfBoundsException,
            self.dsg.copy_structure_parameter, 0, 0, 1, -1, False)
        self.assertRaises(
            exceptions.DataSpecificationParameterOutOfBoundsException,
            self.dsg.copy_structure_parameter, 0, 0, 1,
            constants.MAX_STRUCT_ELEMENTS, False)

        self.assertRaises(
            exceptions.DataSpecificationParameterOutOfBoundsException,
            self.dsg.copy_structure_parameter, 0, 0, -1, 0, True)
        self.assertRaises(
            exceptions.DataSpecificationParameterOutOfBoundsException,
            self.dsg.copy_structure_parameter,
            0, 0, constants.MAX_REGISTERS, 0, True)

        self.assertRaises(
            exceptions.DataSpecificationNotAllocatedException,
            self.dsg.copy_structure_parameter, 2, 0, 0, 0, False)
        self.assertRaises(
            exceptions.DataSpecificationNotAllocatedException,
            self.dsg.copy_structure_parameter, 0, 0, 2, 0, False)
        self.assertRaises(
            exceptions.DataSpecificationNotAllocatedException,
            self.dsg.copy_structure_parameter, 0, 4, 1, 0, False)
        self.assertRaises(
            exceptions.DataSpecificationNotAllocatedException,
            self.dsg.copy_structure_parameter, 0, 0, 1, 4, False)

        self.assertRaises(
            exceptions.DataSpecificationDuplicateParameterException,
            self.dsg.copy_structure_parameter, 0, 0, 0, 0, False)

        self.assertRaises(
            exceptions.DataSpecificationTypeMismatchException,
            self.dsg.copy_structure_parameter, 0, 0, 1, 1, False)

        self.skip_words(13)

        command = self.get_next_word()
        self.assertEquals(command, 0x17101000, "COPY_PARAM wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x00000000, "COPY_PARAM wrong data word")

        command = self.get_next_word()
        self.assertEquals(command, 0x17140000, "COPY_PARAM wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x00000000, "COPY_PARAM wrong data word")

        command = self.get_next_word()
        self.assertEquals(command, 0x17101000, "COPY_PARAM wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x00000201, "COPY_PARAM wrong data word")

        command = self.get_next_word()
        self.assertEquals(command, 0x17142000, "COPY_PARAM wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x00000001, "COPY_PARAM wrong command word")

        command = self.get_next_word()
        self.assertEquals(command, 0x17143100, "COPY_PARAM wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x00000000, "COPY_PARAM wrong command word")

        command = self.get_next_word()
        self.assertEquals(command, 0x17142100, "COPY_PARAM wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x00000002, "COPY_PARAM wrong command word")

    def test_start_loop(self):
        self.dsg.start_loop(0, 1, 2)
        self.dsg.start_loop(2, 0x02345678, 0x0ABBCCDD)
        self.dsg.start_loop(0, 1, 2, 5)
        self.dsg.start_loop(1, 0x02345678, 0x0ABBCCDD, 0x01111111)
        self.dsg.start_loop(0, 10, 2, -1)
        self.dsg.start_loop(1, 2, 3, 4, True, False, False)
        self.dsg.start_loop(1, 5, 3, 4, False, True, False)
        self.dsg.start_loop(2, 2, 3, 5, False, False, True)
        self.dsg.start_loop(1, 2, 3, 4, True, True, True)
        self.dsg.start_loop(5, 1, 1, 1, False, False, False)
        self.dsg.start_loop(1, 1, 1, 1, True, True, True)

        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.start_loop, -1, 0, 1)
        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.start_loop, constants.MAX_REGISTERS, 0, 1)

        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.start_loop, 1, -1, 1, 1, True)
        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.start_loop, 1, constants.MAX_REGISTERS, 0, 1, True)

        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.start_loop, 1, 1, -1, 1, False, True)
        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.start_loop, 1, 1, constants.MAX_REGISTERS,
                1, False, True)

        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.start_loop, 1, 1, 1, -1, False, False, True)
        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.start_loop, 1, 1, 1, constants.MAX_REGISTERS,
                False, False, True)

        command = self.get_next_word()
        self.assertEquals(command, 0x35100000, "LOOP wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x00000001, "LOOP wrong start word")
        data = self.get_next_word()
        self.assertEquals(data, 0x00000002, "LOOP wrong end word")
        data = self.get_next_word()
        self.assertEquals(data, 0x00000001, "LOOP wrong increment word")

        command = self.get_next_word()
        self.assertEquals(command, 0x35100002, "LOOP wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x02345678, "LOOP wrong start word")
        data = self.get_next_word()
        self.assertEquals(data, 0x0ABBCCDD, "LOOP wrong end word")
        data = self.get_next_word()
        self.assertEquals(data, 0x00000001, "LOOP wrong increment word")

        command = self.get_next_word()
        self.assertEquals(command, 0x35100000, "LOOP wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x00000001, "LOOP wrong start word")
        data = self.get_next_word()
        self.assertEquals(data, 0x00000002, "LOOP wrong end word")
        data = self.get_next_word()
        self.assertEquals(data, 0x00000005, "LOOP wrong increment word")

        command = self.get_next_word()
        self.assertEquals(command, 0x35100001, "LOOP wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x02345678, "LOOP wrong start word")
        data = self.get_next_word()
        self.assertEquals(data, 0x0ABBCCDD, "LOOP wrong end word")
        data = self.get_next_word()
        self.assertEquals(data, 0x01111111, "LOOP wrong increment word")

        command = self.get_next_word()
        self.assertEquals(command, 0x35100000, "LOOP wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x0000000A, "LOOP wrong start word")
        data = self.get_next_word()
        self.assertEquals(data, 0x00000002, "LOOP wrong end word")
        data = self.get_next_word()
        self.assertEquals(data, 0xFFFFFFFF, "LOOP wrong increment word")

        command = self.get_next_word()
        self.assertEquals(command, 0x25142001, "LOOP wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x00000003, "LOOP wrong end word")
        data = self.get_next_word()
        self.assertEquals(data, 0x00000004, "LOOP wrong increment word")

        command = self.get_next_word()
        self.assertEquals(command, 0x25120301, "LOOP wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x00000005, "LOOP wrong start word")
        data = self.get_next_word()
        self.assertEquals(data, 0x00000004, "LOOP wrong increment word")

        command = self.get_next_word()
        self.assertEquals(command, 0x25110052, "LOOP wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x00000002, "LOOP wrong start word")
        data = self.get_next_word()
        self.assertEquals(data, 0x00000003, "LOOP wrong end word")

        command = self.get_next_word()
        self.assertEquals(command, 0x05172341, "LOOP wrong command word")

        command = self.get_next_word()
        self.assertEquals(command, 0x35100005, "LOOP wrong command word")
        command = self.get_next_word()
        self.assertEquals(command, 0x00000001, "LOOP wrong command word")
        command = self.get_next_word()
        self.assertEquals(command, 0x00000001, "LOOP wrong command word")
        command = self.get_next_word()
        self.assertEquals(command, 0x00000001, "LOOP wrong command word")

        command = self.get_next_word()
        self.assertEquals(command, 0x05171111, "LOOP wrong command word")

    def test_end_loop(self):
        self.dsg.end_loop()
        command = self.get_next_word()
        self.assertEquals(command, 0x05300000, "END_LOOP wrong command word")

    def test_start_conditional(self):
        self.dsg.start_conditional(0, Condition.EQUAL, 0, False)
        self.dsg.start_conditional(2, Condition.EQUAL, 1, False)
        self.dsg.start_conditional(3, Condition.NOT_EQUAL, 1, False)
        self.dsg.start_conditional(4, Condition.LESS_THAN_OR_EQUAL, 3, False)
        self.dsg.start_conditional(4, Condition.LESS_THAN, 3, False)
        self.dsg.start_conditional(4, Condition.GREATER_THAN_OR_EQUAL, 5, False)
        self.dsg.start_conditional(2, Condition.GREATER_THAN, 5, False)

        self.dsg.start_conditional(0, Condition.EQUAL, 1, True)
        self.dsg.start_conditional(4, Condition.LESS_THAN, 3, True)
        self.dsg.start_conditional(2, Condition.GREATER_THAN, 5, True)

        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.start_conditional, -1, Condition.EQUAL, 0, False)

        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.start_conditional, constants.MAX_REGISTERS,
                Condition.EQUAL, 0, False)

        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.start_conditional, 0, Condition.EQUAL, -1, True)

        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.start_conditional, 0, Condition.EQUAL,
                constants.MAX_REGISTERS, True)

        command = self.get_next_word()
        self.assertEquals(command, 0x15520000, "IF wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x00000000, "IF wrong data word")

        command = self.get_next_word()
        self.assertEquals(command, 0x15520200, "IF wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x00000001, "IF wrong data word")

        command = self.get_next_word()
        self.assertEquals(command, 0x15520301, "IF wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x00000001, "IF wrong data word")

        command = self.get_next_word()
        self.assertEquals(command, 0x15520402, "IF wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x00000003, "IF wrong data word")

        command = self.get_next_word()
        self.assertEquals(command, 0x15520403, "IF wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x00000003, "IF wrong data word")

        command = self.get_next_word()
        self.assertEquals(command, 0x15520404, "IF wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x00000005, "IF wrong data word")

        command = self.get_next_word()
        self.assertEquals(command, 0x15520205, "IF wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x00000005, "IF wrong data word")

        command = self.get_next_word()
        self.assertEquals(command, 0x05530010, "IF wrong command word")

        command = self.get_next_word()
        self.assertEquals(command, 0x05530433, "IF wrong command word")

        command = self.get_next_word()
        self.assertEquals(command, 0x05530255, "IF wrong command word")

    def test_else_conditional(self):
        self.assertRaises(exceptions.DataSpecificationInvalidCommandException,
                          self.dsg.else_conditional)

        self.dsg.start_conditional(0, Condition.EQUAL, 0, True)
        self.dsg.else_conditional()

        self.assertRaises(exceptions.DataSpecificationInvalidCommandException,
                          self.dsg.else_conditional)

        self.dsg.start_conditional(0, Condition.EQUAL, 0, False)
        self.dsg.else_conditional()

        self.assertRaises(exceptions.DataSpecificationInvalidCommandException,
                          self.dsg.else_conditional)

        self.skip_words(1)
        command = self.get_next_word()
        self.assertEquals(command, 0x05600000, "ELSE wrong command word")

        self.skip_words(2)
        command = self.get_next_word()
        self.assertEquals(command, 0x05600000, "ELSE wrong command word")

    def test_end_conditional(self):
        self.assertRaises(exceptions.DataSpecificationInvalidCommandException,
                          self.dsg.end_conditional)

        self.dsg.start_conditional(0, Condition.EQUAL, 0, True)
        self.dsg.end_conditional()

        self.assertRaises(exceptions.DataSpecificationInvalidCommandException,
                          self.dsg.end_conditional)

        self.dsg.start_conditional(0, Condition.EQUAL, 0, False)
        self.dsg.else_conditional()
        self.dsg.end_conditional()

        self.assertRaises(exceptions.DataSpecificationInvalidCommandException,
                          self.dsg.end_conditional)

        self.skip_words(1)
        command = self.get_next_word()
        self.assertEquals(command, 0x05700000, "END_IF wrong command word")

        self.skip_words(3)
        command = self.get_next_word()
        self.assertEquals(command, 0x05700000, "END_IF wrong command word")

    def test_switch_write_focus(self):
        self.dsg.reserve_memory_region(0, 100)
        self.dsg.reserve_memory_region(2, 100)
        self.dsg.reserve_memory_region(1, 100, empty=True)

        self.dsg.switch_write_focus(0)
        self.dsg.switch_write_focus(2)

        self.assertRaises(
                exceptions.DataSpecificationNotAllocatedException,
                self.dsg.switch_write_focus, 3)
        self.assertRaises(
                exceptions.DataSpecificationRegionUnfilledException,
                self.dsg.switch_write_focus, 1)

        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.switch_write_focus, -1)
        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.switch_write_focus, constants.MAX_MEM_REGIONS)

        self.skip_words(6)

        command = self.get_next_word()
        self.assertEquals(command, 0x05000000,
                          "SWITCH_FOCUS wrong command word")

        command = self.get_next_word()
        self.assertEquals(command, 0x05000200,
                          "SWITCH_FOCUS wrong command word")

    def test_save_write_pointer(self):
        self.assertRaises(exceptions.DataSpecificationNoRegionSelectedException,
                          self.dsg.save_write_pointer, 0)

        self.dsg.reserve_memory_region(0, 100)

        self.assertRaises(exceptions.DataSpecificationNoRegionSelectedException,
                          self.dsg.save_write_pointer, 0)

        self.dsg.switch_write_focus(0)
        self.dsg.save_write_pointer(0)
        self.dsg.save_write_pointer(5)

        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.save_write_pointer, -1)
        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.save_write_pointer, constants.MAX_REGISTERS)

        self.skip_words(3)

        command = self.get_next_word()
        self.assertEquals(command, 0x06340000, "GET_WR_PTR wrong command word")

        command = self.get_next_word()
        self.assertEquals(command, 0x06345000, "GET_WR_PTR wrong command word")

    def test_print_struct(self):

        self.dsg.define_structure(0, [("first", DataType.UINT8, 0xAB)])
        self.dsg.define_structure(1, [("first", DataType.UINT8, 0xAB),
                                      ("second", DataType.UINT32, 0x12345679),
                                      ("third", DataType.INT16, None)])

        self.dsg.print_struct(0)
        self.dsg.print_struct(1)
        self.dsg.print_struct(2, True)
        self.dsg.print_struct(3, True)

        self.assertRaises(exceptions.DataSpecificationNotAllocatedException,
                          self.dsg.print_struct, 2)

        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.print_struct, -1)
        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.print_struct, -1, True)

        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.print_struct, constants.MAX_STRUCT_SLOTS)
        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.print_struct, constants.MAX_REGISTERS, True)

        self.skip_words(11)

        command = self.get_next_word()
        self.assertEquals(command, 0x08200000,
                          "PRINT_STRUCT wrong command word")

        command = self.get_next_word()
        self.assertEquals(command, 0x08200001,
                          "PRINT_STRUCT wrong command word")

        command = self.get_next_word()
        self.assertEquals(command, 0x08220200,
                          "PRINT_STRUCT wrong command word")

        command = self.get_next_word()
        self.assertEquals(command, 0x08220300,
                          "PRINT_STRUCT wrong command word")

    def test_print_text(self):
        self.dsg.print_text("t")
        self.dsg.print_text("te")
        self.dsg.print_text("test")
        self.dsg.print_text("test1234")
        self.dsg.print_text("test12345678")

        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.print_text, "test123456789")

        command = self.get_next_word()
        self.assertEquals(command, 0x18100000, "PRINT_TEXT wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x00000074, "PRINT_TEXT wrong data word")

        command = self.get_next_word()
        self.assertEquals(command, 0x18100001, "PRINT_TEXT wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x00006574, "PRINT_TEXT wrong data word")

        command = self.get_next_word()
        self.assertEquals(command, 0x18100003, "PRINT_TEXT wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x74736574, "PRINT_TEXT wrong data word")

        command = self.get_next_word()
        self.assertEquals(command, 0x28100007, "PRINT_TEXT wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x74736574, "PRINT_TEXT wrong data word")
        data = self.get_next_word()
        self.assertEquals(data, 0x34333231, "PRINT_TEXT wrong data word")

        command = self.get_next_word()
        self.assertEquals(command, 0x3810000B, "PRINT_TEXT wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x74736574, "PRINT_TEXT wrong data word")
        data = self.get_next_word()
        self.assertEquals(data, 0x34333231, "PRINT_TEXT wrong data word")
        data = self.get_next_word()
        self.assertEquals(data, 0x38373635, "PRINT_TEXT wrong data word")

    def test_print_value(self):
        self.dsg.print_value(0x78, False, DataType.UINT8)
        self.dsg.print_value(0x12345678)
        self.dsg.print_value(0, True)
        self.dsg.print_value(2, True)
        self.dsg.print_value(2, True, DataType.INT32)
        self.dsg.print_value(2, True, DataType.INT64)
        self.dsg.print_value(0x123456789ABCDEFL, False, DataType.UINT64)
        self.dsg.print_value(2, True, DataType.U88)

        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.print_value, 0x123456789)
        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.print_value, -1, True)
        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.print_value, constants.MAX_REGISTERS, True)
        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.print_value, 0x12345678, False, DataType.INT16)

        command = self.get_next_word()
        self.assertEquals(command, 0x18000000, "PRINT_VAL wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x00000078, "PRINT_VAL wrong data word")

        command = self.get_next_word()
        self.assertEquals(command, 0x18000002, "PRINT_VAL wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x12345678, "PRINT_VAL wrong data word")

        command = self.get_next_word()
        self.assertEquals(command, 0x08020002, "PRINT_VAL wrong command word")

        command = self.get_next_word()
        self.assertEquals(command, 0x08020202, "PRINT_VAL wrong command word")

        command = self.get_next_word()
        self.assertEquals(command, 0x08020206, "PRINT_VAL wrong command word")

        command = self.get_next_word()
        self.assertEquals(command, 0x08020207, "PRINT_VAL wrong command word")

        command = self.get_next_word()
        self.assertEquals(command, 0x28000003, "PRINT_VAL wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x89ABCDEF, "PRINT_VAL wrong data word")
        data = self.get_next_word()
        self.assertEquals(data, 0x01234567, "PRINT_VAL wrong data word")

    def test_set_register_value(self):
        self.dsg.set_register_value(0, 0, False, DataType.UINT32)
        self.dsg.set_register_value(1, 0x12345678, False, DataType.UINT32)
        self.dsg.set_register_value(2, 0x123456789ABCDEFL, False,
                                    DataType.UINT64)
        self.dsg.set_register_value(2, 0x01234567, False, DataType.INT32)
        self.dsg.set_register_value(3, 0x67, False, DataType.UINT8)

        self.dsg.set_register_value(3, 2, True, DataType.UINT64)
        self.dsg.set_register_value(3, 2, True, DataType.U88)

        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.set_register_value, -1, 0)
        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.set_register_value, constants.MAX_REGISTERS, 0)
        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.set_register_value, 0, -1, True)
        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.set_register_value, 0, constants.MAX_REGISTERS, True)
        self.assertRaises(
                exceptions.DataSpecificationDuplicateParameterException,
                self.dsg.set_register_value, 0, 0, True)

        command = self.get_next_word()
        self.assertEquals(command, 0x16040000, "MV wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x00000000, "MV wrong data word")

        command = self.get_next_word()
        self.assertEquals(command, 0x16041000, "MV wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x12345678, "MV wrong data word")

        command = self.get_next_word()
        self.assertEquals(command, 0x26042000, "MV wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x89ABCDEF, "MV wrong data word")
        data = self.get_next_word()
        self.assertEquals(data, 0x01234567, "MV wrong data word")

        command = self.get_next_word()
        self.assertEquals(command, 0x16042000, "MV wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x01234567, "MV wrong data word")

        command = self.get_next_word()
        self.assertEquals(command, 0x16043000, "MV wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x00000067, "MV wrong data word")

        command = self.get_next_word()
        self.assertEquals(command, 0x06063200, "MV wrong command word")

        command = self.get_next_word()
        self.assertEquals(command, 0x06063200, "MV wrong command word")

    def test_set_write_pointer(self):
        self.dsg.set_write_pointer(0x12345678, False, False)
        self.dsg.set_write_pointer(0x00000078, False, False)
        self.dsg.set_write_pointer(0x12, False, True)
        self.dsg.set_write_pointer(-12, False, True)
        self.dsg.set_write_pointer(1, True, True)
        self.dsg.set_write_pointer(3, True, False)

        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.set_write_pointer, -1, True)
        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.set_write_pointer, constants.MAX_REGISTERS, True)
        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.set_write_pointer, 0x123456789L, False)

        command = self.get_next_word()
        self.assertEquals(command, 0x16400000, "SET_WR_PTR wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x12345678, "SET_WR_PTR wrong data word")

        command = self.get_next_word()
        self.assertEquals(command, 0x16400000, "SET_WR_PTR wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x00000078, "SET_WR_PTR wrong data word")

        command = self.get_next_word()
        self.assertEquals(command, 0x16400001, "SET_WR_PTR wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x00000012, "SET_WR_PTR wrong data word")

        command = self.get_next_word()
        self.assertEquals(command, 0x16400001, "SET_WR_PTR wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0xFFFFFFF4, "SET_WR_PTR wrong data word")

        command = self.get_next_word()
        self.assertEquals(command, 0x06420101, "SET_WR_PTR wrong command word")

        command = self.get_next_word()
        self.assertEquals(command, 0x06420300, "SET_WR_PTR wrong command word")

    def test_write_value(self):
        self.assertRaises(exceptions.DataSpecificationNoRegionSelectedException,
                          self.dsg.write_value, 0x0)

        self.dsg.reserve_memory_region(0, 100)
        self.dsg.switch_write_focus(0)

        self.dsg.write_value(0x0)
        self.dsg.write_value(0x12)
        self.dsg.write_value(0x12345678)
        self.dsg.write_value(0x12345678, 2)
        self.dsg.write_value(0x12, 12)
        self.dsg.write_value(0x12, 0xFF, False, DataType.UINT8)
        self.dsg.write_value(0x12, 5, False, DataType.UINT16)
        self.dsg.write_value(0x123456789ABCDEFL, 5, False, DataType.UINT64)
        self.dsg.write_value(0x123456789ABCDEFL, 5, True, DataType.UINT64)
        self.dsg.write_value(0x123, 2, True, DataType.UINT64)

        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.write_value, 0, -1, True)
        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.write_value, 0, 0, False)
        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.write_value, 0, constants.MAX_REGISTERS, True)
        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.write_value, 0, -1, False)
        self.assertRaises(
                exceptions.DataSpecificationParameterOutOfBoundsException,
                self.dsg.write_value, 0, 256, False)

        self.skip_words(3)

        command = self.get_next_word()
        self.assertEquals(command, 0x14202001, "WRITE wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x00000000, "WRITE wrong data word")

        command = self.get_next_word()
        self.assertEquals(command, 0x14202001, "WRITE wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x00000012, "WRITE wrong data word")

        command = self.get_next_word()
        self.assertEquals(command, 0x14202001, "WRITE wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x12345678, "WRITE wrong data word")

        command = self.get_next_word()
        self.assertEquals(command, 0x14202002, "WRITE wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x12345678, "WRITE wrong data word")

        command = self.get_next_word()
        self.assertEquals(command, 0x1420200C, "WRITE wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x00000012, "WRITE wrong data word")

        command = self.get_next_word()
        self.assertEquals(command, 0x142000FF, "WRITE wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x00000012, "WRITE wrong data word")

        command = self.get_next_word()
        self.assertEquals(command, 0x14201005, "WRITE wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x00000012, "WRITE wrong data word")

        command = self.get_next_word()
        self.assertEquals(command, 0x24203005, "WRITE wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x89ABCDEF, "WRITE wrong data word")
        data = self.get_next_word()
        self.assertEquals(data, 0x01234567, "WRITE wrong data word")

        command = self.get_next_word()
        self.assertEquals(command, 0x24213050, "WRITE wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x89ABCDEF, "WRITE wrong data word")
        data = self.get_next_word()
        self.assertEquals(data, 0x01234567, "WRITE wrong data word")

        command = self.get_next_word()
        self.assertEquals(command, 0x24213020, "WRITE wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x00000123, "WRITE wrong data word")
        data = self.get_next_word()
        self.assertEquals(data, 0x00000000, "WRITE wrong data word")

    def test_write_structure(self):
        self.assertRaises(exceptions.DataSpecificationNotAllocatedException,
                          self.dsg.write_structure, 0)

        self.dsg.define_structure(0, [("first", DataType.UINT8, 0xAB)])
        self.dsg.define_structure(1, [("first", DataType.UINT8, 0xAB),
                                      ("second", DataType.UINT32, 0x12345679),
                                      ("third", DataType.INT16, None)])
        self.dsg.define_structure(0xA, [("first", DataType.UINT8, 0xAB)])

        self.dsg.write_structure(0)
        self.dsg.write_structure(0, 2)
        self.dsg.write_structure(0, 5, True)
        self.dsg.write_structure(1, 5, True)
        self.dsg.write_structure(0xA, 0xF)
        self.dsg.write_structure(0xA, 0xF, True)

        self.assertRaises(
                 exceptions.DataSpecificationParameterOutOfBoundsException,
                 self.dsg.write_structure, -1)
        self.assertRaises(
                 exceptions.DataSpecificationParameterOutOfBoundsException,
                 self.dsg.write_structure, constants.MAX_STRUCT_SLOTS)
        self.assertRaises(
                 exceptions.DataSpecificationParameterOutOfBoundsException,
                 self.dsg.write_structure, 1, -1, True)
        self.assertRaises(
                 exceptions.DataSpecificationParameterOutOfBoundsException,
                 self.dsg.write_structure, 1, constants.MAX_STRUCT_SLOTS, True)
        self.assertRaises(
                 exceptions.DataSpecificationParameterOutOfBoundsException,
                 self.dsg.write_structure, -1)
        self.assertRaises(
                 exceptions.DataSpecificationParameterOutOfBoundsException,
                 self.dsg.write_structure, 16)

        self.skip_words(15)

        command = self.get_next_word()
        self.assertEquals(command, 0x04400100,
                          "WRITE_STRUCT wrong command word")

        command = self.get_next_word()
        self.assertEquals(command, 0x04400200,
                          "WRITE_STRUCT wrong command word")

        command = self.get_next_word()
        self.assertEquals(command, 0x04420500,
                          "WRITE_STRUCT wrong command word")

        command = self.get_next_word()
        self.assertEquals(command, 0x04420501,
                          "WRITE_STRUCT wrong command word")

        command = self.get_next_word()
        self.assertEquals(command, 0x04400F0A,
                          "WRITE_STRUCT wrong command word")

        command = self.get_next_word()
        self.assertEquals(command, 0x04420F0A,
                          "WRITE_STRUCT wrong command word")

    def test_write_array(self):
        self.assertRaises(exceptions.DataSpecificationNoRegionSelectedException,
                          self.dsg.write_array, [0, 1, 2, 3], DataType.UINT8)

        self.dsg.reserve_memory_region(0, 100)
        self.dsg.switch_write_focus(0)

        self.dsg.write_array([], DataType.UINT8)
        self.dsg.write_array([0, 1, 2, 3], DataType.UINT8)
        self.dsg.write_array([0, 1, 2, 3], DataType.UINT16)
        self.dsg.write_array([0, 1, 2, 3], DataType.UINT32)
        self.dsg.write_array([0, 1, 2, 3, 4], DataType.UINT16)
        self.dsg.write_array([0, 1, 2, 3, 4], DataType.UINT8)

        self.skip_words(3)

        command = self.get_next_word()
        self.assertEquals(command, 0x14300001, "WRITE_ARRAY wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x00000000, "WRITE_ARRAY wrong command word")

        command = self.get_next_word()
        self.assertEquals(command, 0x14300001, "WRITE_ARRAY wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x00000004, "WRITE_ARRAY wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x03020100, "WRITE_ARRAY wrong data word")

        command = self.get_next_word()
        self.assertEquals(command, 0x14300002, "WRITE_ARRAY wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x00000004, "WRITE_ARRAY wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x00010000, "WRITE_ARRAY wrong data word")
        data = self.get_next_word()
        self.assertEquals(data, 0x00030002, "WRITE_ARRAY wrong data word")

        command = self.get_next_word()
        self.assertEquals(command, 0x14300004, "WRITE_ARRAY wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x00000004, "WRITE_ARRAY wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x00000000, "WRITE_ARRAY wrong data word")
        data = self.get_next_word()
        self.assertEquals(data, 0x00000001, "WRITE_ARRAY wrong data word")
        data = self.get_next_word()
        self.assertEquals(data, 0x00000002, "WRITE_ARRAY wrong data word")
        data = self.get_next_word()
        self.assertEquals(data, 0x00000003, "WRITE_ARRAY wrong data word")

        command = self.get_next_word()
        self.assertEquals(command, 0x14300002, "WRITE_ARRAY wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x00000005, "WRITE_ARRAY wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x00010000, "WRITE_ARRAY wrong data word")
        data = self.get_next_word()
        self.assertEquals(data, 0x00030002, "WRITE_ARRAY wrong data word")
        data = self.get_next_word()
        self.assertEquals(data, 0x00000004, "WRITE_ARRAY wrong data word")

        command = self.get_next_word()
        self.assertEquals(command, 0x14300001, "WRITE_ARRAY wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x00000005, "WRITE_ARRAY wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x03020100, "WRITE_ARRAY wrong data word")
        data = self.get_next_word()
        self.assertEquals(data, 0x00000004, "WRITE_ARRAY wrong data word")

    def test_set_structure_value(self):
        self.assertRaises(exceptions.DataSpecificationNotAllocatedException,
                          self.dsg.set_structure_value,
                          0, 0, 0, DataType.UINT32)

        self.dsg.define_structure(0, [("first", DataType.UINT8, 0xAB)])
        self.dsg.define_structure(1, [("first", DataType.UINT8, 0xAB),
                                      ("second", DataType.UINT32, 0x12345679),
                                      ("third", DataType.INT16, None)])
        self.dsg.define_structure(0xA, [("first", DataType.UINT8, 0xAB),
                                        ("second", DataType.UINT64, None)])

        self.dsg.set_structure_value(0, 0, 0x12, DataType.UINT8)
        self.dsg.set_structure_value(1, 2, 0x1234, DataType.INT16)
        self.dsg.set_structure_value(1, 1, 0x12345678, DataType.UINT32)
        self.dsg.set_structure_value(10, 1, 0x123456789ABCDEFL, DataType.UINT64)

        self.dsg.set_structure_value(1, 0, 2, DataType.UINT8, True)
        self.dsg.set_structure_value(1, 1, 3, DataType.UINT32, True)
        self.dsg.set_structure_value(10, 1, 5, DataType.UINT64, True)

        self.skip_words(16)

        command = self.get_next_word()
        self.assertEquals(command, 0x17200000, "WRITE_PARAM wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x00000012, "WRITE_PARAM wrong data word")

        command = self.get_next_word()
        self.assertEquals(command, 0x17201002, "WRITE_PARAM wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x00001234, "WRITE_PARAM wrong data word")

        command = self.get_next_word()
        self.assertEquals(command, 0x17201001, "WRITE_PARAM wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x12345678, "WRITE_PARAM wrong data word")

        command = self.get_next_word()
        self.assertEquals(command, 0x2720A001, "WRITE_PARAM wrong command word")
        data = self.get_next_word()
        self.assertEquals(data, 0x89ABCDEF, "WRITE_PARAM wrong data word")
        data = self.get_next_word()
        self.assertEquals(data, 0x01234567, "WRITE_PARAM wrong data word")

        command = self.get_next_word()
        self.assertEquals(command, 0x07221200, "WRITE_PARAM wrong command word")

        command = self.get_next_word()
        self.assertEquals(command, 0x07221301, "WRITE_PARAM wrong command word")

        command = self.get_next_word()
        self.assertEquals(command, 0x0722A501, "WRITE_PARAM wrong command word")


    def test_call_random_distribution(self):
        self.assertEqual(True, False, "Not implemented yet")

    def test_declare_uniform_random_distribution(self):
        self.assertEqual(True, False, "Not implemented yet")

    def test_end_specification(self):
        self.assertEqual(True, False, "Not implemented yet")




if __name__ == '__main__':
    unittest.main()
