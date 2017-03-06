import unittest
import inspect
import os.path

from spinn_storage_handlers.file_data_reader import FileDataReader


class TestFileDataReader(unittest.TestCase):
    def setUp(self):
        self.reader = None
        self._dir = os.path.dirname(inspect.getfile(self.__class__))

    def _file(self, filename):
        return os.path.join(self._dir, "files_data_reader", filename)

    def tearDown(self):
        if self.reader is not None:
            self.reader.close()

    # ------------- TESTS START BELOW HERE -------------

    def test_read_one_byte(self):
        self.reader = FileDataReader(self._file('txt_one_byte'))
        stream = self.reader.read(1)

        self.assertEqual(stream[0], '1')

    def test_readinto_one_byte(self):
        self.reader = FileDataReader(self._file('txt_one_byte'))
        ba = bytearray(1)
        self.reader.readinto(ba)

        self.assertEqual(len(ba), 1)
        self.assertEqual(ba[0], ord('1'))

    def test_read_five_bytes(self):
        self.reader = FileDataReader(self._file('txt_5_bytes'))
        stream = self.reader.read(5)

        self.assertEqual(len(stream), 5)
        self.assertEqual(stream[0], '1')
        self.assertEqual(stream[1], '2')
        self.assertEqual(stream[2], '3')
        self.assertEqual(stream[3], '4')
        self.assertEqual(stream[4], '5')

    def test_read_from_empty_file(self):
        self.reader = FileDataReader(self._file('txt_empty'))
        stream = self.reader.read(1)
        self.assertEqual(len(stream), 0)

    def test_read_truncate(self):
        self.reader = FileDataReader(
            self._file('txt_one_byte_from_multiple_bytes'))
        stream = self.reader.read(2)
        self.assertEqual(len(stream), 2)
        self.assertEqual(stream[0], '\xf0')
        self.assertEqual(stream[1], '\xa4')


if __name__ == '__main__':
    unittest.main()
