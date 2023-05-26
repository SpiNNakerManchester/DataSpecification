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

from enum import Enum, IntEnum
import io
import logging
import struct
import numpy
from spinn_utilities.log import FormatAdapter
from spinn_machine import Machine
from .constants import (
    MAX_CONSTRUCTORS, MAX_MEM_REGIONS, MAX_RANDOM_DISTS, MAX_REGISTERS,
    MAX_RNGS, MAX_STRUCT_SLOTS, LEN1, LEN2, LEN3,
    NO_REGS, SRC1_ONLY, BYTES_PER_WORD)
from .exceptions import (
    InvalidSizeException, NotAllocatedException,
    NoRegionSelectedException, ParameterOutOfBoundsException,
    RegionInUseException, RegionUnfilledException, TypeMismatchException,
    UnknownTypeException, UnknownTypeLengthException)
from .enums import (DataType, Commands)

logger = FormatAdapter(logging.getLogger(__name__))
_ONE_SBYTE = struct.Struct("<b")
_ONE_WORD = struct.Struct("<I")
_ONE_SIGNED_INT = struct.Struct("<i")
_TWO_WORDS = struct.Struct("<II")


def _bounds(cmd, name, value, low, high):
    """
    A simple bounds checker.
    """
    if value < low or value >= high:
        raise ParameterOutOfBoundsException(
            name, value, low, high - 1, cmd.name)


def _typebounds(cmd, name, value, valuetype):
    """
    A simple bounds checker that uses the bounds from a type descriptor.
    """
    if valuetype not in DataType:
        raise UnknownTypeException(valuetype, cmd.name)
    if value < valuetype.min or value > valuetype.max:
        raise ParameterOutOfBoundsException(
            name, value, valuetype.min, valuetype.max, cmd.name)


class _Field(IntEnum):
    """
    Various shifts for fields used with :py:func:`_binencode`.
    """
    LENGTH = 28
    COMMAND = 20
    SIGNED = 19
    USAGE = 16
    DESTINATION = 12
    FUNCTION = 11
    SOURCE_1 = 8
    EMPTY = 7
    REFERENCEABLE = 6
    SOURCE_2 = 4
    IMMEDIATE = 0


def _binencode(command, arguments):
    """
    Encodes commands as binary words.

    :param Commands command: The code of the command being encoded.
    :param  dict(_Field,int) arguments: How to parametrise the command.
    :return: the encoded command
    :rtype: bytearray
    """
    cmd_word = command.value << _Field.COMMAND
    for shift in arguments:
        if shift < 0 or shift > 31:
            raise KeyError()
        val = arguments[shift]
        if isinstance(val, Enum):
            val = val.value
        else:
            val = int(val)
        cmd_word |= val << shift
    return bytearray(_ONE_WORD.pack(cmd_word))


class _MemSlot(object):
    """
    Metadata for a memory region.
    """
    __slots__ = ["label", "size", "empty"]

    def __init__(self, label, size, empty):
        #: Optional label for the region; str or None
        self.label = label
        # round size to a number of words
        if size % BYTES_PER_WORD != 0:
            size = size + (BYTES_PER_WORD - (size % BYTES_PER_WORD))
        #: The size of the region; int
        self.size = size
        #: Whether the region is to be left empty; bool
        self.empty = empty


