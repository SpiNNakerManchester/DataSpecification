import unittest
import inspect
import os.path

from spinn_storage_handlers import FileDataWriter


class TestFileDataWriter(unittest.TestCase):
    def setUp(self):
        self._dir = os.path.dirname(inspect.getfile(self.__class__))

    def _file(self, filename):
        return os.path.join(self._dir, "files_data_writer", filename)

    def test_write_one_byte(self):
        self.writer = FileDataWriter(self._file('txt_one_byte'))
        self.writer.write(bytearray([0]))
        self.writer.close()

        with open(self._file('txt_one_byte'), "r") as file_handle:
            self.assertEqual(file_handle.read(1), '\x00')
            self.assertEqual(file_handle.read(1), '')

    def test_write_five_bytes(self):
        self.writer = FileDataWriter(self._file('txt_5_bytes'))
        self.writer.write(bytearray([1, 2, 3, 4, 5]))
        self.writer.close()

        with open(self._file('txt_5_bytes'), "r") as file_handle:
            self.assertEqual(file_handle.read(1), '\x01')
            self.assertEqual(file_handle.read(1), '\x02')
            self.assertEqual(file_handle.read(1), '\x03')
            self.assertEqual(file_handle.read(1), '\x04')
            self.assertEqual(file_handle.read(1), '\x05')
            self.assertEqual(file_handle.read(1), '')

    def test_write_from_empty_file(self):
        self.writer = FileDataWriter(self._file('txt_empty'))
        self.writer.write(bytearray())
        self.writer.close()

        with open(self._file('txt_empty'), "r") as file_handle:
            self.assertEqual(file_handle.read(1), '')


if __name__ == '__main__':
    unittest.main()
