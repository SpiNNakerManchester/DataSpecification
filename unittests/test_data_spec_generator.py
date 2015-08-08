import unittest
import struct
from io import BytesIO
from StringIO import StringIO

from data_specification import constants, exceptions
from data_specification.enums.data_type import DataType
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

        self.assertEqual(command, 0x00000000, "BREAK command word wrong")

        command = self.spec_writer.read(1)
        self.assertEqual(command, "", "BREAK added more words")

    def test_no_operation(self):
        self.dsg.no_operation()

        command = self.get_next_word()
        self.assertEqual(command, 0x00100000, "NOP command word wrong")

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
                         "RESERVE command word wrong for memory region 1")
        command = self.get_next_word()
        self.assertEqual(command, 0x111,
                         "RESERVE size word wrong for memory region 1")
        command = self.get_next_word()
        self.assertEqual(command, 0x10200002,
                         "RESERVE command word wrong for memory region 2")
        command = self.get_next_word()
        self.assertEqual(command, 0x1122,
                         "RESERVE size word wrong for memory region 2")
        command = self.get_next_word()
        self.assertEqual(command, 0x10200083,
                         "RESERVE command word wrong for memory region 3")
        command = self.get_next_word()
        self.assertEqual(command, 0x1122,
                         "RESERVE size word wrong for memory region 3")
        command = self.get_next_word()
        self.assertEqual(command, 0x10200004,
                         "RESERVE command word wrong for memory region 4")
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

        self.assertEqual(True, False, "Not implemented yet")

    def test_align_write_pointer(self):
        self.assertEqual(True, False, "Not implemented yet")

    def test_break_loop(self):
        self.assertEqual(True, False, "Not implemented yet")

    def test_call_arithmetic_operation(self):
        self.assertEqual(True, False, "Not implemented yet")

    def test_call_function(self):
        self.assertEqual(True, False, "Not implemented yet")

    def test_call_logic_operation(self):
        self.assertEqual(True, False, "Not implemented yet")

    def test_call_random_distribution(self):
        self.assertEqual(True, False, "Not implemented yet")

    def test_comment(self):
        self.assertEqual(True, False, "Not implemented yet")

    def test_copy_structure(self):
        self.assertEqual(True, False, "Not implemented yet")

    def test_copy_structure_parameter(self):
        self.assertEqual(True, False, "Not implemented yet")

    def test_declare_random_number_generator(self):
        self.assertEqual(True, False, "Not implemented yet")

    def test_declare_uniform_random_distribution(self):
        self.assertEqual(True, False, "Not implemented yet")

    def test_define_structure(self):
        self.assertEqual(True, False, "Not implemented yet")

    def test_else_conditional(self):
        self.assertEqual(True, False, "Not implemented yet")

    def test_end_conditional(self):
        self.assertEqual(True, False, "Not implemented yet")

    def test_end_function(self):
        self.assertEqual(True, False, "Not implemented yet")

    def test_end_loop(self):
        self.assertEqual(True, False, "Not implemented yet")

    def test_end_specification(self):
        self.assertEqual(True, False, "Not implemented yet")

    def test_free_memory_region(self):
        self.assertEqual(True, False, "Not implemented yet")

    def test_print_struct(self):
        self.assertEqual(True, False, "Not implemented yet")

    def test_print_text(self):
        self.assertEqual(True, False, "Not implemented yet")

    def test_print_value(self):
        self.assertEqual(True, False, "Not implemented yet")

    def test_save_write_pointer(self):
        self.assertEqual(True, False, "Not implemented yet")

    def test_set_register_value(self):
        self.assertEqual(True, False, "Not implemented yet")

    def test_set_structure_value(self):
        self.assertEqual(True, False, "Not implemented yet")

    def test_set_write_pointer(self):
        self.assertEqual(True, False, "Not implemented yet")

    def test_start_conditional(self):
        self.assertEqual(True, False, "Not implemented yet")

    def test_start_function(self):
        self.assertEqual(True, False, "Not implemented yet")

    def test_start_loop(self):
        self.assertEqual(True, False, "Not implemented yet")

    def test_switch_write_focus(self):
        self.assertEqual(True, False, "Not implemented yet")

    def test_write_array(self):
        self.assertEqual(True, False, "Not implemented yet")

    def test_write_structure(self):
        self.assertEqual(True, False, "Not implemented yet")

    def test_write_value(self):
        self.assertEqual(True, False, "Not implemented yet")



if __name__ == '__main__':
    unittest.main()
