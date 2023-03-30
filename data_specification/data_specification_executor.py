# Copyright (c) 2014 The University of Manchester
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import struct
import functools
import numpy
import math
from spinn_utilities.log import FormatAdapter
from .data_specification_executor_functions import (
    DataSpecificationExecutorFunctions)
from .constants import (
    APPDATA_MAGIC_NUM, DSE_VERSION, END_SPEC_EXECUTOR, BYTES_PER_WORD,
    MAX_MEM_REGIONS, APP_PTR_TABLE_BYTE_SIZE, APP_PTR_TABLE_HEADER_BYTE_SIZE)
from .enums import Commands
from .exceptions import DataSpecificationException
from .memory_region_real import MemoryRegionReal

logger = FormatAdapter(logging.getLogger(__name__))
_ONE_WORD = struct.Struct("<I")


class DataSpecificationExecutor(object):
    """
    Used to execute a SpiNNaker data specification language file to
    produce a memory image.
    """

    __slots__ = [
        # The object to read the specification language file
        "_spec_reader",

        # The executer functions
        "dsef",

        # The pointer table (Empty until executed)
        "__pointer_table"
    ]

    TABLE_TYPE = numpy.dtype(
        [("pointer", "<u4"), ("checksum", "<u4"), ("n_words", "<u4")])

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

        #: The pointer table (Empty until executed)
        self.__pointer_table = numpy.zeros(
            MAX_MEM_REGIONS, dtype=self.TABLE_TYPE)

    def __operation_func(self, cmd, index):
        """
        Decode the command and select an implementation of the command.
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
                f"Invalid command 0x{cmd:X} while reading "
                f"file {self._spec_reader.filename}") from e

    def execute(self):
        """
        Executes the specification.
        This will result in a configuration of memory regions being created
        (but not actually uploaded to SpiNNaker).

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

        # Make the checksums
        for i, region in self.mem_regions:
            if isinstance(region, MemoryRegionReal):
                data = numpy.array(region.region_data, dtype="uint8")
                if data.size % BYTES_PER_WORD != 0:
                    data = numpy.concatenate((
                        data, numpy.zeros(
                            BYTES_PER_WORD - (data.size % BYTES_PER_WORD))))
                self.__pointer_table[i]["n_words"] = int(
                    math.ceil(region.max_write_pointer / BYTES_PER_WORD))
                self.__pointer_table[i]["checksum"] = int(numpy.sum(
                    data.view("uint32"))) & 0xFFFFFFFF
            else:
                self.__pointer_table[i]["n_words"] = 0
                self.__pointer_table[i]["checksum"] = 0

    def get_region(self, region_id):
        """
        Get a region with a given ID.

        :param int region_id: The ID of the region to get
        :return: The region, or `None` if the region was not allocated
        :rtype: MemoryRegionReal or None
        """
        return self.dsef.mem_regions[region_id]

    @property
    def mem_regions(self):
        """
        An enumeration of the mapping from region ID to region holder.

        :rtype: iterable(tuple(int, AbstractMemoryRegion or None))
        """
        return enumerate(self.dsef.mem_regions)

    def get_header(self):
        """
        Get the header of the data as a numpy array.

        :rtype: numpy.ndarray
        """
        return numpy.array([APPDATA_MAGIC_NUM, DSE_VERSION], dtype="<u4")

    def get_pointer_table(self, start_address):
        """
        Get the pointer table as a numpy array.

        :param int start_address: The base address of the data to be written
        :rtype: numpy.ndarray
        """
        pointer_table_size = MAX_MEM_REGIONS * self.TABLE_TYPE.itemsize
        next_free_offset = pointer_table_size + APP_PTR_TABLE_HEADER_BYTE_SIZE

        # Fill in the last bit of the pointer table
        for i, region in self.mem_regions:
            if isinstance(region, MemoryRegionReal):
                data = numpy.array(region.region_data, dtype="uint8")
                if data.size % BYTES_PER_WORD != 0:
                    data = numpy.concatenate((
                        data, numpy.zeros(
                            BYTES_PER_WORD - (data.size % BYTES_PER_WORD))))
                self.__pointer_table[i]["pointer"] = (
                    next_free_offset + start_address)
                next_free_offset += region.allocated_size
            else:
                self.__pointer_table[i]["pointer"] = 0
        return self.__pointer_table

    @property
    def referenceable_regions(self):
        """
        The regions that can be referenced by others.

        :rtype: list(int)
        """
        return self.dsef.referenceable_regions

    @property
    def references_to_fill(self):
        """
        The references that need to be filled.

        :rtype: list(int)
        """
        return self.dsef.references_to_fill

    def get_constructed_data_size(self):
        """
        Return the size of the data that will be written to memory.

        :return: size of the data that will be written to memory
        :rtype: int
        """
        return APP_PTR_TABLE_BYTE_SIZE + sum(
            region.allocated_size
            for _, region in self.mem_regions
            if isinstance(region, MemoryRegionReal))
