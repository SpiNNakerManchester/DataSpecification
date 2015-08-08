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

    def test_reserve_memory_region(self):
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
