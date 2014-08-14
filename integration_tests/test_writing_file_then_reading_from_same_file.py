import unittest
from data_specification.file_data_writer import FileDataWriter
from data_specification.file_data_reader import FileDataReader


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.reader = None

    def tearDown(self):
        if self.reader is not None:
            self.reader.close()

    def test_one_byte(self):
        self.writer = FileDataWriter('data_files/txt_one_byte')
        self.writer.write(bytearray([1]))
        self.writer.close()
        with open('data_files/txt_one_byte', "rb") as file_handle:
            self.assertEqual(file_handle.read(1), '\x01')
            self.assertEqual(file_handle.read(1), '')
        self.reader = FileDataReader('data_files/txt_one_byte')
        stream = self.reader.read(1)
        self.assertEqual(stream[0], 1)

    def test_readinto_one_byte(self):
        self.writer = FileDataWriter('data_files/txt_one_byte')
        self.writer.write(bytearray([5]))
        self.writer.close()
        with open('data_files/txt_one_byte', "rb") as file_handle:
            self.assertEqual(file_handle.read(1), '\x05')
            self.assertEqual(file_handle.read(1), '')
        self.reader = FileDataReader('data_files/txt_one_byte')
        ba = bytearray(1)
        self.reader.readinto(ba)
        self.assertEqual(len(ba), 1)
        self.assertEqual(ba[0], 5)

    def test_read_five_bytes(self):
        self.writer = FileDataWriter('data_files/txt_5_bytes')
        self.writer.write(bytearray([1, 2, 3, 4, 5]))
        self.writer.close()
        with open('data_files/txt_5_bytes', "rb") as file_handle:
            self.assertEqual(file_handle.read(1), '\x01')
            self.assertEqual(file_handle.read(1), '\x02')
            self.assertEqual(file_handle.read(1), '\x03')
            self.assertEqual(file_handle.read(1), '\x04')
            self.assertEqual(file_handle.read(1), '\x05')
            self.assertEqual(file_handle.read(1), '')
        self.reader = FileDataReader('data_files/txt_5_bytes')
        stream = self.reader.read(5)
        self.assertEqual(len(stream), 5)
        self.assertEqual(stream[0], 1)
        self.assertEqual(stream[1], 2)
        self.assertEqual(stream[2], 3)
        self.assertEqual(stream[3], 4)
        self.assertEqual(stream[4], 5)

    def test_read_from_empty_file(self):
        self.writer = FileDataWriter('data_files/txt_empty')
        self.writer.write(bytearray())
        self.writer.close()
        with open('data_files/txt_empty', "rb") as file_handle:
            self.assertEqual(file_handle.read(1), '')
        self.reader = FileDataReader('data_files/txt_empty')
        stream = self.reader.read(1)
        self.assertEqual(len(stream), 0)

    def test_read_truncate(self):
        self.writer = FileDataWriter(
            'data_files/txt_one_byte_from_multiple_bytes')
        self.writer.write(bytearray([0xF0, 0xA4, 0xAD, 0xA2]))
        self.writer.close()
        with open('data_files/txt_one_byte_from_multiple_bytes', "rb") \
                as file_handle:
            self.assertEqual(file_handle.read(1), '\xf0')
            self.assertEqual(file_handle.read(1), '\xA4')
            self.assertEqual(file_handle.read(1), '\xAD')
            self.assertEqual(file_handle.read(1), '\xA2')
            self.assertEqual(file_handle.read(1), '')
        self.reader = FileDataReader(
            'data_files/txt_one_byte_from_multiple_bytes')
        stream = self.reader.read(2)
        self.assertEqual(len(stream), 2)
        self.assertEqual(stream[0], 240)
        self.assertEqual(stream[1], 164)


if __name__ == '__main__':
    unittest.main()