class DataSpecificationGenerator(object):
    """
    Used to generate a SpiNNaker data specification language file that
    can be executed to produce a memory image.
    """
    # pylint: disable=too-many-arguments

    __slots__ = [
        "_bytes",
        "_closed_bytes",
        "_report_writer",
        "_txt_indent",
        "_instruction_counter",
        "_mem_slots",
        "_function_slots",
        "_struct_slots",
        "_rng",
        "_random_distribution",
        "_conditionals",
        "_current_region",
        "_ongoing_function_definition",
        "_ongoing_loop"
    ]

    def __init__(self, report_writer=None):
        """
        :param report_writer:
            Determines if a text version of the specification is to be
            written and, if so, where. No report is written if this is `None`.
        :type report_writer: ~io.TextIOBase or None
        """
        #: The object to write the specification to (before close)
        self._bytes = bytearray()
        #: The object to hold the data after close is called.
        self._closed_bytes = None
        if report_writer is not None and not isinstance(
                report_writer, io.TextIOBase):
            raise TypeError("report_writer must be a TextIOBase or None")
        #: the writer for the human readable report
        self._report_writer = report_writer
        #: current indentation for the report writer
        self._txt_indent = 0
        #: instruction counter, for the report writer only
        self._instruction_counter = 0
        #: the memory regions; list(
        self._mem_slots = [None] * MAX_MEM_REGIONS
        #: the functions
        self._function_slots = [None] * MAX_CONSTRUCTORS
        #: the structure definitions
        self._struct_slots = [None] * MAX_STRUCT_SLOTS
        #: the random number generators
        self._rng = [None] * MAX_RNGS
        #: the random distributions
        self._random_distribution = [None] * MAX_RANDOM_DISTS
        #: stack of _conditionals, used for 'else' tracking
        self._conditionals = []
        #: the current DSG region we're writing to
        self._current_region = None
        #: whether there is a currently-being-made function definition
        self._ongoing_function_definition = False
        #: whether there is a currently executing loop
        self._ongoing_loop = False

    def comment(self, comment):
        """
        Write a comment to the text version of the specification.

        .. note::
            This is ignored by the binary file.

        :param str comment: The comment to write
        """
        self._write_command_to_files(
            bytearray(), comment, no_instruction_number=True)

    def reserve_memory_region(
            self, region, size, label=None, empty=False, reference=None):
        """
        Insert command to reserve a memory region.

        :param int region: The number of the region to reserve, from 0 to 15
        :param int size: The size to reserve for the region, in bytes
        :param label: An optional label for the region
        :type label: str or None
        :param bool empty: Specifies if the region will be left empty
        :param reference: A globally unique reference for this region
        :type reference: int or None
        :raise RegionInUseException: If the ``region`` was already reserved
        :raise ParameterOutOfBoundsException:
            If the ``region`` requested was out of the allowed range, or the
            ``size`` was too big to fit in SDRAM
        """
        _bounds(Commands.RESERVE, "memory region identifier",
                region, 0, MAX_MEM_REGIONS)
        _bounds(Commands.RESERVE, "memory size",
                size, 1, Machine.DEFAULT_SDRAM_BYTES)
        if self._mem_slots[region] is not None:
            raise RegionInUseException(region, self._mem_slots[region].label)

        self._mem_slots[region] = _MemSlot(label, size, empty)

        cmd_word = _binencode(Commands.RESERVE, {
            _Field.LENGTH: LEN2 if reference is None else LEN3,
            _Field.USAGE: NO_REGS,
            _Field.EMPTY: bool(empty),
            _Field.REFERENCEABLE: reference is not None,
            _Field.IMMEDIATE: region})
        encoded_size = _ONE_WORD.pack(size)
        encoded_ref = b""
        if reference is not None:
            encoded_ref = _ONE_WORD.pack(reference)

        cmd_string = Commands.RESERVE.name
        cmd_string += f" memRegion={region:d} size={size:d}"
        if label is not None:
            cmd_string += f" label='{label}'"
        if empty:
            cmd_string += " UNFILLED"
        if reference is not None:
            cmd_string += f" REF {reference:d}"

        self._write_command_to_files(
            cmd_word + encoded_size + encoded_ref, cmd_string)

    def reference_memory_region(self, region, ref, label=None):
        """
        Insert command to reference another memory region.

        :param int region: The number of the region to reserve, from 0 to 15
        :param int ref: The identifier of the region to reference
        :param label: An optional label for the region
        :type label: str or None
        :raise RegionInUseException: If the ``region`` was already reserved
        :raise ParameterOutOfBoundsException:
            If the ``region`` requested was out of the allowed range, or the
            ``size`` was too big to fit in SDRAM
        """
        _bounds(Commands.REFERENCE, "memory region identifier",
                region, 0, MAX_MEM_REGIONS)
        if self._mem_slots[region] is not None:
            raise RegionInUseException(region, self._mem_slots[region].label)

        self._mem_slots[region] = _MemSlot(label, 0, True)

        cmd_word = _binencode(Commands.REFERENCE, {
            _Field.LENGTH: LEN2,
            _Field.IMMEDIATE: region})
        encoded_args = _ONE_WORD.pack(ref)

        cmd_string = Commands.REFERENCE.name
        cmd_string += f" memRegion={region:d} ref={ref:d}"
        if label is not None:
            cmd_string += f" label='{label}'"

        self._write_command_to_files(cmd_word + encoded_args, cmd_string)

    def _create_cmd(self, data, data_type=DataType.UINT32):
        """
        Creates command to write a value to the current write pointer, causing
        the write pointer to move on by the number of bytes required to
        represent the data type. The data is passed as a parameter to this
        function.

        .. note::
            This does not actually insert the ``WRITE`` command in the spec;
            that is done by :py:meth:`write_cmd`.

        :param data: the data to write.
        :type data: int or float
        :param DataType data_type: the type to convert ``data`` to
        :return: ``cmd_word_list`` (binary data to be added to the binary data
            specification file), and ``cmd_string`` (string describing the
            command to be added to the report for the data specification file)
        :rtype: tuple(bytearray, str)
        :raise ParameterOutOfBoundsException:
            * If ``data_type`` is an integer type, and ``data`` has a
              fractional part
            * If ``data`` would overflow the data type
        :raise UnknownTypeException: If the data type is not known
        :raise InvalidSizeException: If the data size is invalid
        """
        _typebounds(Commands.WRITE, "data", data, data_type)

        data_size = data_type.size
        if data_size == 1:
            cmd_data_len = LEN2
            data_len = 0
        elif data_size == 2:
            cmd_data_len = LEN2
            data_len = 1
        elif data_size == 4:
            cmd_data_len = LEN2
            data_len = 2
        elif data_size == 8:
            cmd_data_len = LEN3
            data_len = 3
        else:
            raise InvalidSizeException(
                data_type.name, data_size, Commands.WRITE.name)

        cmd_string = None
        if self._report_writer is not None:
            cmd_string = Commands.WRITE.name
            cmd_string += f" data={data}"

        repeat_reg_usage = NO_REGS
        cmd_word = _binencode(Commands.WRITE, {
            _Field.LENGTH: cmd_data_len,
            _Field.USAGE: repeat_reg_usage,
            _Field.DESTINATION: data_len,
            _Field.IMMEDIATE: 1})
        # 1 is based on parameters = 0, repeats = 1 and parameters |= repeats

        cmd_word_list = cmd_word + data_type.encode(data)
        if self._report_writer is not None:
            cmd_string += f", dataType={data_type.name}"
        return (cmd_word_list, cmd_string)

    def write_value(self, data, data_type=DataType.UINT32):
        """
        Insert command to write a value (once) to the current write pointer,
        causing the write pointer to move on by the number of bytes required
        to represent the data type. The data is passed as a parameter to this
        function

        .. note::
            This method used to have two extra parameters ``repeats`` and
            ``repeats_is_register``. They have been removed here. If you need
            them, use :meth:`write_repeated_value`

        :param data: the data to write as a float.
        :type data: int or float
        :param DataType data_type: the type to convert ``data`` to
        :raise ParameterOutOfBoundsException:
            * If ``data_type`` is an integer type, and ``data`` has a
              fractional part
            * If ``data`` would overflow the data type
        :raise UnknownTypeException: If the data type is not known
        :raise InvalidSizeException: If the data size is invalid
        :raise NoRegionSelectedException: If no region has been selected
        """
        if self._current_region is None:
            raise NoRegionSelectedException(Commands.WRITE.name)
        cmd_word_list, cmd_string = self._create_cmd(data, data_type)
        self._write_command_to_files(cmd_word_list, cmd_string)

    def write_array(self, array_values, data_type=DataType.UINT32):
        """
        Insert command to write an array, causing the write pointer
        to move on by (data type size * the array size), in bytes.

        :param array_values: An array of words to be written
        :type array_values: list(int) or list(float) or ~numpy.ndarray
        :param DataType data_type: Type of data contained in the array
        :raise NoRegionSelectedException: If no region has been selected
        """
        if data_type.numpy_typename is None:
            raise TypeMismatchException(Commands.WRITE_ARRAY.name)
        if self._current_region is None:
            raise NoRegionSelectedException(Commands.WRITE_ARRAY.name)

        data = numpy.array(array_values, dtype=data_type.numpy_typename)
        size = data.size * data_type.size

        if size % 4 != 0:
            raise UnknownTypeLengthException(size, Commands.WRITE_ARRAY.name)

        cmd_word = _binencode(Commands.WRITE_ARRAY, {
            _Field.LENGTH: LEN2,
            _Field.IMMEDIATE: data_type.size})
        cmd_string = Commands.WRITE_ARRAY.name
        cmd_string += f" {size // 4:d} elements\n"
        cmd_string += str(list(array_values))
        arg_word = _ONE_WORD.pack(size // 4)
        self._write_command_to_files(cmd_word + arg_word, cmd_string)
        self._bytes += data.tostring()

    def switch_write_focus(self, region):
        """
        Insert command to switch the region being written to.

        :param int region: The ID of the region to switch to, between 0 and 15
        :raise ParameterOutOfBoundsException:
            If the region identifier is not valid
        :raise NotAllocatedException: If the region has not been allocated
        :raise RegionUnfilledException:
            If the selected region should not be filled
        """
        _bounds(Commands.SWITCH_FOCUS, "region", region, 0, MAX_MEM_REGIONS)
        if self._mem_slots[region] is None:
            raise NotAllocatedException(
                "region", region, Commands.SWITCH_FOCUS.name)
        if self._mem_slots[region].empty:
            raise RegionUnfilledException(region, Commands.SWITCH_FOCUS.name)

        self._current_region = region

        cmd_string = Commands.SWITCH_FOCUS.name
        cmd_string += f" memRegion = {region:d}"
        # Write command to switch focus:
        cmd_word = _binencode(Commands.SWITCH_FOCUS, {
            _Field.LENGTH: LEN1,
            _Field.USAGE: 0x0,
            _Field.SOURCE_1: region})
        self._write_command_to_files(cmd_word, cmd_string)

    def set_write_pointer(self, address, address_is_register=False,
                          relative_to_current=False):
        """
        Insert command to set the position of the write pointer within the
        current region.

        :param int address:
            * If ``address_is_register`` is True, the ID of the register
              containing the address to move to
            * If ``address_is_register`` is False, the address to move the
              write pointer to
        :param bool address_is_register:
            Indicates if ``address`` is a register ID
        :param bool relative_to_current:
            Indicates if ``address`` (or the value read from that register
            when ``address_is_register`` is True) is to be added to the
            current address, or used as an absolute address from the start
            of the current region
        :raise ParameterOutOfBoundsException:
            If the ``address_is_register`` is True and ``address`` is not a
            valid register ID
        :raise NoRegionSelectedException: If no region has been selected
        """
        if self._current_region is None:
            raise NoRegionSelectedException(Commands.SET_WR_PTR.name)
        relative = bool(relative_to_current)
        relative_string = "RELATIVE" if relative else "ABSOLUTE"

        data_encoded = bytearray()
        cmd_string = Commands.SET_WR_PTR.name
        if address_is_register:
            _bounds(Commands.SET_WR_PTR, "address", address, 0, MAX_REGISTERS)
            cmd_word = _binencode(Commands.SET_WR_PTR, {
                _Field.LENGTH: LEN1,
                _Field.USAGE: SRC1_ONLY,
                _Field.SOURCE_1: address,
                _Field.IMMEDIATE: relative})
            cmd_string += f" reg[{address:d}] {relative_string}"
        else:
            if not relative_to_current:
                _typebounds(Commands.SET_WR_PTR, "address",
                            address, DataType.UINT32)
                data_encoded += _ONE_WORD.pack(address)
            else:
                _typebounds(Commands.SET_WR_PTR, "address",
                            address, DataType.INT32)
                data_encoded += _ONE_SIGNED_INT.pack(address)

            cmd_word = _binencode(Commands.SET_WR_PTR, {
                _Field.LENGTH: LEN2,
                _Field.USAGE: NO_REGS,
                _Field.IMMEDIATE: relative})
            cmd_string += f" {address:d} {relative_string}"

        self._write_command_to_files(cmd_word + data_encoded, cmd_string)

    def end_specification(self, close_writer=True):
        """
        Insert a command to indicate that the specification has finished
        and finish writing.

        :param bool close_writer:
            Indicates whether to close the underlying writer(s)
        """
        self.comment("\nEnd of specification:")

        cmd_word = _binencode(Commands.END_SPEC, {
            _Field.LENGTH: LEN1})
        encoded_parameter = _ONE_SIGNED_INT.pack(-1)
        cmd_string = Commands.END_SPEC.name
        self._write_command_to_files(cmd_word + encoded_parameter, cmd_string)

        if close_writer:
            assert self._bytes is not None
            self._closed_bytes = self._bytes
            self._bytes = None
            if self._report_writer is not None:
                self._report_writer.close()
                self._report_writer = None

    def get_bytes_after_close(self):
        """
        Returns the bytes but only after end_specification(True)

        :return: Bytes written
        :rtype: bytearray
        """
        assert self._closed_bytes is not None
        return self._closed_bytes

    def _write_command_to_files(self, cmd_word_list, cmd_string, indent=False,
                                outdent=False, no_instruction_number=False):
        """
        Writes the binary command to the binary output file and, if the
        user has requested a text output for debug purposes, also write
        the text version to the text file.

        Setting the optional parameter ``indent`` to ``True`` causes subsequent
        commands to be indented by two spaces relative to this one. Similarly,
        setting ``outdent`` to ``True`` reverses this spacing.

        :param bytearray cmd_word_list: list of binary words to be added to
            the binary data specification file
        :param str cmd_string: string describing the command to be added to
            the report for the data specification file
        :param bool indent: if the following lines need to be indented
        :param bool outdent: if the following lines need to be out-dented
        :param bool no_instruction_number: if each report line should include
            also the address of the command in the file
        """
        self._bytes += cmd_word_list

        if self._report_writer is not None:
            if outdent is True:
                self._txt_indent = min(self._txt_indent - 1, 0)
            indent_string = "   " * self._txt_indent
            if no_instruction_number:
                formatted_cmd_string = f"{indent_string}{cmd_string}\n"
            else:
                formatted_cmd_string = (
                    f"{self._instruction_counter:08X}. "
                    f"{indent_string}{cmd_string}\n")
                self._instruction_counter += len(cmd_word_list)
            self._report_writer.write(str(formatted_cmd_string))
            if indent is True:
                self._txt_indent += 1
        return

    @property
    def region_sizes(self):
        """
        A list of sizes of each region that has been reserved.

        .. note::
            The list will include ``0`` for each non-reserved region.

        :rtype: list(int)
        """
        return [0 if slot is None else slot.size for slot in self._mem_slots]
