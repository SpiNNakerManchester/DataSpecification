import unittest
from data_specification.memory_region_collection import MemoryRegionCollection


class MyTestCase(unittest.TestCase):
    @unittest.skip("unimplemented test")
    def test_something(self):
        MemoryRegionCollection()
        self.assertEqual(True, False, "Test not implemented yet")


if __name__ == '__main__':
    unittest.main()
