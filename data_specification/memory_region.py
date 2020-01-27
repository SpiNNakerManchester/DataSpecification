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


class MemoryRegion(object):
    """ Memory region storage object.
    """

    __slots__ = [
        "_unfilled",
        "_allocated_size",
        "_region_data",
        "_write_pointer",
        "_max_write_pointer"
    ]

    def __init__(self, unfilled, size):
        """
        :param bool unfilled: if the region should not be written to by the
            data specification (i.e., because the vertex uses it as a working
            data region or an output region)
        :param int size: the size of the region, in bytes
        """
        #: flag that states if the region is filled or not
        self._unfilled = unfilled
        #: the amount of memory allocated to this DSG
        self._allocated_size = size
        #: the region buffer, or None for unfilled regions
        self._region_data = None if unfilled else bytearray(size)
        #: the position in the memory where the writing is currently occurring
        self._write_pointer = 0
        #: the max point where if written over, it will cause an error
        self._max_write_pointer = 0

    @property
    def allocated_size(self):
        """ The size of the region.

        :rtype: int
        """
        return self._allocated_size

    @property
    def remaining_space(self):
        """ The space between the current write pointer and the end of the\
            region, which is the number of bytes remaining in the region that\
            can be written.

        :rtype: int
        """
        return self._allocated_size - self._write_pointer

    @property
    def unfilled(self):
        """ Whether the region is marked as not fillable; unfilled regions\
            will not contain any data at write time.

        :rtype: bool
        """
        return self._unfilled

    @property
    def region_data(self):
        """ The buffer which holds the data written in this region.

        :rtype: bytearray
        """
        return (
            bytearray(self._allocated_size) if self._unfilled
            else self._region_data)

    @property
    def write_pointer(self):
        """ The position in the buffer where data will be written to next.

        :rtype: int
        """
        return self._write_pointer

    @write_pointer.setter
    def write_pointer(self, write_pointer):
        self._write_pointer = write_pointer
        self._max_write_pointer = max((
            self._write_pointer, self._max_write_pointer))

    @property
    def max_write_pointer(self):
        """ The max point where if written over, it will cause an error.

        :rtype: int
        """
        return self._max_write_pointer

    def increment_write_pointer(self, n_bytes):
        """ Advance the write pointer.

        :param int n_bytes: The number of bytes to advance the pointer by.
        """
        self._write_pointer += n_bytes
        self._max_write_pointer = max((
            self._write_pointer, self._max_write_pointer))
