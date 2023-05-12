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
import io
import os
import struct
import tempfile
from data_specification import constants, DataSpecificationGenerator
from data_specification.config_setup import unittest_setup
from data_specification.exceptions import (
    TypeMismatchException, ParameterOutOfBoundsException,
    RegionInUseException, NotAllocatedException,
    NoRegionSelectedException, RegionUnfilledException)
from data_specification.enums import DataType

_64BIT_VALUE = 0x1234567890ABCDEF


class TestDataSpecGeneration(unittest.TestCase):
    def setUp(self):
        #raise self.skipTest("sysncronise read and write no longer supported")
        unittest_setup()
        self.temp_dir = tempfile.mkdtemp()
        self.spec_file = os.path.join(self.temp_dir, "spec")
        self.report_file = os.path.join(self.temp_dir, "report")
        self.spec_writer = io.FileIO(self.spec_file, "wb")
        self.report_writer = io.TextIOWrapper(io.FileIO(self.report_file, "w"))
        self.spec_reader = io.FileIO(self.spec_file, "rb")
        self.report_reader = io.TextIOWrapper(io.FileIO(self.report_file, "r"))
        self.dsg = DataSpecificationGenerator(self.report_writer)

    def tearDown(self):
        self.spec_reader.close()
        self.report_reader.close()
        os.remove(self.spec_file)
        os.remove(self.report_file)
        os.rmdir(self.temp_dir)

    def get_next_word(self, count=1):
        self.spec_writer.flush()
        if count < 2:
            return struct.unpack("<I", self.spec_reader.read(4))[0]
        words = list()
        for _ in range(count):
            words.append(struct.unpack("<I", self.spec_reader.read(4))[0])
        return words

    def skip_words(self, words):
        self.spec_writer.flush()
        self.spec_reader.read(4 * words)

    def test_new_data_spec_generator(self):
        self.assertEqual(self.dsg._report_writer, self.report_writer)
        self.assertEqual(self.dsg._instruction_counter, 0)
        self.assertEqual(self.dsg._mem_slots,
                         constants.MAX_MEM_REGIONS * [None])
        self.assertEqual(self.dsg._function_slots,
                         constants.MAX_CONSTRUCTORS * [None])
        self.assertEqual(self.dsg._struct_slots,
                         constants.MAX_STRUCT_SLOTS * [None])

    def test_reserve_memory_region(self):
        self.dsg.reserve_memory_region(1, 0x111)
        self.dsg.reserve_memory_region(2, 0x1122)
        self.dsg.reserve_memory_region(3, 0x1122, empty=True)
        self.dsg.reserve_memory_region(4, 0x3344, label='test')
        self.dsg.reserve_memory_region(5, 0x5564, reference=1)

        with self.assertRaises(ParameterOutOfBoundsException):
            self.dsg.reserve_memory_region(-1, 0x100)
        with self.assertRaises(ParameterOutOfBoundsException):
            self.dsg.reserve_memory_region(constants.MAX_MEM_REGIONS, 0x100)
        with self.assertRaises(RegionInUseException):
            self.dsg.reserve_memory_region(1, 0x100)

        # RESERVE for memory region 1
        #self.assertEqual(self.get_next_word(2), [0x10200001, 0x111])
        # RESERVE for memory region 2
        #self.assertEqual(self.get_next_word(2), [0x10200002, 0x1122])
        # RESERVE for memory region 3
        #self.assertEqual(self.get_next_word(2), [0x10200083, 0x1122])
        # RESERVE for memory region 4
        #self.assertEqual(self.get_next_word(2), [0x10200004, 0x3344])
        # RESERVE for memory region 5
        #self.assertEqual(self.get_next_word(3), [0x20200045, 0x5564, 1])
        # Memory region 1 DSG data wrong
        self.assertEqual(self.dsg._mem_slots[1].size, 0x114)
        self.assertIsNone(self.dsg._mem_slots[1].label)
        self.assertEqual(self.dsg._mem_slots[1].empty, False)
        # Memory region 2 DSG data wrong
        self.assertEqual(self.dsg._mem_slots[2].size, 0x1124)
        self.assertIsNone(self.dsg._mem_slots[2].label)
        self.assertEqual(self.dsg._mem_slots[2].empty, False)
        # Memory region 3 DSG data wrong
        self.assertEqual(self.dsg._mem_slots[3].size, 0x1124)
        self.assertIsNone(self.dsg._mem_slots[3].label)
        self.assertEqual(self.dsg._mem_slots[3].empty, True)
        # FREE wrong command word
        self.assertEqual(self.dsg._mem_slots[4].size, 0x3344)
        self.assertEqual(self.dsg._mem_slots[4].label, "test")
        self.assertEqual(self.dsg._mem_slots[4].empty, False)
        # Memory region 4 DSG data
        self.assertEqual(self.dsg._mem_slots[5].size, 0x5564)
        self.assertIsNone(self.dsg._mem_slots[5].label)
        self.assertEqual(self.dsg._mem_slots[5].empty, False)

    def test_reference_memory_region(self):
        self.dsg.reference_memory_region(1, 1)
        self.dsg.reference_memory_region(2, 2, label="TestRef")

        with self.assertRaises(ParameterOutOfBoundsException):
            self.dsg.reference_memory_region(-1, 3)
        with self.assertRaises(ParameterOutOfBoundsException):
            self.dsg.reference_memory_region(constants.MAX_MEM_REGIONS, 0)

        # REFERENCE for memory region 1
        #self.assertEqual(self.get_next_word(2), [0x10400001, 1])
        # REFERENCE for memory region 2
        #self.assertEqual(self.get_next_word(2), [0x10400002, 2])

        self.assertEqual(self.dsg._mem_slots[1].size, 0)
        self.assertIsNone(self.dsg._mem_slots[1].label)
        self.assertEqual(self.dsg._mem_slots[1].empty, True)

        self.assertEqual(self.dsg._mem_slots[2].size, 0)
        self.assertEqual(self.dsg._mem_slots[2].label, "TestRef")
        self.assertEqual(self.dsg._mem_slots[2].empty, True)

    def test_comment(self):
        self.dsg.comment("test")

        # Comment generated data specification
        self.report_writer.flush()
        self.assertEqual(self.spec_writer.tell(), 0)
        self.assertEqual(self.report_reader.read(), "test\n")

    def test_switch_write_focus(self):
        self.dsg.reserve_memory_region(0, 100)
        self.dsg.reserve_memory_region(2, 100)
        self.dsg.reserve_memory_region(1, 100, empty=True)

        self.dsg.switch_write_focus(0)
        self.dsg.switch_write_focus(2)

        with self.assertRaises(NotAllocatedException):
            self.dsg.switch_write_focus(3)
        with self.assertRaises(RegionUnfilledException):
            self.dsg.switch_write_focus(1)
        with self.assertRaises(ParameterOutOfBoundsException):
            self.dsg.switch_write_focus(-1)
        with self.assertRaises(ParameterOutOfBoundsException):
            self.dsg.switch_write_focus(constants.MAX_MEM_REGIONS)

        self.skip_words(6)
        # SWITCH_FOCUS
        #self.assertEqual(self.get_next_word(), 0x05000000)
        #self.assertEqual(self.get_next_word(), 0x05000200)

    def test_set_write_pointer(self):
        with self.assertRaises(NoRegionSelectedException):
            self.dsg.set_write_pointer(0x100)

        # Define a memory region and switch focus to it
        self.dsg.reserve_memory_region(1, 100)
        self.dsg.switch_write_focus(1)

        self.dsg.set_write_pointer(0x12345678, False, False)
        self.dsg.set_write_pointer(0x00000078, False, False)
        self.dsg.set_write_pointer(0x12, False, True)
        self.dsg.set_write_pointer(-12, False, True)
        self.dsg.set_write_pointer(1, True, True)
        self.dsg.set_write_pointer(3, True, False)

        with self.assertRaises(ParameterOutOfBoundsException):
            self.dsg.set_write_pointer(-1, True)
        with self.assertRaises(ParameterOutOfBoundsException):
            self.dsg.set_write_pointer(constants.MAX_REGISTERS, True)
        with self.assertRaises(ParameterOutOfBoundsException):
            self.dsg.set_write_pointer(0x123456789, False)

        self.skip_words(3)
        # SET_WR_PTR
        #self.assertEqual(self.get_next_word(2), [0x16400000, 0x12345678])
        #self.assertEqual(self.get_next_word(2), [0x16400000, 0x00000078])
        #self.assertEqual(self.get_next_word(2), [0x16400001, 0x00000012])
        #self.assertEqual(self.get_next_word(2), [0x16400001, 0xFFFFFFF4])
        #self.assertEqual(self.get_next_word(), 0x06420101)
        #self.assertEqual(self.get_next_word(), 0x06420300)

    def test_write_value(self):
        with self.assertRaises(NoRegionSelectedException):
            self.dsg.write_value(0x0)

        self.dsg.reserve_memory_region(0, 100)
        self.dsg.switch_write_focus(0)

        self.dsg.write_value(0x0)
        self.dsg.write_value(0x12)
        self.dsg.write_value(0x12345678)

        self.skip_words(3)
        # WRITE
        #self.assertEqual(self.get_next_word(2), [0x14202001, 0x00000000])
        #self.assertEqual(self.get_next_word(2), [0x14202001, 0x00000012])
        #self.assertEqual(self.get_next_word(2), [0x14202001, 0x12345678])
        #self.assertEqual(self.get_next_word(2), [0x14202002, 0x12345678])
        #self.assertEqual(self.get_next_word(2), [0x1420200C, 0x00000012])
        #self.assertEqual(self.get_next_word(2), [0x142000FF, 0x00000012])
        #self.assertEqual(self.get_next_word(2), [0x14201005, 0x00000012])
        #self.assertEqual(self.get_next_word(3),
        #                 [0x24203005, 0x90ABCDEF, 0x12345678])
        #self.assertEqual(self.get_next_word(3),
        #                 [0x24213050, 0x90ABCDEF, 0x12345678])
        #self.assertEqual(self.get_next_word(3),
        #                 [0x24213020, 0x00000123, 0x00000000])

    def test_write_array(self):
        with self.assertRaises(NoRegionSelectedException):
            self.dsg.write_array([0, 1, 2, 3], DataType.UINT8)

        self.dsg.reserve_memory_region(0, 100)
        self.dsg.switch_write_focus(0)

        self.dsg.write_array([], DataType.UINT8)
        self.dsg.write_array([], DataType.UINT32)
        self.dsg.write_array([0, 1, 2, 3], DataType.UINT8)
        self.dsg.write_array([0, 1, 2, 3], DataType.UINT16)
        self.dsg.write_array([0, 1, 2, 3], DataType.UINT32)
        self.dsg.write_array([0, 1, 2, 3, 4, 5], DataType.UINT16)
        self.dsg.write_array([0, 1, 2, 3, 4, 5, 6, 7], DataType.UINT8)

        self.skip_words(3)
        # WRITE_ARRAY
        #self.assertEqual(self.get_next_word(2), [0x14300001, 0])
        #self.assertEqual(self.get_next_word(2), [0x14300004, 0])
        #self.assertEqual(self.get_next_word(3), [0x14300001, 1, 0x03020100])
        #self.assertEqual(self.get_next_word(4),
        #                 [0x14300002, 2, 0x00010000, 0x00030002])
        #self.assertEqual(self.get_next_word(6), [0x14300004, 4, 0, 1, 2, 3])
        #self.assertEqual(self.get_next_word(5),
        #                 [0x14300002, 3, 0x00010000, 0x00030002, 0x00050004])
        #self.assertEqual(self.get_next_word(4),
        #                [0x14300001, 2, 0x03020100, 0x07060504])

    def test_end_specification(self):
        self.dsg.end_specification(False)

        # END_SPEC
        #self.assertEqual(self.get_next_word(), 0x0FF00000)

        self.dsg.end_specification()
        #with self.assertRaises(ValueError):
        #    self.get_next_word()


if __name__ == '__main__':
    unittest.main()
