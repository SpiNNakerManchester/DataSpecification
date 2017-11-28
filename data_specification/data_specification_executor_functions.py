import struct

from .memory_region import MemoryRegion
from .memory_region_collection import MemoryRegionCollection
from .abstract_executor_functions import AbstractExecutorFunctions
from .constants \
    import MAX_REGISTERS, MAX_MEM_REGIONS, LEN2, LEN3, END_SPEC_EXECUTOR
from .exceptions \
    import ExecuteBreakInstruction, DataSpecificationSyntaxError, \
    DataSpecificationNoMoreException, DataSpecificationRegionNotAllocated, \
    DataSpecificationNoRegionSelectedException, \
    DataSpecificationUnknownTypeLengthException, \
    DataSpecificationRegionUnfilledException, \
    DataSpecificationParameterOutOfBoundsException, \
    DataSpecificationRegionInUseException

_ONE_BYTE = struct.Struct("<B")
_ONE_SHORT = struct.Struct("<H")
_ONE_WORD = struct.Struct("<I")
_ONE_LONG = struct.Struct("<Q")
_ONE_SIGNED_INT = struct.Struct("<i")


def _unpack(self, cmd):
    """ Routine to unpack the command read from the data spec file.

    :param cmd: The command read form the data spec file
    :type cmd: int
    :return: (cmdsize, dest_reg, src1_reg, src2_reg, data_len)
    :rtype: tuple
    """
    cmdsize = (cmd >> 28) & 0x3
    use_dest_reg = (cmd >> 18) & 0x1 == 0x1
    use_src1_reg = (cmd >> 17) & 0x1 == 0x1
    use_src2_reg = (cmd >> 16) & 0x1 == 0x1
    dest_reg = (cmd >> 12) & 0xF if use_dest_reg else None
    src1_reg = (cmd >> 8) & 0xF if use_src1_reg else None
    src2_reg = (cmd >> 4) & 0xF if use_src2_reg else None
    data_len = (cmd >> 12) & 0x3
    return (cmdsize, dest_reg, src1_reg, src2_reg, data_len)


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
        "mem_regions"
    ]

    def __init__(self, spec_reader, memory_space):
        """

        :param spec_reader: The object to read the specification language file\
            from
        :type spec_reader:\
            :py:class:`data_specification.abstract_data_reader.\
            AbstractDataReader`
        :param memory_space: Memory space available for the data to be\
            generated
        :type memory_space: int
        """
        self.spec_reader = spec_reader
        self.memory_space = memory_space

        self.space_allocated = 0
        self.current_region = None

        self.registers = [0] * MAX_REGISTERS
        self.mem_regions = MemoryRegionCollection(MAX_MEM_REGIONS)

    def execute_break(self, cmd):
        """
        This command raises an exception to stop the execution of the data \
            spec executor (DSE)

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
        """
        This command reserves a region and assigns some memory space to it

        :param cmd: the command which triggered the function call
        :type cmd: int
        :return: No value returned
        :rtype: None
        :raise data_specification.exceptions.DataSpecificationSyntaxError:\
            If there is an error in the command syntax
        :raise data_specification.exceptions.\
            DataSpecificationParameterOutOfBoundsException: If the requested \
            size of the region is beyond the available memory space
        """
        cmd_size, _dest_reg, _src1_reg, _src2_reg, _data_len = _unpack(cmd)
        region = cmd & 0x1F  # cmd[4:0]

        if cmd_size != LEN2:
            raise DataSpecificationSyntaxError(
                "Command {0:s} requires one word as argument (total 2 words), "
                "but the current encoding ({1:X}) is specified to be {2:d} "
                "words long".format(
                    "RESERVE", cmd, cmd_size))

        unfilled = (cmd >> 7) & 0x1 == 0x1

        if not self.mem_regions.is_empty(region):
            raise DataSpecificationRegionInUseException(region)

        size = _ONE_WORD.unpack(self.spec_reader.read(4))[0]
        if size & 0x3 != 0:
            size = (size + 4) - (size & 0x3)

        if not (0 < size <= self.memory_space):
            raise DataSpecificationParameterOutOfBoundsException(
                "region size", size, 1, self.memory_space, "RESERVE")

        self.mem_regions[region] = MemoryRegion(
            memory_pointer=0, unfilled=unfilled, size=size)
        self.space_allocated += size

    def execute_write(self, cmd):
        """
        This command writes the given value in the specified region a number\
         of times as identified by either a value in the command or a register\
         value

        :param cmd: the command which triggered the function call
        :type cmd: int
        :return: No value returned
        :rtype: None
        :raise data_specification.exceptions.DataSpecificationSyntaxError:\
            If there is an error in the command syntax
        """
        _cmd_size, _dest_reg, src1_reg, src2_reg, data_len = _unpack(cmd)

        if src2_reg is not None:
            n_repeats = self.registers[src2_reg]
        else:
            n_repeats = cmd & 0xFF

        # Convert data length to bytes
        data_len = 1 << data_len

        if src1_reg is not None:
            value = self.registers[src1_reg]
        elif self._cmd_size == LEN2 and data_len != 8:
            value = _ONE_WORD.unpack(self.spec_reader.read(4))[0]
        elif self._cmd_size == LEN3 and data_len == 8:
            value = _ONE_LONG.unpack(self.spec_reader.read(8))[0]
        else:
            raise DataSpecificationSyntaxError(
                "Command {0:s} requires a value as an argument, but the "
                "current encoding ({1:X}) is specified to be {2:d} words "
                "long and the data length command argument is specified "
                "to be {3:d} bytes long".format(
                    "WRITE", cmd, self._cmd_size, data_len))

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
        :raise data_specification.exceptions.\
            DataSpecificationRegionUnfilledException: If the focus is being \
            switched to a region of memory which has been declared to be kept \
            unfilled
        """
        _cmd_size, _dest_reg, src1_reg, _src2_reg, _data_len = _unpack(cmd)

        if src1_reg is not None:
            region = self.registers[src1_reg]
        else:
            region = (cmd >> 8) & 0xF

        if self.mem_regions.is_empty(region):
            raise DataSpecificationRegionUnfilledException(
                region, "SWITCH_FOCUS")
        self.current_region = region

    def execute_mv(self, cmd):
        """ This command moves an immediate value to a register or copies the \
            value of a register to another register

        :param cmd: the command which triggered the function call
        :type cmd: int
        :return: No value returned
        :rtype: None
        :raise data_specification.exceptions.DataSpecificationSyntaxError: \
                if the destination register is not correctly specified - the \
                destination must be a register and the appropriate bit needs \
                to be set in the specification
        """
        _cmd_size, dest_reg, src1_reg, _src2_reg, _data_len = _unpack(cmd)

        if dest_reg is None:
            raise DataSpecificationSyntaxError(
                "Destination register not correctly specified")

        if src1_reg is not None:
            self.registers[dest_reg] = self.registers[src1_reg]
        else:
            self.registers[dest_reg] = \
                _ONE_WORD.unpack(self.spec_reader.read(4))[0]

    def execute_set_wr_ptr(self, cmd):
        _cmd_size, _dest_reg, src1_reg, _src2_reg, _data_len = _unpack(cmd)
        if src1_reg is not None:
            # the data is a register
            future_address = self.registers[src1_reg]
        else:
            # the data is a raw address
            future_address = _ONE_WORD.unpack(self.spec_reader.read(4))[0]

        # check that the address is relative or absolute
        if cmd & 0x1 == 1:
            # relative to its current write pointer
            if self.mem_regions[self.current_region] is None:
                raise DataSpecificationNoRegionSelectedException(
                    "the write pointer for this region is currently undefined")

            # relative to the base address of the region (obsolete)
            # noinspection PyTypeChecker
            address = (
                self.mem_regions[self.current_region].write_pointer +
                future_address)
        else:
            address = future_address

        # update write pointer
        self.mem_regions[self.current_region].write_pointer = address

    def execute_end_spec(self, cmd):  # @UnusedVariable
        """ Return the value which terminates the data spec executor

        :param cmd: the command which triggered the function call
        :type cmd: int
        :return: constants.END_SPEC_EXECUTOR
        :rtype: int
        :raise data_specification.exceptions.DataSpecificationSyntaxError:\
            If command END_SPEC != -1
        """
        value = _ONE_SIGNED_INT.unpack(self.spec_reader.read(4))[0]
        if value != -1:
            raise DataSpecificationSyntaxError(
                "Command END_SPEC requires an argument equal to -1. The "
                "current argument value is {0:d}".format(value))
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
        :raise data_specification.exceptions.\
            DataSpecificationNoRegionSelectedException: raised if there is no \
            memory region selected for the write operation
        :raise data_specification.exceptions.\
            DataSpecificationRegionNotAllocated: raised if the selected region\
            has not been allocated memory space
        :raise data_specification.exceptions.DataSpecificationNoMoreException:\
            raised if the selected region has not enough available memory to \
            store the required data
        :raise data_specification.exceptions.\
            DataSpecificationUnknownTypeLengthException: raised if the data \
            type size is not 1, 2, 4, or 8 bytes
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
            raise DataSpecificationUnknownTypeLengthException(
                n_bytes, command)
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
        :raise data_specification.exceptions.\
            DataSpecificationNoRegionSelectedException: raised if there is no \
            memory region selected for the write operation
        :raise data_specification.exceptions.\
            DataSpecificationRegionNotAllocated: raised if the selected region\
            has not been allocated memory space
        :raise data_specification.exceptions.DataSpecificationNoMoreException:\
            raised if the selected region has not enough available memory to \
            store the required data
        """

        if self.current_region is None:
            raise DataSpecificationNoRegionSelectedException(command)
        if self.mem_regions.is_empty(self.current_region) is None:
            raise DataSpecificationRegionNotAllocated(
                self.current_region, command)

        self.__write_blob(data)

    def __write_blob(self, blob):
        """ Does the actual write to the region, enforcing that writes cannot\
        go outside the region.

        :param blob: The data to write
        :type blob: str
        :raise data_specification.exceptions.DataSpecificationNoMoreException:\
            if the selected region has not enough space to store the data
        """
        length = len(blob)
        region = self.mem_regions[self.current_region]
        if region.available_space < length:
            raise DataSpecificationNoMoreException(
                region.available_space, length, self.current_region)
        write_ptr = region.write_pointer
        # noinspection PyTypeChecker
        region.region_data[write_ptr:write_ptr + length] = blob
        region.increment_write_pointer(length)
