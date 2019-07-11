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

import struct
from .constants import (
    END_SPEC_EXECUTOR, LEN2, LEN3, MAX_MEM_REGIONS, MAX_REGISTERS)
from .exceptions import (
    DataSpecificationSyntaxError, ExecuteBreakInstruction, NoMoreException,
    NoRegionSelectedException, ParameterOutOfBoundsException,
    RegionInUseException, RegionNotAllocatedException,
    RegionUnfilledException, UnknownTypeLengthException)
from .abstract_executor_functions import AbstractExecutorFunctions
from .memory_region import MemoryRegion
from .memory_region_collection import MemoryRegionCollection

_ONE_BYTE = struct.Struct("<B")
_ONE_SHORT = struct.Struct("<H")
_ONE_WORD = struct.Struct("<I")
_ONE_LONG = struct.Struct("<Q")
_ONE_SIGNED_INT = struct.Struct("<i")


class DataSpecificationExecutorFunctions(AbstractExecutorFunctions):
    """ This class includes the function related to each of the commands\
        of the data specification file.
    """

    __slots__ = [
        # Where we are reading the data spec from
        "spec_reader",
        # How much space do we have available? Maximum *PER REGION*
        "memory_space",
        # How much space has been allocated
        "space_allocated",
        # What is the current region that we're writing to
        "current_region",
        # The model registers, a list of 16 ints
        "registers",
        # The collection of memory regions that can be written to
        "mem_regions",

        # Decodings of the current command
        "cmd_size",
        "opcode",
        "dest_reg",
        "src1_reg",
        "src2_reg",
        "data_len"]

    def __init__(self, spec_reader, memory_space):
        """
        :param spec_reader: \
            The object to read the specification language file from
        :type spec_reader:\
            :py:class:`~spinn_storage_handlers.abstract_classes.AbstractDataReader`
        :param memory_space: \
            Memory space available for the data to be generated
        :type memory_space: int
        """
        self.spec_reader = spec_reader
        self.memory_space = memory_space

        self.space_allocated = 0
        self.current_region = None

        self.registers = [0] * MAX_REGISTERS
        self.mem_regions = MemoryRegionCollection(MAX_MEM_REGIONS)

        # storage objects
        self.cmd_size = None
        self.opcode = None
        self.dest_reg = None
        self.src1_reg = None
        self.src2_reg = None
        self.data_len = None

    def __unpack_cmd(self, cmd):
        """ Routine to unpack the command read from the data spec file. The\
            parameters of the command are stored in the class data.

        :param cmd: The command read form the data spec file
        :type cmd: int
        :return: No value returned
        :rtype: None
        """
        self.cmd_size = (cmd >> 28) & 0x3
        self.opcode = (cmd >> 20) & 0xFF
        use_dest_reg = (cmd >> 18) & 0x1 == 0x1
        use_src1_reg = (cmd >> 17) & 0x1 == 0x1
        use_src2_reg = (cmd >> 16) & 0x1 == 0x1
        self.dest_reg = (cmd >> 12) & 0xF if use_dest_reg else None
        self.src1_reg = (cmd >> 8) & 0xF if use_src1_reg else None
        self.src2_reg = (cmd >> 4) & 0xF if use_src2_reg else None
        self.data_len = (cmd >> 12) & 0x3

    @property
    def _region(self):
        if self.current_region is None:
            return None
        return self.mem_regions[self.current_region]

    def execute_break(self, cmd):
        """ This command raises an exception to stop the execution of the \
            data spec executor (DSE)

        :param cmd: the command which triggered the function call
        :type cmd: int
        :return: No value returned
        :rtype: None
        :raise data_specification.exceptions.ExecuteBreakInstruction:\
            Raises the exception to break the execution of the DSE
        """
        raise ExecuteBreakInstruction(
            self.spec_reader.tell(), self.spec_reader.filename)

    def execute_reserve(self, cmd):
        """ This command reserves a region and assigns some memory space to it

        :param cmd: the command which triggered the function call
        :type cmd: int
        :return: No value returned
        :rtype: None
        :raise data_specification.exceptions.DataSpecificationSyntaxError:\
            If there is an error in the command syntax
        :raise data_specification.exceptions.ParameterOutOfBoundsException: \
            If the requested size of the region is beyond the available\
            memory space
        """
        self.__unpack_cmd(cmd)
        region = cmd & 0x1F  # cmd[4:0]

        if self.cmd_size != LEN2:
            raise DataSpecificationSyntaxError(
                "Command {0:s} requires one word as argument (total 2 words), "
                "but the current encoding ({1:X}) is specified to be {2:d} "
                "words long".format(
                    "RESERVE", cmd, self.cmd_size))

        unfilled = (cmd >> 7) & 0x1 == 0x1

        if not self.mem_regions.is_empty(region):
            raise RegionInUseException(region)

        size = _ONE_WORD.unpack(self.spec_reader.read(4))[0]
        if size & 0x3 != 0:
            size = (size + 4) - (size & 0x3)

        if not (0 < size <= self.memory_space):
            raise ParameterOutOfBoundsException(
                "region size", size, 1, self.memory_space, "RESERVE")

        self.mem_regions[region] = MemoryRegion(
            unfilled=unfilled, size=size)
        self.space_allocated += size

    def execute_write(self, cmd):
        """ This command writes the given value in the specified region a\
            number of times as identified by either a value in the command or\
            a register value

        :param cmd: the command which triggered the function call
        :type cmd: int
        :return: No value returned
        :rtype: None
        :raise data_specification.exceptions.DataSpecificationSyntaxError:\
            If there is an error in the command syntax
        """
        self.__unpack_cmd(cmd)

        if self.src2_reg is not None:
            n_repeats = self.registers[self.src2_reg]
        else:
            n_repeats = cmd & 0xFF

        # Convert data length to bytes
        data_len = 1 << self.data_len

        if self.src1_reg is not None:
            value = self.registers[self.src1_reg]
        elif self.cmd_size == LEN2 and data_len != 8:
            value = _ONE_WORD.unpack(self.spec_reader.read(4))[0]
        elif self.cmd_size == LEN3 and data_len == 8:
            value = _ONE_LONG.unpack(self.spec_reader.read(8))[0]
        else:
            raise DataSpecificationSyntaxError(
                "Command {0:s} requires a value as an argument, but the "
                "current encoding ({1:X}) is specified to be {2:d} words "
                "long and the data length command argument is specified "
                "to be {3:d} bytes long".format(
                    "WRITE", cmd, self.cmd_size, data_len))

        # Perform the writes
        self._write_to_mem(value, data_len, n_repeats, "WRITE")

    def execute_write_array(self, cmd):  # @UnusedVariable
        """ This command writes an array of values in the specified region

        :param cmd: the command which triggered the function call
        :type cmd: int
        :return: No value returned
        :rtype: None
        """
        length = _ONE_WORD.unpack(self.spec_reader.read(4))[0]
        value_encoded = self.spec_reader.read(4 * length)
        self._write_bytes_to_mem(value_encoded, "WRITE_ARRAY")

    def execute_switch_focus(self, cmd):
        """ This command switches the focus to the desired, already allocated,\
            memory region

        :param cmd: the command which triggered the function call
        :type cmd: int
        :return: No value returned
        :rtype: None
        :raise data_specification.exceptions.RegionUnfilledException: \
            If the focus is being switched to a region of memory which has\
            been declared to be kept unfilled
        """
        self.__unpack_cmd(cmd)

        if self.src1_reg is not None:
            region = self.registers[self.src1_reg]
        else:
            region = (cmd >> 8) & 0xF

        if self.mem_regions.is_empty(region):
            raise RegionUnfilledException(region, "SWITCH_FOCUS")
        self.current_region = region

    def execute_mv(self, cmd):
        """ This command moves an immediate value to a register or copies the \
            value of a register to another register

        :param cmd: the command which triggered the function call
        :type cmd: int
        :return: No value returned
        :rtype: None
        :raise data_specification.exceptions.DataSpecificationSyntaxError: \
            If the destination register is not correctly specified; the\
            destination must be a register and the appropriate bit needs to\
            be set in the specification
        """
        self.__unpack_cmd(cmd)
        if self.dest_reg is None:
            raise DataSpecificationSyntaxError(
                "Destination register not correctly specified")

        if self.src1_reg is not None:
            self.registers[self.dest_reg] = self.registers[self.src1_reg]
        else:
            self.registers[self.dest_reg] = \
                _ONE_WORD.unpack(self.spec_reader.read(4))[0]

    def execute_set_wr_ptr(self, cmd):
        self.__unpack_cmd(cmd)
        if self.src1_reg is not None:
            # the data is a register
            future_address = self.registers[self.src1_reg]
        else:
            # the data is a raw address
            future_address = _ONE_WORD.unpack(self.spec_reader.read(4))[0]

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

    def execute_end_spec(self, cmd):  # @UnusedVariable
        """ Return the value which terminates the data spec executor

        :param cmd: the command which triggered the function call
        :type cmd: int
        :return: END_SPEC_EXECUTOR
        :rtype: int
        :raise data_specification.exceptions.DataSpecificationSyntaxError:\
            If command END_SPEC != -1
        """
        value = _ONE_SIGNED_INT.unpack(self.spec_reader.read(4))[0]
        if value != -1:
            raise DataSpecificationSyntaxError(
                "Command END_SPEC requires an argument equal to -1. The "
                "current argument value is {0}".format(value))
        return END_SPEC_EXECUTOR

    def _write_to_mem(self, value, n_bytes, repeat, command):
        """ Write the specified value to data memory the specified amount of\
            times.

            The selected memory region needs to be already allocated

        :param value: the value to be written in the data memory region
        :type value: int
        :param n_bytes: number of bytes that represent the value
        :type n_bytes: int
        :param repeat: the number of times the value is to be repeated
        :type repeat: int
        :param command: the command which is being executed
        :type command: str
        :return: No value returned
        :rtype: None
        :raise data_specification.exceptions.NoRegionSelectedException: \
            if there is no memory region selected for the write operation
        :raise data_specification.exceptions.RegionNotAllocatedException: \
            if the selected region has not been allocated memory space
        :raise data_specification.exceptions.NoMoreException:\
            if the selected region has not enough available memory to \
            store the required data
        :raise data_specification.exceptions.UnknownTypeLengthException: \
            if the data type size is not 1, 2, 4, or 8 bytes
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
        """ Write raw bytes to data memory

            The selected memory region needs to be already allocated

        :param data: the value to be written in the data memory region
        :type data: str
        :param command: the command which is being executed
        :type command: str
        :return: No value returned
        :rtype: None
        :raise data_specification.exceptions.NoRegionSelectedException: \
            if there is no memory region selected for the write operation
        :raise data_specification.exceptions.RegionNotAllocatedException: \
            if the selected region has not been allocated memory space
        :raise data_specification.exceptions.NoMoreException:\
            if the selected region has not enough available memory to \
            store the required data
        """
        # A region must've been selected
        if self.current_region is None:
            raise NoRegionSelectedException(command)

        # It must be a real region
        if self._region is None:
            raise RegionNotAllocatedException(self.current_region, command)

        self.__write_blob(data)

    def __write_blob(self, data):
        """ Does the actual write to the region, enforcing that writes cannot\
            go outside the region.

        :param data: The data to write
        :type data: str
        :raise data_specification.exceptions.NoMoreException:\
            if the selected region has not enough space to store the data
        """
        # It must have enough space
        region = self._region
        if region.remaining_space < len(data):
            raise NoMoreException(
                region.remaining_space, len(data), self.current_region)

        # We can safely write
        write_ptr = region.write_pointer
        region.region_data[write_ptr:write_ptr + len(data)] = data
        region.increment_write_pointer(len(data))
