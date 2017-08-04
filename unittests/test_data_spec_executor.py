import unittest
from tempfile import mktemp
import struct

from data_specification \
    import DataSpecificationExecutor, DataSpecificationGenerator, constants

from spinn_storage_handlers import FileDataWriter, FileDataReader


class TestDataSpecExecutor(unittest.TestCase):

    def test_simple_spec(self):

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
        self.assertEqual(
            executor.get_constructed_data_size(),
            header_and_table_size + 100 + 200 + 4)

        # Test the unused regions
        for region in range(3, constants.MAX_MEM_REGIONS):
            self.assertIsNone(executor.get_region(region))

        # Test region 0
        region_0 = executor.get_region(0)
        self.assertEqual(region_0.allocated_size, 100)
        self.assertEqual(region_0.max_write_pointer, 24)
        self.assertFalse(region_0.unfilled)
        self.assertEqual(
            region_0.region_data[:region_0.max_write_pointer],
            struct.pack("<IIIIII", 0, 1, 2, 0, 0, 4))

        # Test region 1
        region_1 = executor.get_region(1)
        self.assertEqual(region_1.allocated_size, 200)
        self.assertTrue(region_1.unfilled)

        # Test region 2
        region_2 = executor.get_region(2)
        self.assertEqual(region_2.allocated_size, 4)
        self.assertEqual(region_2.region_data, struct.pack("<I", 10))

        # Test the pointer table
        table = executor.get_pointer_table(0)
        self.assertEqual(len(table), constants.MAX_MEM_REGIONS)
        self.assertEqual(table[0], header_and_table_size)
        self.assertEqual(table[1], header_and_table_size + 100)
        self.assertEqual(table[2], header_and_table_size + 300)
        for region in range(3, constants.MAX_MEM_REGIONS):
            self.assertEqual(table[region], 0)

        # Test the header
        header = executor.get_header()
        self.assertEqual(len(header), 2)
        self.assertEqual(header[0], constants.APPDATA_MAGIC_NUM)
        self.assertEqual(header[1], constants.DSE_VERSION)


if __name__ == '__main__':
    unittest.main()
