import os.path
import unittest
from data_specification.utility_calls import (
    get_region_base_address_offset, get_data_spec_and_file_writer_filename)


class TestingUtilities(unittest.TestCase):
    def test_get_region_base_address_offset(self):
        val = get_region_base_address_offset(48, 7)
        self.assertEqual(val, 84)

    def test_get_data_spec_and_file_writer_filename(self):
        a, b = get_data_spec_and_file_writer_filename(
            2, 3, 5, "example.com", "TEMP", True, "TEMP")
        self.assertEqual(os.path.split(a)[-1],
                         "example.com_dataSpec_2_3_5.dat")
        # Should be a DSG
        self.assertEqual(b.region_sizes,
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])


if __name__ == '__main__':
    unittest.main()
