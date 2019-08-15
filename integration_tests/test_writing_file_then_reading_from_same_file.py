# Copyright (c) 2017-2019 The University of Manchester
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import unittest
import inspect
import os.path
from spinn_storage_handlers import FileDataReader, FileDataWriter


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.reader = None
        self.writer = None
        self._dir = os.path.dirname(inspect.getfile(self.__class__))

    def _file(self, filename):
        return os.path.join(self._dir, "data_files", filename)

    def tearDown(self):
        if self.reader is not None:
            self.reader.close()
            self.reader = None

    def test_one_byte(self):
        myfile = self._file('txt_one_byte')
        self.writer = FileDataWriter(myfile)
        self.writer.write(bytearray([1]))
        self.writer.close()
        with open(myfile, "rb") as f:
            self.assertEqual(f.read(1), b'\x01')
            self.assertEqual(f.read(1), b'')
        self.reader = FileDataReader(myfile)
        stream = self.reader.read(1)
        self.assertEqual(stream, b'\x01')

    def test_readinto_one_byte(self):
        myfile = self._file('txt_one_byte')
        self.writer = FileDataWriter(myfile)
        self.writer.write(bytearray([5]))
        self.writer.close()
        with open(myfile, "rb") as f:
            self.assertEqual(f.read(1), b'\x05')
            self.assertEqual(f.read(1), b'')
        self.reader = FileDataReader(myfile)
        ba = bytearray(1)
        self.reader.readinto(ba)
        self.assertEqual(len(ba), 1)
        self.assertEqual(ba[0], 5)

    def test_read_five_bytes(self):
        myfile = self._file('txt_5_bytes')
        self.writer = FileDataWriter(myfile)
        self.writer.write(bytearray([1, 2, 3, 4, 5]))
        self.writer.close()
        with open(myfile, "rb") as f:
            self.assertEqual(f.read(1), b'\x01')
            self.assertEqual(f.read(1), b'\x02')
            self.assertEqual(f.read(1), b'\x03')
            self.assertEqual(f.read(1), b'\x04')
            self.assertEqual(f.read(1), b'\x05')
            self.assertEqual(f.read(1), b'')
        self.reader = FileDataReader(myfile)
        stream = self.reader.read(5)
        self.assertEqual(len(stream), 5)
        self.assertEqual(stream, b'\x01\x02\x03\x04\x05')

    def test_read_from_empty_file(self):
        myfile = self._file('txt_empty')
        self.writer = FileDataWriter(myfile)
        self.writer.write(bytearray())
        self.writer.close()
        with open(myfile, "rb") as f:
            self.assertEqual(f.read(1), b'')
        self.reader = FileDataReader(myfile)
        stream = self.reader.read(1)
        self.assertEqual(len(stream), 0)

    def test_read_truncate(self):
        myfile = self._file('txt_one_byte_from_multiple_bytes')
        self.writer = FileDataWriter(myfile)
        self.writer.write(bytearray([0xF0, 0xA4, 0xAD, 0xA2]))
        self.writer.close()
        with open(myfile, "rb") as f:
            self.assertEqual(f.read(1), b'\xf0')
            self.assertEqual(f.read(1), b'\xA4')
            self.assertEqual(f.read(1), b'\xAD')
            self.assertEqual(f.read(1), b'\xA2')
            self.assertEqual(f.read(1), b'')
        self.reader = FileDataReader(myfile)
        stream = self.reader.read(2)
        self.assertEqual(len(stream), 2)
        self.assertEqual(stream, b'\xf0\xa4')


if __name__ == '__main__':
    unittest.main()
