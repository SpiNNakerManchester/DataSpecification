import unittest
import struct
from tempfile import mktemp
from spinn_machine import SDRAM
from spinn_storage_handlers import FileDataWriter, FileDataReader
from data_specification.enums import DataType
from data_specification import (
    DataSpecificationExecutor, DataSpecificationGenerator, constants)
from data_specification.exceptions import NoMoreException


class TestDataSpecExecutor(unittest.TestCase):

    def test_simple_spec(self):

        # Create a sdram just to set max chip size
        SDRAM(1000)
        # Write a data spec to execute
        temp_spec = mktemp()
        spec_writer = FileDataWriter(temp_spec)
        spec = DataSpecificationGenerator(spec_writer)
        spec.reserve_memory_region(0, 100)
        spec.reserve_memory_region(1, 200, empty=True)
        spec.reserve_memory_region(2, 4)
        spec.switch_write_focus(0)
        spec.write_array([0, 1, 2])
        spec.set_write_pointer(20)
        spec.write_value(4)
        spec.switch_write_focus(2)
        spec.write_value(3)
        spec.set_write_pointer(0)
        spec.write_value(10)
        spec.end_specification()

        # Execute the spec
        spec_reader = FileDataReader(temp_spec)
        executor = DataSpecificationExecutor(spec_reader, 400)
        executor.execute()

        # Test the size
        header_and_table_size = (constants.MAX_MEM_REGIONS + 2) * 4
        self.assertEquals(
            executor.get_constructed_data_size(),
            header_and_table_size + 100 + 200 + 4)

        # Test the unused regions
        for region in range(3, constants.MAX_MEM_REGIONS):
            self.assertIsNone(executor.get_region(region))

        # Test region 0
        region_0 = executor.get_region(0)
        self.assertEquals(region_0.allocated_size, 100)
        self.assertEquals(region_0.max_write_pointer, 24)
        self.assertFalse(region_0.unfilled)
        self.assertEquals(
            region_0.region_data[:region_0.max_write_pointer],
            struct.pack("<IIIIII", 0, 1, 2, 0, 0, 4))

        # Test region 1
        region_1 = executor.get_region(1)
        self.assertEquals(region_1.allocated_size, 200)
        self.assertTrue(region_1.unfilled)

        # Test region 2
        region_2 = executor.get_region(2)
        self.assertEquals(region_2.allocated_size, 4)
        self.assertEquals(region_2.region_data, struct.pack("<I", 10))

        # Test the pointer table
        table = executor.get_pointer_table(0)
        self.assertEquals(len(table), constants.MAX_MEM_REGIONS)
        self.assertEquals(table[0], header_and_table_size)
        self.assertEquals(table[1], header_and_table_size + 100)
        self.assertEquals(table[2], header_and_table_size + 300)
        for region in range(3, constants.MAX_MEM_REGIONS):
            self.assertEquals(table[region], 0)

        # Test the header
        header = executor.get_header()
        self.assertEquals(len(header), 2)
        self.assertEquals(header[0], constants.APPDATA_MAGIC_NUM)
        self.assertEquals(header[1], constants.DSE_VERSION)

    def test_trivial_spec(self):
        temp_spec = mktemp()
        spec = DataSpecificationGenerator(FileDataWriter(temp_spec))
        spec.end_specification()

        executor = DataSpecificationExecutor(FileDataReader(temp_spec), 400)
        executor.execute()
        for r in range(constants.MAX_MEM_REGIONS):
            self.assertIsNone(executor.get_region(r))

    def test_complex_spec(self):
        # Create a sdram just to set max chip size
        SDRAM(1000)
        temp_spec = mktemp()
        spec = DataSpecificationGenerator(FileDataWriter(temp_spec))
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

        executor = DataSpecificationExecutor(FileDataReader(temp_spec), 400)
        executor.execute()
        r = executor.get_region(0)
        self.assertEquals(r.allocated_size, 44)
        self.assertEquals(r.max_write_pointer, 40)
        self.assertFalse(r.unfilled)
        self.assertEquals(r.region_data, bytearray(
            "A321" "B321" "D321" "G321" "K321" "\0\0\0\0" "abcd" "pppp"
            "}\0\0\0" "\0\0\0\0" "\0\0\0\0".encode("ISO 8859-1")))

    def test_overwrite(self):
        # Create a sdram just to set max chip size
        SDRAM(1000)
        temp_spec = mktemp()
        spec = DataSpecificationGenerator(FileDataWriter(temp_spec))
        spec.reserve_memory_region(0, 4)
        spec.switch_write_focus(0)
        spec.write_value(1)
        spec.write_value(2)
        spec.end_specification()

        executor = DataSpecificationExecutor(FileDataReader(temp_spec), 400)
        self.assertRaises(NoMoreException, executor.execute)


if __name__ == '__main__':
    unittest.main()
