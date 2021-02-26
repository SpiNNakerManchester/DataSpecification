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

import logging
import struct
import functools
import numpy
from spinn_utilities.log import FormatAdapter
from .data_specification_executor_functions import (
    DataSpecificationExecutorFunctions)
from .constants import (
    APPDATA_MAGIC_NUM, DSE_VERSION, END_SPEC_EXECUTOR,
    MAX_MEM_REGIONS, APP_PTR_TABLE_BYTE_SIZE, APP_PTR_TABLE_HEADER_BYTE_SIZE)
from .enums import Commands
from .exceptions import DataSpecificationException

logger = FormatAdapter(logging.getLogger(__name__))
_ONE_WORD = struct.Struct("<I")


class DataSpecificationExecutor(object):
    """ Used to execute a SpiNNaker data specification language file to\
        produce a memory image.
    """

    __slots__ = [
        # The object to read the specification language file
        "_spec_reader",

        # The executer functions
        "dsef"
    ]

    def __init__(self, spec_reader, memory_space):
        """
        :param ~io.RawIOBase spec_reader:
            The object to read the specification language file from
        :param int memory_space:
            memory available on the destination architecture
        :raise IOError: If a read or write fails
        """
        #: The object to read the specification to execute.
        self._spec_reader = spec_reader
        #: The executor functions themselves.
        self.dsef = DataSpecificationExecutorFunctions(
            self._spec_reader, memory_space)
        # TODO: make the dsef field a private detail of the executor
        # Currently accessed directly from FEC to get memory regions...

    def __operation_func(self, cmd, index):
        """ Decode the command and select an implementation of the command.
        """
        try:
            opcode = (cmd >> 20) & 0xFF
            # noinspection PyArgumentList
            # pylint: disable=no-value-for-parameter
            return functools.partial(Commands(opcode).exec_function, self.dsef)
        except (ValueError, TypeError) as e:
            logger.debug("problem decoding opcode %d at index %d",
                         cmd, index, exc_info=True)
            raise DataSpecificationException(
                "Invalid command 0x{0:X} while reading file {1:s}".format(
                    cmd, self._spec_reader.filename)) from e

    def execute(self):
        """ Executes the specification. This will result in a configuration \
            of memory regions being done.

        :raise IOError: If a read or write fails
        :raise DataSpecificationException:
            If there is an error when executing the specification
        :raise TablePointerOutOfMemoryException:
            If the table pointer generated as data header exceeds the size of
            the available memory
        """
        index = 0
        instruction_spec = self._spec_reader.read(4)
        while instruction_spec:
            # process the received command
            cmd = _ONE_WORD.unpack(instruction_spec)[0]
            operation_fn = self.__operation_func(cmd, index)
            if operation_fn(cmd) == END_SPEC_EXECUTOR:
                break
            instruction_spec = self._spec_reader.read(4)
            index += 4

    def get_region(self, region_id):
        """ Get a region with a given ID.

        :param int region_id: The ID of the region to get
        :return: The region, or None if the region was not allocated
        :rtype: MemoryRegion or None
        """
        return self.dsef.mem_regions[region_id]

    @property
    def mem_regions(self):
        """ An enumeration of the mapping from region ID to region holder.

        :rtype: iterable(tuple(int, MemoryRegion or None))
        """
        return enumerate(self.dsef.mem_regions)

    def get_header(self):
        """ Get the header of the data as a numpy array.

        :rtype: numpy.ndarray
        """
        return numpy.array([APPDATA_MAGIC_NUM, DSE_VERSION], dtype="<u4")

    def get_pointer_table(self, start_address):
        """ Get the pointer table as a numpy array.

        :param int start_address: The base address of the data to be written
        :rtype: numpy.ndarray
        """
        pointer_table = numpy.zeros(MAX_MEM_REGIONS, dtype="<u4")
        pointer_table_size = MAX_MEM_REGIONS * 4
        next_free_offset = pointer_table_size + APP_PTR_TABLE_HEADER_BYTE_SIZE

        for i, region in self.mem_regions:
            if region is not None:
                pointer_table[i] = next_free_offset + start_address
                next_free_offset += region.allocated_size
            else:
                pointer_table[i] = 0
        return pointer_table

    def get_constructed_data_size(self):
        """ Return the size of the data that will be written to memory.

        :return: size of the data that will be written to memory
        :rtype: int
        """
        return APP_PTR_TABLE_BYTE_SIZE + sum(
            region.allocated_size
            for _, region in self.mem_regions if region is not None)
