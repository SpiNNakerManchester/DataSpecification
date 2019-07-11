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
from six import raise_from
from .data_specification_executor_functions import (
    DataSpecificationExecutorFunctions)
from .constants import (
    APPDATA_MAGIC_NUM, DSE_VERSION, END_SPEC_EXECUTOR,
    MAX_MEM_REGIONS, APP_PTR_TABLE_BYTE_SIZE, APP_PTR_TABLE_HEADER_BYTE_SIZE)
from .enums import Commands
from .exceptions import DataSpecificationException

logger = logging.getLogger(__name__)
_ONE_WORD = struct.Struct("<I")


class DataSpecificationExecutor(object):
    """ Used to execute a SpiNNaker data specification language file to\
        produce a memory image
    """

    __slots__ = [
        # The object to read the specification language file
        "spec_reader",

        # The executer functions
        "dsef"
    ]

    def __init__(self, spec_reader, memory_space):
        """
        :param spec_reader: \
            The object to read the specification language file from
        :type spec_reader:\
            :py:class:`~spinn_storage_handlers.abstract_classes.AbstractDataReader`
        :param memory_space: memory available on the destination architecture
        :type memory_space: int
        :raise spinn_storage_handlers.exceptions.DataReadException:\
            If a read from external storage fails
        :raise spinn_storage_handlers.exceptions.DataWriteException:\
            If a write to external storage fails
        """
        self.spec_reader = spec_reader
        self.dsef = DataSpecificationExecutorFunctions(
            self.spec_reader, memory_space)

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
            raise_from(DataSpecificationException(
                "Invalid command 0x{0:X} while reading file {1:s}".format(
                    cmd, self.spec_reader.filename)), e)

    def execute(self):
        """ Executes the specification

        :return: Nothing
        :raise spinn_storage_handlers.exceptions.DataReadException:\
            If a read from external storage fails
        :raise spinn_storage_handlers.exceptions.DataWriteException:\
            If a write to external storage fails
        :raise data_specification.exceptions.DataSpecificationException:\
            If there is an error when executing the specification
        :raise data_specification.exceptions.TablePointerOutOfMemory:\
            If the table pointer generated as data header exceeds the size of\
            the available memory
        """
        index = 0
        instruction_spec = self.spec_reader.read(4)
        while instruction_spec:
            # process the received command
            cmd = _ONE_WORD.unpack(instruction_spec)[0]
            operation_fn = self.__operation_func(cmd, index)
            if operation_fn(cmd) == END_SPEC_EXECUTOR:
                break
            instruction_spec = self.spec_reader.read(4)
            index += 4

    def get_region(self, region_id):
        """ Get a region with a given ID

        :param region_id: The ID of the region to get
        :type region_id: int
        :return: The region, or None if the region was not allocated
        :rtype: :py:class:`MemoryRegion`
        """
        return self.dsef.mem_regions[region_id]

    def get_header(self):
        """ Get the header of the data as a numpy array
        """
        return numpy.array([APPDATA_MAGIC_NUM, DSE_VERSION], dtype="<u4")

    def get_pointer_table(self, start_address):
        """ Get the pointer table as a numpy array

        :param start_address: The base address of the data to be written
        :rtype: numpy.array
        """
        pointer_table = numpy.zeros(MAX_MEM_REGIONS, dtype="<u4")
        pointer_table_size = MAX_MEM_REGIONS * 4
        next_free_offset = pointer_table_size + APP_PTR_TABLE_HEADER_BYTE_SIZE

        for i, region in enumerate(self.dsef.mem_regions):
            if region is not None:
                pointer_table[i] = next_free_offset + start_address
                next_free_offset += region.allocated_size
            else:
                pointer_table[i] = 0
        return pointer_table

    def get_constructed_data_size(self):
        """ Return the size of the data that will be written to memory

        :return: size of the data that will be written to memory
        :rtype: int
        """
        return APP_PTR_TABLE_BYTE_SIZE + sum(
            region.allocated_size
            for region in self.dsef.mem_regions if region is not None)
