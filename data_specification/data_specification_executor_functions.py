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

import io
import struct
from spinn_utilities.overrides import overrides
from .constants import (
    END_SPEC_EXECUTOR, LEN2, LEN3, MAX_MEM_REGIONS, MAX_REGISTERS)
from .exceptions import (
    DataSpecificationSyntaxError, ExecuteBreakInstruction, NoMoreException,
    NoRegionSelectedException, ParameterOutOfBoundsException,
    RegionInUseException, RegionNotAllocatedException,
    RegionUnfilledException, UnknownTypeLengthException)
from data_specification.spi import AbstractExecutorFunctions
from .memory_region_real import MemoryRegionReal
from .memory_region_reference import MemoryRegionReference
from .memory_region_collection import MemoryRegionCollection

_ONE_BYTE = struct.Struct("<B")
_ONE_SHORT = struct.Struct("<H")
_ONE_WORD = struct.Struct("<I")
_TWO_WORDS = struct.Struct("<II")
_ONE_LONG = struct.Struct("<Q")
_ONE_SIGNED_INT = struct.Struct("<i")


class DataSpecificationExecutorFunctions(AbstractExecutorFunctions):
    """
    This class includes the function related to each of the commands
    of the data specification file.

    .. note::
        DSG operations not mentioned in this class will cause an error during
        DSE if used.
    """

    __slots__ = [
        "_spec_reader",
        "_memory_space",
        "_space_allocated",
        "_current_region",
        "_registers",
        "_mem_regions",
        "_referenceable_regions",
        "_references_to_fill",

        # Decodings of the current command
        "__cmd_size",
        "__dest_reg",
        "__src1_reg",
        "__src2_reg",
        "__data_len"]

    def __init__(self, spec_reader, memory_space):
        """
        :param ~io.RawIOBase spec_reader:
            The object to read the specification language file from
        :param int memory_space:
            Memory space available for the data to be generated *per region*
        """
        #: Where we are reading the data spec from
        self._spec_reader = spec_reader
        #: How much space do we have available? Maximum *PER REGION*
        self._memory_space = memory_space

        #: How much space has been allocated
        self._space_allocated = 0
        #: What is the current region that we're writing to
        self._current_region = None

        #: The model registers, a list of 16 ints
        self._registers = [0] * MAX_REGISTERS
        #: The collection of memory regions that can be written to
        self._mem_regions = MemoryRegionCollection(MAX_MEM_REGIONS)
        #: The indices of regions that are marked as referenceable
        self._referenceable_regions = []
        #: The indices of regions that are references of others
        self._references_to_fill = []

        #: Decoded from command: size in words
        self.__cmd_size = None
        #: Decoded from command: destination register or None
        self.__dest_reg = None
        #: Decoded from command: first source register or None
        self.__src1_reg = None
        #: Decoded from command: second source register or None
        self.__src2_reg = None
        #: Decoded from command: data length
        self.__data_len = None

    @property
    def mem_regions(self):
        """
        The collection of memory regions that can be written to.

        :rtype: MemoryRegionCollection
        """
        return self._mem_regions

    def __unpack_cmd(self, cmd):
        """
        Routine to unpack the command read from the data spec file.
        The parameters of the command are stored in the class data.

        :param int cmd: The command read form the data spec file
        """
        self.__cmd_size = (cmd >> 28) & 0x3
        use_dest_reg = (cmd >> 18) & 0x1 == 0x1
        use_src1_reg = (cmd >> 17) & 0x1 == 0x1
        use_src2_reg = (cmd >> 16) & 0x1 == 0x1
        self.__dest_reg = (cmd >> 12) & 0xF if use_dest_reg else None
        self.__src1_reg = (cmd >> 8) & 0xF if use_src1_reg else None
        self.__src2_reg = (cmd >> 4) & 0xF if use_src2_reg else None
        self.__data_len = (cmd >> 12) & 0x3

    @property
    def _region(self):
        if self._current_region is None:
            return None
        return self._mem_regions[self._current_region]

    @overrides(AbstractExecutorFunctions.execute_break)
    def execute_break(self, cmd):
        """
        :raise ExecuteBreakInstruction:
            Raises the exception to break the execution of the DSE
        """
        if isinstance(self._spec_reader, io.FileIO):
            name = self._spec_reader.name
        else:
            name = "<stream>"
        raise ExecuteBreakInstruction(self._spec_reader.tell(), name)

    @overrides(AbstractExecutorFunctions.execute_reserve)
    def execute_reserve(self, cmd):
        """
        :raise ParameterOutOfBoundsException:
            If the requested size of the region is beyond the available
            memory space
        """
        self.__unpack_cmd(cmd)
        region = cmd & 0x1F  # cmd[4:0]

        unfilled = (cmd >> 7) & 0x1 == 0x1
        referenceable = (cmd >> 6) & 0x1 == 0x1

        if not referenceable and self.__cmd_size != LEN2:
            raise DataSpecificationSyntaxError(
                "Command RESERVE requires one word as argument (total 2 "
                f"words), but the current encoding ({cmd:X}) is specified to "
                f"be {self.__cmd_size:d} words long")
        if referenceable and self.__cmd_size != LEN3:
            raise DataSpecificationSyntaxError(
                "Command RESERVE requires two words as arguments (total 3 "
                f"words), but the current encoding ({cmd:X}) is specified to "
                f"be {self.__cmd_size:d} words long")

        if not self._mem_regions.is_empty(region):
            raise RegionInUseException(region)

        if not referenceable:
            size = _ONE_WORD.unpack(self._spec_reader.read(4))[0]
            reference = None
        else:
            size, reference = _TWO_WORDS.unpack(self._spec_reader.read(8))
        if size & 0x3 != 0:
            size = (size + 4) - (size & 0x3)

        if not (0 < size <= self._memory_space):
            raise ParameterOutOfBoundsException(
                "region size", size, 1, self._memory_space, "RESERVE")

        self._mem_regions[region] = MemoryRegionReal(
            unfilled=unfilled, size=size, reference=reference)
        if referenceable:
            self._referenceable_regions.append(region)
        self._space_allocated += size

    @overrides(AbstractExecutorFunctions.execute_reference)
    def execute_reference(self, cmd):
        """
        :raise ParameterOutOfBoundsException:
            If the requested size of the region is beyond the available
            memory space
        """
        self.__unpack_cmd(cmd)
        region = cmd & 0x1F  # cmd[4:0]

        if self.__cmd_size != LEN2:
            raise DataSpecificationSyntaxError(
                "Command REFERENCE requires one word as argument (total 2 "
                f"words), but the current encoding ({cmd:X}) is specified to "
                f"be {self.__cmd_size:d} words long")

        if not self._mem_regions.is_empty(region):
            raise RegionInUseException(region)

        ref = _ONE_WORD.unpack(self._spec_reader.read(4))[0]
        self._mem_regions[region] = MemoryRegionReference(ref)
        self._references_to_fill.append(region)

    @overrides(AbstractExecutorFunctions.execute_write)
    def execute_write(self, cmd):
        """
        :raise NoRegionSelectedException:
            If there is no memory region selected for the write operation
        :raise RegionNotAllocatedException:
            If the selected region has not been allocated memory space
        :raise NoMoreException:
            If the selected region has not enough available memory to store
            the required data
        :raise UnknownTypeLengthException:
            If the data type size is not 1, 2, 4, or 8 bytes
        """
        self.__unpack_cmd(cmd)

        if self.__src2_reg is not None:
            n_repeats = self._registers[self.__src2_reg]
        else:
            n_repeats = cmd & 0xFF

        # Convert data length to bytes
        data_len = 1 << self.__data_len

        if self.__src1_reg is not None:
            value = self._registers[self.__src1_reg]
        elif self.__cmd_size == LEN2 and data_len != 8:
            value = _ONE_WORD.unpack(self._spec_reader.read(4))[0]
        elif self.__cmd_size == LEN3 and data_len == 8:
            value = _ONE_LONG.unpack(self._spec_reader.read(8))[0]
        else:
            raise DataSpecificationSyntaxError(
                "Command WRITE requires a value as an argument, but the "
                f"current encoding ({cmd:X}) is specified to be "
                f"{self.__cmd_size:d} words long and the data length command "
                f"argument is specified to be {data_len:d} bytes long")

        # Perform the writes
        self._write_to_mem(value, data_len, n_repeats, "WRITE")

    @overrides(AbstractExecutorFunctions.execute_write_array)
    def execute_write_array(self, cmd):  # @UnusedVariable
        """
        :raise NoRegionSelectedException:
            If there is no memory region selected for the write operation
        :raise RegionNotAllocatedException:
            If the selected region has not been allocated memory space
        :raise NoMoreException:
            If the selected region has not enough available memory to store
            the required data
        """
        length = _ONE_WORD.unpack(self._spec_reader.read(4))[0]
        value_encoded = self._spec_reader.read(4 * length)
        self._write_bytes_to_mem(value_encoded, "WRITE_ARRAY")

    @overrides(AbstractExecutorFunctions.execute_switch_focus)
    def execute_switch_focus(self, cmd):
        """
        :raise RegionUnfilledException:
            If the focus is being switched to a region of memory which has
            been declared to be kept unfilled
        """
        self.__unpack_cmd(cmd)

        if self.__src1_reg is not None:
            region = self._registers[self.__src1_reg]
        else:
            region = (cmd >> 8) & 0x1F

        if self._mem_regions.is_empty(region):
            raise RegionUnfilledException(region, "SWITCH_FOCUS")
        self._current_region = region

    @overrides(AbstractExecutorFunctions.execute_mv)
    def execute_mv(self, cmd):
        self.__unpack_cmd(cmd)
        if self.__dest_reg is None:
            raise DataSpecificationSyntaxError(
                "Destination register not correctly specified")

        if self.__src1_reg is not None:
            self._registers[self.__dest_reg] = self._registers[self.__src1_reg]
        else:
            self._registers[self.__dest_reg] = \
                _ONE_WORD.unpack(self._spec_reader.read(4))[0]

    @overrides(AbstractExecutorFunctions.execute_set_wr_ptr)
    def execute_set_wr_ptr(self, cmd):
        """
        :raise NoRegionSelectedException:
            If there is no memory region selected for the set-ptr operation
        """
        self.__unpack_cmd(cmd)
        if self.__src1_reg is not None:
            # the data is a register
            future_address = self._registers[self.__src1_reg]
        else:
            # the data is a raw address
            future_address = _ONE_WORD.unpack(self._spec_reader.read(4))[0]

        # check that the address is relative or absolute
        if cmd & 0x1 == 1:
            # relative to its current write pointer
            if self._region is None:
                raise NoRegionSelectedException(
                    "the write pointer for this region is currently undefined")

            # relative to the base address of the region (obsolete)
            # noinspection PyTypeChecker
            address = self._region.write_pointer + future_address
        else:
            address = future_address

        # update write pointer
        self._region.write_pointer = address

    @overrides(AbstractExecutorFunctions.execute_end_spec)
    def execute_end_spec(self, cmd):  # @UnusedVariable
        value = _ONE_SIGNED_INT.unpack(self._spec_reader.read(4))[0]
        if value != -1:
            raise DataSpecificationSyntaxError(
                "Command END_SPEC requires an argument equal to -1. The "
                f"current argument value is {value}")
        return END_SPEC_EXECUTOR

    def _write_to_mem(self, value, n_bytes, repeat, command):
        """
        Write the specified value to data memory the specified amount of
        times.

        The selected memory region needs to be already allocated.

        :param int value: the value to be written in the data memory region
        :param int n_bytes: number of bytes that represent the value
        :param int repeat: the number of times the value is to be repeated
        :param str command: the command which is being executed
        :raise NoRegionSelectedException:
            If there is no memory region selected for the write operation
        :raise RegionNotAllocatedException:
            If the selected region has not been allocated memory space
        :raise NoMoreException:
            f the selected region has not enough available memory to
            store the required data
        :raise UnknownTypeLengthException:
            If the data type size is not 1, 2, 4, or 8 bytes
        """
        if n_bytes == 1:
            encoder = _ONE_BYTE
        elif n_bytes == 2:
            encoder = _ONE_SHORT
        elif n_bytes == 4:
            encoder = _ONE_WORD
        elif n_bytes == 8:
            encoder = _ONE_LONG
        else:
            raise UnknownTypeLengthException(n_bytes, command)
        self._write_bytes_to_mem(encoder.pack(value) * repeat, command)

    def _write_bytes_to_mem(self, data, command):
        """
        Write raw bytes to data memory.

        The selected memory region needs to be already allocated.

        :param data: the value to be written in the data memory region
        :type data: bytes or bytearray
        :param str command: the command which is being executed
        :raise NoRegionSelectedException:
            If there is no memory region selected for the write operation
        :raise RegionNotAllocatedException:
            If the selected region has not been allocated memory space
        :raise NoMoreException:
            If the selected region has not enough available memory to store
            the required data
        """
        # A region must've been selected
        if self._current_region is None:
            raise NoRegionSelectedException(command)

        # It must be a real region
        if self._region is None:
            raise RegionNotAllocatedException(self._current_region, command)

        self.__write_blob(data)

    def __write_blob(self, data):
        """
        Does the actual write to the region, enforcing that writes cannot
        go outside the region.

        :param data: The data to write
        :type data: bytes or bytearray
        :raise NoMoreException:
            if the selected region has not enough space to store the data
        """
        # It must have enough space
        region = self._region
        if region.remaining_space < len(data):
            raise NoMoreException(
                region.remaining_space, len(data), self._current_region)

        # We can safely write
        write_ptr = region.write_pointer
        region.region_data[write_ptr:write_ptr + len(data)] = data
        region.increment_write_pointer(len(data))

    @property
    def referenceable_regions(self):
        """
        The regions that can be referenced by others.

        :rtype: list(int)
        """
        return self._referenceable_regions

    @property
    def references_to_fill(self):
        """
        The references that need to be filled.

        :rtype: list(int)
        """
        return self._references_to_fill
