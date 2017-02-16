import unittest
from data_specification.data_specification_executor \
    import DataSpecificationExecutor


class MyTestCase(unittest.TestCase):
    @unittest.skip("unimplemented test")
    def test_something(self):
        DataSpecificationExecutor()
        self.assertEqual(True, False, "Test not implemented yet")


if __name__ == '__main__':
    unittest.main()
