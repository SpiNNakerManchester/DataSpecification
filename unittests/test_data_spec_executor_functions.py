import unittest
from data_specification import DataSpecificationExecutorFunctions


class MyTestCase(unittest.TestCase):
    @unittest.skip("unimplemented test")
    def test_something(self):
        DataSpecificationExecutorFunctions()
        self.assertEqual(True, False, "Test not implemented yet")


if __name__ == '__main__':
    unittest.main()
