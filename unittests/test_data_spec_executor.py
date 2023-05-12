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
import struct
from tempfile import mktemp
from data_specification.config_setup import unittest_setup
from data_specification.enums import DataType
from data_specification import (
    DataSpecificationExecutor, DataSpecificationGenerator, constants,
    MemoryRegionReference, MemoryRegionReal)
from data_specification.exceptions import NoMoreException


class TestDataSpecExecutor(unittest.TestCase):

    def setUp(self):
        unittest_setup()

    def test_simple_spec(self):
        # Write a data spec to execute
        spec = DataSpecificationGenerator()
        spec.reserve_memory_region(0, 100)
        spec.reserve_memory_region(1, 200, empty=True)
        spec.reserve_memory_region(2, 4)
        spec.reserve_memory_region(3, 12, reference=1)
        spec.reference_memory_region(4, 2)
        spec.switch_write_focus(0)
        spec.write_array([0, 1, 2])
        spec.set_write_pointer(20)
        spec.write_value(4)
        spec.switch_write_focus(2)
        spec.write_value(3)
        spec.set_write_pointer(0)
        spec.write_value(10)
        spec.end_specification()

        spec_reader = io.BytesIO(spec.get_bytes_after_close())

        # Execute the spec
        executor = DataSpecificationExecutor(spec_reader, 400)
        executor.execute()

        # Test the size
        header_and_table_size = ((constants.MAX_MEM_REGIONS * 3) + 2) * 4
        self.assertEqual(
            executor.get_constructed_data_size(),
            header_and_table_size + 100 + 200 + 4 + 12)

        # Test the unused regions
        for region in range(5, constants.MAX_MEM_REGIONS):
            self.assertIsNone(executor.get_region(region))

        # Test region 0
        region_0 = executor.get_region(0)
        self.assertEqual(region_0.allocated_size, 100)
        self.assertEqual(region_0.max_write_pointer, 24)
        self.assertFalse(region_0.unfilled)
        self.assertIsNone(region_0.reference)
        self.assertEqual(
            region_0.region_data[:region_0.max_write_pointer],
            struct.pack("<IIIIII", 0, 1, 2, 0, 0, 4))

        # Test region 1
        region_1 = executor.get_region(1)
        self.assertIsInstance(region_1, MemoryRegionReal)
        self.assertEqual(region_1.allocated_size, 200)
        self.assertTrue(region_1.unfilled)
        self.assertIsNone(region_1.reference)

        # Test region 2
        region_2 = executor.get_region(2)
        self.assertIsInstance(region_2, MemoryRegionReal)
        self.assertEqual(region_2.allocated_size, 4)
        self.assertIsNone(region_2.reference)
        self.assertEqual(region_2.region_data, struct.pack("<I", 10))

        # Test region 3
        region_3 = executor.get_region(3)
        self.assertIsInstance(region_3, MemoryRegionReal)
        self.assertEqual(region_3.allocated_size, 12)
        self.assertEqual(region_3.reference, 1)
        self.assertEqual(executor.referenceable_regions, [3])

        # Test region 4
        region_4 = executor.get_region(4)
        self.assertIsInstance(region_4, MemoryRegionReference)
        self.assertEqual(region_4.ref, 2)
        self.assertEqual(executor.references_to_fill, [4])

        # Test the pointer table
        table = executor.get_pointer_table(0)
        self.assertEqual(len(table), constants.MAX_MEM_REGIONS)
        self.assertEqual(table[0]["pointer"], header_and_table_size)
        self.assertEqual(table[1]["pointer"], header_and_table_size + 100)
        self.assertEqual(table[2]["pointer"], header_and_table_size + 300)
        self.assertEqual(table[3]["pointer"], header_and_table_size + 304)
        # 4 is also 0 because it is a reference
        for region in range(4, constants.MAX_MEM_REGIONS):
            self.assertEqual(table[region]["pointer"], 0)

        # Test the header
        header = executor.get_header()
        self.assertEqual(len(header), 2)
        self.assertEqual(header[0], constants.APPDATA_MAGIC_NUM)
        self.assertEqual(header[1], constants.DSE_VERSION)

    def test_trivial_spec(self):
        spec = DataSpecificationGenerator()
        spec.end_specification()

        spec_bytes = io.BytesIO(spec.get_bytes_after_close())

        executor = DataSpecificationExecutor(spec_bytes, 400)
        executor.execute()
        for r in range(constants.MAX_MEM_REGIONS):
            self.assertIsNone(executor.get_region(r))

    def test_complex_spec(self):
        spec = DataSpecificationGenerator()
        spec.reserve_memory_region(0, 44)
        spec.switch_write_focus(0)
        spec.set_register_value(3, 0x31323341)
        spec.write_value_from_register(3)
        spec.set_register_value(3, 0x31323342)
        spec.write_value_from_register(3)
        spec.set_register_value(3, 0x31323344)
        spec.write_value_from_register(3)
        spec.set_register_value(3, 0x31323347)
        spec.write_value_from_register(3)
        spec.set_register_value(3, 0x3132334B)
        spec.write_value_from_register(3)
        spec.set_register_value(2, 24)
        spec.set_write_pointer(2, address_is_register=True)
        spec.write_array([0x61, 0x62, 0x63, 0x64], data_type=DataType.UINT8)
        spec.set_register_value(5, 4)
        spec.write_repeated_value(0x70, 5, repeats_is_register=True,
                                  data_type=DataType.UINT8)
        spec.write_value(0x7d, data_type=DataType.INT64)
        spec.end_specification()

        spec_bytes = io.BytesIO(spec.get_bytes_after_close())

        executor = DataSpecificationExecutor(spec_bytes, 400)
        executor.execute()
        r = executor.get_region(0)
        self.assertEqual(r.allocated_size, 44)
        self.assertEqual(r.max_write_pointer, 40)
        self.assertFalse(r.unfilled)
        self.assertEqual(r.region_data, bytearray(
            "A321" "B321" "D321" "G321" "K321" "\0\0\0\0" "abcd" "pppp"
            "}\0\0\0" "\0\0\0\0" "\0\0\0\0".encode("ISO 8859-1")))

    def test_overwrite(self):
        spec = DataSpecificationGenerator()
        spec.reserve_memory_region(0, 4)
        spec.switch_write_focus(0)
        spec.write_value(1)
        spec.write_value(2)
        spec.end_specification()

        spec_bytes = io.BytesIO(spec.get_bytes_after_close())

        executor = DataSpecificationExecutor(spec_bytes, 400)
        self.assertRaises(NoMoreException, executor.execute)


if __name__ == '__main__':
    unittest.main()
