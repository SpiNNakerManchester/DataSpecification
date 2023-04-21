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
from spinn_machine import sdram
from .constants import (
    MAX_CONSTRUCTORS, MAX_MEM_REGIONS, MAX_RANDOM_DISTS, MAX_REGISTERS,
    MAX_RNGS, MAX_STRUCT_ELEMENTS, MAX_STRUCT_SLOTS, LEN1, LEN2, LEN3, LEN4,
    NO_REGS, DEST_AND_SRC1, DEST_ONLY, SRC1_ONLY, SRC1_AND_SRC2,
    BYTES_PER_WORD)
from .exceptions import (
    DataUndefinedWriterException, DuplicateParameterException,
    FunctionInUseException, InvalidCommandException,
    InvalidOperationException, InvalidSizeException, NotAllocatedException,
    NoRegionSelectedException, ParameterOutOfBoundsException,
    RandomNumberDistributionInUseException, RegionInUseException,
    RegionUnfilledException, RNGInUseException, StructureInUseException,
    TypeMismatchException, UnknownConditionException, UnknownTypeException,
    UnknownTypeLengthException, WrongParameterNumberException)
from .enums import (
    DataType, RandomNumberGenerator, Commands, Condition, LogicOperation,
    ArithmeticOperation)

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
        "_spec_writer",
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

    def __init__(self, spec_writer, report_writer=None):
        """
        :param ~io.RawIOBase spec_writer:
            The object to write the specification to
        :param report_writer:
            Determines if a text version of the specification is to be
            written and, if so, where. No report is written if this is `None`.
        :type report_writer: ~io.TextIOBase or None
        :raise IOError: If a write to external storage fails
        """
        if not isinstance(spec_writer, io.RawIOBase):
            raise TypeError("spec_writer must be a RawIOBase")
        #: The object to write the specification to
        self._spec_writer = spec_writer
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
        :raise DataUndefinedWriterException:
            If the binary specification file writer has not been initialised
        :raise IOError: If a write to external storage fails
        """
        self._write_command_to_files(
            bytearray(), comment, no_instruction_number=True)

    def define_break(self):
        """
        Insert command to stop execution with an exception (for debugging).

        :raise DataUndefinedWriterException:
            If the binary specification file writer has not been initialised
        :raise IOError: If a write to external storage fails
        """
        cmd_word = _binencode(Commands.BREAK, {
            _Field.LENGTH: LEN1})
        cmd_string = Commands.BREAK.name
        self._write_command_to_files(cmd_word, cmd_string)

    def no_operation(self):
        """
        Insert command to execute nothing.

        :raise DataUndefinedWriterException:
            If the binary specification file writer has not been initialised
        :raise IOError: If a write to external storage fails
        """
        cmd_word = _binencode(Commands.NOP, {
            _Field.LENGTH: LEN1})
        cmd_string = Commands.NOP.name
        self._write_command_to_files(cmd_word, cmd_string)
        return

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
        :raise DataUndefinedWriterException:
            If the binary specification file writer has not been initialised
        :raise IOError: If a write to external storage fails
        :raise RegionInUseException: If the ``region`` was already reserved
        :raise ParameterOutOfBoundsException:
            If the ``region`` requested was out of the allowed range, or the
            ``size`` was too big to fit in SDRAM
        """
        _bounds(Commands.RESERVE, "memory region identifier",
                region, 0, MAX_MEM_REGIONS)
        _bounds(Commands.RESERVE, "memory size",
                size, 1, sdram.SDRAM.max_sdram_found)
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
        :raise DataUndefinedWriterException:
            If the binary specification file writer has not been initialised
        :raise IOError: If a write to external storage fails
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

    def free_memory_region(self, region):
        """
        Insert command to free a previously reserved memory region.

        :param int region: The number of the region to free, from 0 to 15
        :raise DataUndefinedWriterException:
            If the binary specification file writer has not been initialised
        :raise IOError: If a write to external storage fails
        :raise NotAllocatedException: If the region was not reserved
        :raise ParameterOutOfBoundsException:
            If the ``region`` requested was out of the allowed range
        """
        _bounds(Commands.FREE, "memory region identifier",
                region, 0, MAX_MEM_REGIONS)
        if self._mem_slots[region] is None:
            raise NotAllocatedException("region", region, Commands.FREE.name)

        label = self._mem_slots[region].label
        self._mem_slots[region] = None

        cmd_word = _binencode(Commands.FREE, {
            _Field.LENGTH: LEN1,
            _Field.USAGE: NO_REGS,
            _Field.IMMEDIATE: region})
        cmd_string = Commands.FREE.name
        cmd_string += f" memRegion={region:d}"
        if label is not None:
            cmd_string += f" ({label})"
        self._write_command_to_files(cmd_word, cmd_string)

    def declare_random_number_generator(self, rng_id, rng_type, seed):
        """
        Insert command to declare a random number generator.

        :param int rng_id: The ID of the random number generator
        :param RandomNumberGenerator rng_type:
            The type of the random number generator
        :param int seed: The seed of the random number generator >= 0
        :raise DataUndefinedWriterException:
            If the binary specification file writer has not been initialised
        :raise IOError: If a write to external storage fails
        :raise UnknownTypeException:
            If the ``rng_type`` is not one of the allowed values
        :raise ParameterOutOfBoundsException:
            * If the ``seed`` is too big or too small
            * If the ``rng_id`` is not in the allowed range
        :raise RNGInUseException:
            If the random number generator with the given ID has already been
            defined
        """
        _bounds(Commands.DECLARE_RNG, "random number generator ID",
                rng_id, 0, MAX_RNGS)
        if rng_type not in RandomNumberGenerator:
            raise UnknownTypeException(
                rng_type.value, Commands.DECLARE_RNG.name)

        if self._rng[rng_id] is not None:
            raise RNGInUseException(rng_id)
        _typebounds(Commands.DECLARE_RNG, "seed", seed, DataType.UINT32)

        self._rng[rng_id] = [rng_type, seed]

        cmd_word = _binencode(Commands.DECLARE_RNG, {
            _Field.LENGTH: LEN2,
            _Field.DESTINATION: rng_id,
            _Field.SOURCE_1: rng_type})
        encoded_seed = _ONE_WORD.pack(seed)

        cmd_string = Commands.DECLARE_RNG.name
        cmd_string += (
            f" ID={rng_id:d}, source={rng_type.value:d}, seed={seed:d}")
        self._write_command_to_files(cmd_word + encoded_seed, cmd_string)

    def declare_uniform_random_distribution(
            self, distribution_id, structure_id, rng_id, min_value, max_value):
        """
        Insert commands to declare a uniform random distribution.

        :param int distribution_id: ID of the distribution being set up
        :param int structure_id: ID of an empty structure slot to fill with
            the uniform random distribution data
        :param int rng_id:
            The ID of the random number generator, between 0 and 15
        :param float min_value: The minimum value that should be returned from
            the distribution between -32768.0 and max_value
        :param float max_value: The maximum value that should be returned from
            the distribution between min_value and 32767.9999847
        :raise DataUndefinedWriterException:
            If the binary specification file writer has not been initialised
        :raise IOError: If a write to external storage fails
        :raise NoMoreException:
            If there is no more space for a new random distribution
        :raise NotAllocatedException:
            If the requested ``rng_id`` has not been allocated
        :raise ParameterOutOfBoundsException:
            If ``rng_id``, ``structure_id``, ``min_value`` or ``max_value`` is
            out of range
        :raise StructureInUseException:
            If structure ``structure_id`` is already defined
        """
        _bounds(Commands.DECLARE_RANDOM_DIST, "distribution ID",
                distribution_id, 0, MAX_RANDOM_DISTS)
        _bounds(Commands.DECLARE_RANDOM_DIST, "rng ID",
                rng_id, 0, MAX_RNGS)
        _typebounds(Commands.DECLARE_RANDOM_DIST, "min_value",
                    min_value, DataType.S1615)
        _typebounds(Commands.DECLARE_RANDOM_DIST, "max_value",
                    max_value, DataType.S1615)
        _bounds(Commands.DECLARE_RANDOM_DIST, "structure ID",
                structure_id, 0, MAX_STRUCT_SLOTS)

        if self._rng[rng_id] is None:
            raise NotAllocatedException(
                "RNG", rng_id, Commands.DECLARE_RANDOM_DIST.name)
        if self._random_distribution[distribution_id] is not None:
            raise RandomNumberDistributionInUseException(distribution_id)

        parameters = [("distType", DataType.UINT32, 0),
                      ("rngID", DataType.UINT32, rng_id),
                      ("param1", DataType.S1615, min_value),
                      ("param2", DataType.S1615, max_value)]

        self._random_distribution[distribution_id] = parameters
        self.define_structure(structure_id, parameters)

        cmd_word = _binencode(Commands.DECLARE_RANDOM_DIST, {
            _Field.LENGTH: LEN1,
            _Field.SOURCE_1: distribution_id,
            _Field.IMMEDIATE: structure_id})

        cmd_string = Commands.DECLARE_RANDOM_DIST.name
        cmd_string += (
            f" distribution_id={distribution_id:d}"
            f" structure_id={structure_id:d}")
        self._write_command_to_files(cmd_word, cmd_string)

    def call_random_distribution(self, distribution_id, register_id):
        """
        Insert command to get the next random number from a random
        distribution, placing the result in a register to be used in a
        future call.

        :param int distribution_id:
            The ID of the random distribution to call between 0 and 63
        :param int register_id:
            The ID of the register to store the result in between 0 and 15
        :raise DataUndefinedWriterException:
            If the binary specification file writer has not been initialised
        :raise IOError: If a write to external storage fails
        :raise NotAllocatedException:
            If the random distribution ID was not previously declared
        :raise ParameterOutOfBoundsException:
            If the ``distribution_id`` or ``register_id`` specified was out
            of range
        """
        _bounds(Commands.GET_RANDOM_NUMBER, "register_id",
                register_id, 0, MAX_REGISTERS)
        _bounds(Commands.GET_RANDOM_NUMBER, "distribution_id",
                distribution_id, 0, MAX_RANDOM_DISTS)
        if self._random_distribution[distribution_id] is None:
            raise NotAllocatedException(
                "random number distribution", distribution_id,
                Commands.GET_RANDOM_NUMBER.name)

        cmd_word = _binencode(Commands.GET_RANDOM_NUMBER, {
            _Field.LENGTH: LEN1,
            _Field.USAGE: 0x4,
            _Field.DESTINATION: register_id,
            _Field.IMMEDIATE: distribution_id})
        cmd_string = Commands.GET_RANDOM_NUMBER.name
        cmd_string += (
            f" distribution={distribution_id:d} dest=reg[{register_id:d}]")
        self._write_command_to_files(cmd_word, cmd_string)

    def define_structure(self, structure_id, parameters):
        """
        Insert commands to define a data structure.

        :param int structure_id:
            the ID of the structure to create, between 0 and 15
        :param parameters: A list of between 1 and 255 tuples of
            `(label, data_type, value)` where:

            * `label` is the label of the element (for debugging)
            * `data_type` is the data type of the element
            * `value` is the value of the element, or `None` if no value is to
               be assigned
        :type parameters: list(tuple(str, DataType, float))
        :raise DataUndefinedWriterException:
            If the binary specification file writer has not been initialised
        :raise IOError: If a write to external storage fails
        :raise NoMoreException:
            If there are no more spaces for new structures
        :raise ParameterOutOfBoundsException:
            * If there are an incorrect number of parameters
            * If the size of one of the tuples is incorrect
            * If one of the values to be assigned has an integer ``data_type``
              but has a fractional part
            * If one of the values to be assigned would overflow its
              ``data_type``
        :raise UnknownTypeException:
            If one of the data types in the structure is unknown
        """
        # start of struct
        _bounds(Commands.START_STRUCT, "structure ID",
                structure_id, 0, MAX_STRUCT_SLOTS)
        _bounds(Commands.START_STRUCT, "structure elements",
                len(parameters), 1, MAX_STRUCT_ELEMENTS)
        if self._struct_slots[structure_id] is not None:
            raise StructureInUseException(structure_id)

        self._struct_slots[structure_id] = parameters
        cmd_word = _binencode(Commands.START_STRUCT, {
            _Field.LENGTH: LEN1,
            _Field.IMMEDIATE: structure_id})
        cmd_string = Commands.START_STRUCT.name
        cmd_string += f" ID={structure_id:d}"
        self._write_command_to_files(cmd_word, cmd_string)

        # elements of the struct
        for elem_index, i in enumerate(parameters):
            label, data_type, value = i
            if data_type not in DataType:
                raise UnknownTypeException(
                    data_type.value, Commands.WRITE_PARAM.name)

            cmd_string = Commands.WRITE_PARAM.name
            cmd_string += (
                f" element_id={elem_index:d}, element_type={data_type.name}")
            if value is not None:
                _typebounds(Commands.WRITE_PARAM, "value", value, data_type)
                if data_type.size <= 4:
                    cmd_word = _binencode(Commands.STRUCT_ELEM, {
                        _Field.LENGTH: LEN2,
                        _Field.IMMEDIATE: data_type})
                elif data_type.size == 8:
                    cmd_word = _binencode(Commands.STRUCT_ELEM, {
                        _Field.LENGTH: LEN3,
                        _Field.IMMEDIATE: data_type})
                else:
                    raise InvalidSizeException(
                        data_type.name, data_type.size,
                        Commands.STRUCT_ELEM.name)

                value_bytes = data_type.encode(value)
                if len(label) == 0:
                    cmd_string += f", value={value:d}"
                else:
                    cmd_string += f", value={value:f}, label={label}"
                self._write_command_to_files(
                    cmd_word + value_bytes, cmd_string)
            else:
                cmd_word = _binencode(Commands.STRUCT_ELEM, {
                    _Field.LENGTH: LEN1,
                    _Field.IMMEDIATE: data_type})
                if len(label):
                    cmd_string += f", label={label}"
                self._write_command_to_files(cmd_word, cmd_string)

        # end of struct
        cmd_word = _binencode(Commands.END_STRUCT, {
            _Field.LENGTH: LEN1})
        cmd_string = Commands.END_STRUCT.name
        cmd_string += f" ID={structure_id:d}"
        self._write_command_to_files(cmd_word, cmd_string)

    def get_structure_value(
            self, destination_id, structure_id, parameter_index,
            parameter_index_is_register=False):
        """
        Insert command to get a value from a structure.
        The value is copied in a register.

        :param int destination_id: The ID of the destination register
        :param int structure_id: The ID of the source structure
        :param int parameter_index: The ID of the parameter/element to copy
        :param bool parameter_index_is_register:
            True if ``parameter_index`` is a register ID containing the ID of
            the parameter/element to copy
        :raise DataUndefinedWriterException:
            If the binary specification file writer has not been initialised
        :raise IOError: If a write to external storage fails
        :raise ParameterOutOfBoundsException:
            * If ``structure_id`` is not in the allowed range
            * If ``parameter_index`` is larger than the number of parameters
              declared in the original structure
            * If ``destination_id`` is not the ID of a valid register
            * If ``parameter_index_is_register`` is True and
              ``parameter_index`` is not a valid register ID
        :raise NotAllocatedException:
            If the structure requested has not been declared
        """
        _bounds(Commands.READ_PARAM, "structure_id",
                structure_id, 0, MAX_STRUCT_SLOTS)
        _bounds(Commands.READ_PARAM, "destination_id",
                destination_id, 0, MAX_REGISTERS)
        if self._struct_slots[structure_id] is None:
            raise NotAllocatedException(
                "structure", structure_id, Commands.READ_PARAM.name)

        cmd_string = Commands.READ_PARAM.name
        cmd_string += f" structure_id={structure_id:d}, "

        if parameter_index_is_register is True:
            _bounds(Commands.READ_PARAM, "parameter_index",
                    parameter_index, 0, MAX_REGISTERS)
            cmd_word = _binencode(Commands.READ_PARAM, {
                _Field.LENGTH: LEN1,
                _Field.USAGE: DEST_AND_SRC1,
                _Field.DESTINATION: destination_id,
                _Field.SOURCE_1: parameter_index,
                _Field.IMMEDIATE: structure_id})
            cmd_string += (
                f"element_id_from_register={parameter_index:d}, "
                f"destination_register={destination_id:d}")
        else:
            _bounds(Commands.READ_PARAM, "parameter_index",
                    parameter_index, 0, MAX_STRUCT_ELEMENTS)
            if len(self._struct_slots[structure_id]) <= parameter_index:
                raise NotAllocatedException(
                    f"structure {structure_id:d} parameter",
                    parameter_index, Commands.READ_PARAM.name)
            cmd_word = _binencode(Commands.READ_PARAM, {
                _Field.LENGTH: LEN1,
                _Field.USAGE: DEST_ONLY,
                _Field.DESTINATION: destination_id,
                _Field.SOURCE_2: parameter_index,
                _Field.IMMEDIATE: structure_id})
            cmd_string += (
                f"element_id={parameter_index:d}, "
                f"destination_register={destination_id:d}")

        self._write_command_to_files(cmd_word, cmd_string)

    def set_structure_value(self, structure_id, parameter_index, value,
                            data_type, value_is_register=False):
        """
        Insert command to set a value in a structure.

        :param int structure_id:
            * If called outside of a function, the ID of the structure,
              between 0 and 15
            * If called within a function, the ID of the structure
              argument, between 0 and 4
        :param int parameter_index: The index of the value to assign in the
            structure, between 0 and the number of parameters declared in the
            structure
        :param float value:
            * If ``value_is_register`` is False, the value to assign at the
              selected position as a float or int
            * If ``value_is_register`` is True, the ID of the register
              containing the value to assign to the position, between 0 and 15
        :param DataType data_type: type of the data to be stored in the
            structure. If parameter ``value_is_register`` is set to true,
            this variable is disregarded
        :param bool value_is_register:
            Identifies if value identifies a register
        :raise DataUndefinedWriterException:
            If the binary specification file writer has not been initialised
        :raise IOError: If a write to external storage fails
        :raise ParameterOutOfBoundsException:
            * If ``structure_id`` is not in the allowed range
            * If ``parameter_index`` is larger than the number of parameters
              declared in the original structure
            * If ``value_is_register`` is False, and the data type of the
              structure value is an integer, and ``value`` has a fractional
              part
            * If ``value_is_register`` is False, and ``value`` would overflow
              the position in the structure
            * If ``value_is_register`` is True, and ``value`` is not a valid
              register ID
        :raise NotAllocatedException:
            If the structure requested has not been declared
        :raise UnknownTypeException: If the data type is unknown
        """
        _bounds(Commands.WRITE_PARAM, "structure_id",
                structure_id, 0, MAX_STRUCT_SLOTS)
        _bounds(Commands.WRITE_PARAM, "parameter_index",
                parameter_index, 0, MAX_STRUCT_ELEMENTS)
        if self._struct_slots[structure_id] is None:
            raise NotAllocatedException(
                "structure", structure_id, Commands.WRITE_PARAM.name)
        if len(self._struct_slots[structure_id]) <= parameter_index:
            raise NotAllocatedException(
                f"structure {structure_id} parameter",
                parameter_index, Commands.WRITE_PARAM.name)

        if self._struct_slots[
                structure_id][parameter_index][1] is not data_type:
            raise TypeMismatchException(Commands.WRITE_PARAM.name)

        cmd_string = Commands.WRITE_PARAM.name
        cmd_string += (
            f" structure_id={structure_id:d}, "
            f"element_id={parameter_index:d}, ")

        if value_is_register:
            _bounds(Commands.WRITE_PARAM, "value", value, 0, MAX_REGISTERS)
            cmd_word = _binencode(Commands.WRITE_PARAM, {
                _Field.LENGTH: LEN1,
                _Field.USAGE: SRC1_ONLY,
                _Field.DESTINATION: structure_id,
                _Field.SOURCE_1: value,
                _Field.IMMEDIATE: parameter_index})
            cmd_string += f"value=reg[{value:d}]"
            self._write_command_to_files(cmd_word, cmd_string)
        else:
            _typebounds(Commands.WRITE_PARAM, "value", value, data_type)
            if data_type.size > 4 and data_type.size != 8:
                raise InvalidSizeException(
                    data_type.name, data_type.size, Commands.WRITE_PARAM.name)
            cmd_word = _binencode(Commands.WRITE_PARAM, {
                _Field.LENGTH: LEN2 if data_type.size <= 4 else LEN3,
                _Field.USAGE: NO_REGS,
                _Field.DESTINATION: structure_id,
                _Field.IMMEDIATE: parameter_index})
            value_encoded = data_type.encode(value)
            cmd_string += f"value={value:d}"
            self._write_command_to_files(cmd_word + value_encoded, cmd_string)

    def write_structure(
            self, structure_id, repeats=1, repeats_is_register=False):
        """
        Insert command to write a structure to the current write pointer,
        causing the current write pointer to move on by the number of bytes
        needed to represent the structure.

        :param int structure_id:
            * If called within a function, the ID of the structure to write,
              between 0 and 15
            * If called outside of a function, the ID of the structure
              argument, between 0 and 5
        :param int repeats:
            * If ``repeats_is_register`` is True, the ID of the register
              containing the number of repeats, between 0 and 15
            * If ``repeats_is_register`` is False, the number of repeats to
              write, between 0 and 255
        :param bool repeats_is_register:
            Whether ``repeats`` identifies a register
        :raise DataUndefinedWriterException:
            If the binary specification file writer has not been initialised
        :raise IOError: If a write to external storage fails
        :raise ParameterOutOfBoundsException:
            * If ``structure_id`` is not a valid structure ID
            * If ``repeats_is_register`` is False and ``repeats`` is not in
              range
            * If ``repeats_is_register`` is True and ``repeats`` is not a
              valid register ID
        :raise NoRegionSelectedException: If no region has been selected
        :raise RegionExhaustedException:
            If the selected region has no more space
        """
        _bounds(Commands.WRITE_STRUCT, "structure_id",
                structure_id, 0, MAX_STRUCT_SLOTS)
        if self._struct_slots[structure_id] is None:
            raise NotAllocatedException(
                "structure", structure_id, Commands.WRITE_STRUCT.name)

        cmd_string = Commands.WRITE_STRUCT.name
        cmd_string += f" structure_id={structure_id:d}, "
        if repeats_is_register:
            _bounds(Commands.WRITE_STRUCT, "repeats",
                    repeats, 0, MAX_REGISTERS)
            cmd_word = _binencode(Commands.WRITE_STRUCT, {
                _Field.LENGTH: LEN1,
                _Field.USAGE: SRC1_ONLY,
                _Field.SOURCE_1: repeats,
                _Field.IMMEDIATE: structure_id})
            cmd_string += f"repeats=reg[{repeats:d}]"
        else:
            _bounds(Commands.WRITE_STRUCT, "repeats",
                    repeats, 0, MAX_STRUCT_SLOTS)
            cmd_word = _binencode(Commands.WRITE_STRUCT, {
                _Field.LENGTH: LEN1,
                _Field.SOURCE_1: repeats,
                _Field.IMMEDIATE: structure_id})
            cmd_string += f"repeats={repeats:d}"
        self._write_command_to_files(cmd_word, cmd_string)

    def start_function(self, function_id, argument_by_value):
        """
        Insert command to start a function definition, with up to 5 arguments,
        which are the IDs of structures to be used within the function, each
        of which can be passed by reference or by value. In the commands
        following this command up to the :meth:`end_function` command,
        structures can only be referenced using the numbers 1 to 5 which
        address the arguments, rather than the original structure IDs.

        :param int function_id: The ID of the function currently defined.
        :param list(bool) argument_by_value: A list of up to 5 booleans
            indicating if the structure to be passed as an argument is to be
            passed by reference (i.e., changes made within the function are
            persisted) or by value (i.e., changes made within the function
            are lost when the function exits. The number of arguments is
            determined by the length of this list.
        :raise ParameterOutOfBoundsException:
            If there are too many items in the list of arguments
        :raise InvalidCommandException:
            If there is already a function being defined at this point
        :raise FunctionInUseException: If the function is already defined
        """
        if self._ongoing_function_definition:
            raise InvalidCommandException(Commands.START_CONSTRUCTOR.name)
        _bounds(Commands.START_CONSTRUCTOR, "number of arguments",
                len(argument_by_value), 0, 6)
        _bounds(Commands.START_CONSTRUCTOR, "function_id",
                function_id, 0, MAX_CONSTRUCTORS)
        if self._function_slots[function_id] is not None:
            raise FunctionInUseException(function_id)

        self._function_slots[function_id] = argument_by_value

        cmd_string = Commands.START_CONSTRUCTOR.name
        cmd_string += (
            f" ID={function_id:d} number_of_args={len(argument_by_value):d}")

        self._ongoing_function_definition = True

        read_only_flags = 0
        for i, abv in enumerate(argument_by_value):
            cmd_string += f" arg[{i + 1:d}]="
            if abv:
                read_only_flags |= 1 << i
                cmd_string += "read-only"
            else:
                cmd_string += "read-write"

        cmd_word = _binencode(Commands.START_CONSTRUCTOR, {
            _Field.LENGTH: LEN1,
            _Field.FUNCTION: function_id,
            _Field.SOURCE_1: len(argument_by_value),
            _Field.IMMEDIATE: read_only_flags})
        self._write_command_to_files(cmd_word, cmd_string, indent=True)

    def end_function(self):
        """
        Insert command to mark the end of a function definition.

        :raise InvalidCommandException:
            If there is no function being defined at this point
        """
        if not self._ongoing_function_definition:
            raise InvalidCommandException(Commands.END_CONSTRUCTOR.name)

        self._ongoing_function_definition = False

        cmd_word = _binencode(Commands.END_CONSTRUCTOR, {
            _Field.LENGTH: LEN1})
        cmd_string = Commands.END_CONSTRUCTOR.name
        self._write_command_to_files(cmd_word, cmd_string, outdent=True)

    def call_function(self, function_id, structure_ids):
        """
        Insert command to call a function.

        :param int function_id:
            The ID of a previously defined function, between 0 and 31
        :param structure_ids: A list of structure IDs that will be passed into
            the function, each between 0 and 15
        :type structure_ids: list(int)
        :raise DataUndefinedWriterException:
            If the binary specification file writer has not been initialised
        :raise IOError: If a write to external storage fails
        :raise ParameterOutOfBoundsException:
            * If the function ID is not valid
            * If any of the structure IDs are not valid
        :raise NotAllocatedException:
            * If a function has not been defined with the given ID
            * If no structure has been defined with one of the IDs in
              ``structure_ids``
        :raise WrongParameterNumberException:
            If a function is called with a wrong number of parameters
        :raise DuplicateParameterException:
            If a function is called with duplicate parameters
        """
        _bounds(Commands.CONSTRUCT, "function",
                function_id, 0, MAX_CONSTRUCTORS)
        if self._function_slots[function_id] is None:
            raise NotAllocatedException(
                "function", function_id, Commands.CONSTRUCT.name)
        if len(structure_ids) != len(self._function_slots[function_id]):
            raise WrongParameterNumberException(
                function_id, len(self._function_slots[function_id]),
                structure_ids)
        if len(structure_ids) != len(set(structure_ids)):
            raise DuplicateParameterException(
                f"{Commands.CONSTRUCT.name} {function_id}",
                structure_ids)

        cmd_string = Commands.CONSTRUCT.name
        cmd_string += f" function_id={function_id:d}"

        param_word_encoded = bytearray()
        cmd_word_length = LEN1
        if structure_ids:
            param_word = 0
            for i, struct_id in enumerate(structure_ids):
                _bounds(Commands.CONSTRUCT,
                        f"structure argument {i}",
                        structure_ids[i], 0, MAX_STRUCT_SLOTS)
                if self._struct_slots[struct_id] is None:
                    raise NotAllocatedException(
                        f"structure argument {i}",
                        struct_id, Commands.CONSTRUCT.name)

                param_word |= struct_id << (6 * i)
                cmd_string += f" arg[{i:d}]=struct[{struct_id:d}]"

            cmd_word_length = LEN2
            param_word_encoded += _ONE_WORD.pack(param_word)

        cmd_word = _binencode(Commands.CONSTRUCT, {
            _Field.LENGTH: cmd_word_length,
            _Field.SOURCE_1: function_id})
        self._write_command_to_files(cmd_word + param_word_encoded, cmd_string)

    def read_value(self, dest_id, data_type):
        """
        Insert command to read a value from the current write pointer, causing
        the write pointer to move by the number of bytes read. The data is
        stored in a register passed as argument.

        :param int dest_id: The ID of the destination register.
        :param DataType data_type: The type of the data to be read.
        :raise ParameterOutOfBoundsException:
            If ``dest_id`` is out of range for a register ID
        """
        if data_type not in DataType:
            raise UnknownTypeException(
                data_type.value, Commands.READ.name)
        _bounds(Commands.READ, "register", dest_id, 0, MAX_REGISTERS)

        cmd_word = _binencode(Commands.READ, {
            _Field.LENGTH: LEN1,
            _Field.USAGE: DEST_ONLY,
            _Field.DESTINATION: dest_id,
            _Field.IMMEDIATE: data_type.size})
        cmd_string = Commands.READ.name
        cmd_string += f" {data_type.size:d} bytes in register {dest_id:d}"
        self._write_command_to_files(cmd_word, cmd_string)

    def create_cmd(self, data, data_type=DataType.UINT32):
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
        :raise DataUndefinedWriterException:
            If the binary specification file writer has not been initialised
        :raise IOError: If a write to external storage fails
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
        cmd_word_list, cmd_string = self.create_cmd(data, data_type)
        self._write_command_to_files(cmd_word_list, cmd_string)

    def write_cmd(self, cmd_word_list, cmd_string):
        """
        Applies write commands created previously created (and cached).

        .. note::
            See :meth:`create_cmd` for how to create the arguments to
            this method.

        :param bytearray cmd_word_list: list of binary words to be added to
            the binary data specification file
        :param str cmd_string: string describing the command to be added to
            the report for the data specification file
        :raise IOError: If a write to external storage fails
        :raise NoRegionSelectedException: If no region has been selected
        """
        if self._current_region is None:
            raise NoRegionSelectedException(Commands.WRITE.name)
        self._write_command_to_files(cmd_word_list, cmd_string)

    def write_repeated_value(
            self, data, repeats=1, repeats_is_register=False,
            data_type=DataType.UINT32):
        """
        Insert command to write a value one or more times to the current write
        pointer, causing the write pointer to move on by the number of bytes
        required to represent the data type. The data is passed as a parameter
        to this function

        :param data: the data to write as a float.
        :type data: float or int
        :param int repeats:
            * If ``repeats_is_register`` is False, this parameter identifies
              the number of times to repeat the data, between 1 and 255
              (default 1)
            * If ``repeats_is_register`` is True, this parameter identifies
              the register that contains the number of repeats.
        :param bool repeats_is_register:
            Indicates if the parameter ``repeats`` identifies the register
            containing the number of repeats of the value to write
        :param DataType data_type: the type to convert data to
        :raise DataUndefinedWriterException:
            If the binary specification file writer has not been initialised
        :raise IOError: If a write to external storage fails
        :raise ParameterOutOfBoundsException:
            * If ``repeats_is_register`` is False, and ``repeats`` is out of
              range
            * If ``repeats_is_register`` is True, and ``repeats`` is not a
              valid register ID
            * If ``data_type`` is an integer type, and ``data`` has a
              fractional part
            * If ``data`` would overflow the data type
        :raise UnknownTypeException: If the data type is not known
        :raise InvalidSizeException: If the data size is invalid
        :raise NoRegionSelectedException: If no region has been selected
        """
        if self._current_region is None:
            raise NoRegionSelectedException(Commands.WRITE.name)
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

        if repeats_is_register is False:
            _bounds(Commands.WRITE, "repeats", repeats, 1, 256)
        else:
            _bounds(Commands.WRITE, "repeats", repeats, 0, MAX_REGISTERS)

        parameters = 0
        cmd_string = Commands.WRITE.name
        cmd_string += f" data={data}"

        if repeats_is_register:
            repeat_reg_usage = 1
            parameters |= (repeats << 4)
            cmd_string += f", repeats=reg[{repeats:d}]"
        else:
            repeat_reg_usage = NO_REGS
            parameters |= repeats & 0xFF
            cmd_string += f", repeats={repeats:d}"

        cmd_word = _binencode(Commands.WRITE, {
            _Field.LENGTH: cmd_data_len,
            _Field.USAGE: repeat_reg_usage,
            _Field.DESTINATION: data_len,
            _Field.IMMEDIATE: parameters})
        data_word = data_type.encode(data)
        cmd_string += f", dataType={data_type.name}"
        self._write_command_to_files(cmd_word + data_word, cmd_string)

    def write_value_from_register(
            self, data_register, repeats=1, repeats_is_register=False,
            data_type=DataType.UINT32):
        """
        Insert command to write a value one or more times at the write pointer
        of the current memory region, causing it to move. The data is contained
        in a register whose ID is passed to the function.

        :param int data_register:
            Identifies the register in which the data is stored.
        :param int repeats:
            * If ``repeats_is_register`` is `None`, this parameter identifies
              the number of times to repeat the data, between 1 and 255
              (default 1)
            * If ``repeats_is_register`` is not `None` (i.e. has an integer
              value), the content of this parameter is disregarded
        :param bool repeats_is_register: Identifies if ``repeats`` is the
            register containing the number of repeats of the value to write
        :param DataType data_type: the type of the data held in the register
        :raise DataUndefinedWriterException:
            If the binary specification file writer has not been initialised
        :raise IOError: If a write to external storage fails
        :raise ParameterOutOfBoundsException:
            * If ``repeats_is_register`` is False, and ``repeats`` is out of
              range
            * If ``repeats_is_register`` is True, and ``repeats`` is not a
              valid register ID
            * If ``data_register`` is not a valid register ID
        :raise UnknownTypeException: If the data type is not known
        :raise NoRegionSelectedException: If no region has been selected
        :raise RegionExhaustedException:
            If the selected region has no more space
        """
        if data_type not in DataType:
            raise UnknownTypeException(
                data_type.value, Commands.WRITE.name)
        if self._current_region is None:
            raise NoRegionSelectedException(Commands.WRITE.name)

        data_size = data_type.size
        if data_size == 1:
            cmd_data_len = 0
        elif data_size == 2:
            cmd_data_len = 1
        elif data_size == 4:
            cmd_data_len = 2
        elif data_size == 8:
            cmd_data_len = 3
        else:
            raise InvalidSizeException(
                data_type.name, data_size, Commands.WRITE.name)

        if repeats_is_register is False:
            _bounds(Commands.WRITE, "repeats", repeats, 1, 256)
        else:
            _bounds(Commands.WRITE, "repeats", repeats, 0, MAX_REGISTERS)
        _bounds(Commands.WRITE, "data_register",
                data_register, 0, MAX_REGISTERS)

        cmd_string = Commands.WRITE.name
        cmd_string += f" data=reg[{data_register:d}]"
        if repeats_is_register:
            reg_usage = SRC1_AND_SRC2
            parameters = repeats << 4
            cmd_string += f", repeats=reg[{repeats:d}]"
        else:
            reg_usage = SRC1_ONLY
            parameters = repeats & 0xFF
            cmd_string += f", repeats={repeats:d}"

        cmd_word = _binencode(Commands.WRITE, {
            _Field.LENGTH: LEN1,
            _Field.USAGE: reg_usage,
            _Field.DESTINATION: cmd_data_len,
            _Field.SOURCE_1: data_register,
            _Field.IMMEDIATE: parameters})
        cmd_string += f", dataType={data_type.name}"
        self._write_command_to_files(cmd_word, cmd_string)

    def write_array(self, array_values, data_type=DataType.UINT32):
        """
        Insert command to write an array, causing the write pointer
        to move on by (data type size * the array size), in bytes.

        :param array_values: An array of words to be written
        :type array_values: list(int) or list(float) or ~numpy.ndarray
        :param DataType data_type: Type of data contained in the array
        :raise DataUndefinedWriterException:
            If the binary specification file writer has not been initialised
        :raise IOError: If a write to external storage fails
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
        self._spec_writer.write(data.tostring())

    def switch_write_focus(self, region):
        """
        Insert command to switch the region being written to.

        :param int region: The ID of the region to switch to, between 0 and 15
        :raise DataUndefinedWriterException:
            If the binary specification file writer has not been initialised
        :raise IOError: If a write to external storage fails
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

    def start_loop(self, counter_register_id, start, end, increment=1,
                   start_is_register=False, end_is_register=False,
                   increment_is_register=False):
        """
        Insert command to start a loop.

        :param int counter_register_id: The ID of the register to use as the
            loop counter, between 0 and 15
        :param int start:
            * If ``start_is_register`` is False, the number at which to start
              the loop counter, >= 0
            * If ``start_is_register`` is True, the ID of the register
              containing the number at which to start the loop counter,
              between 0 and 15
        :param int end:
            * If ``end_is_register`` is False, the number which the loop
              counter must reach to stop the loop i.e. the loop will run while
              the contents of ``counter_register`` < ``end``, >= 0
            * If ``end_is_register`` is True, the ID of the register
              containing the number at which to stop the loop, between 0 and 15
        :param int increment:
            * If ``increment_is_register`` is False, the amount by which to
              increment the loop counter on each run of the loop, >= 0
            * If ``increment_is_register`` is True, the ID of the register
              containing the amount by which to increment the loop counter on
              each run of the loop, between 0 and 15
        :param bool start_is_register: Indicates if ``start`` is a register ID
        :param bool end_is_register: Indicates if ``end`` is a register ID
        :param bool increment_is_register:
            Indicates if ``increment`` is a register ID
        :raise DataUndefinedWriterException:
            If the binary specification file writer has not been initialised
        :raise IOError: If a write to external storage fails
        :raise ParameterOutOfBoundsException:
            * If ``counter_register_id`` is not a valid register ID
            * If ``start_is_register`` is True and ``start`` is not a valid
              register ID
            * If ``end_is_register`` is True and ``end`` is not a valid
              register ID
            * If ``increment_is_register`` is True, and ``increment`` is not a
              valid register ID
            * If ``start_is_register is False and ``start`` is not in the
              allowed range
            * If ``end_is_register is False and ``end`` is not in the allowed
              range
            * If ``increment_is_register`` is False and ``increment`` is not
              in the allowed range
        """
        _bounds(Commands.LOOP, "counter_register_id",
                counter_register_id, 0, MAX_REGISTERS)

        bit_field = 0
        length = LEN1
        encoded_values = bytearray()
        cmd_string = Commands.LOOP.name
        cmd_string += f" counter_register_id=reg[{counter_register_id:d}],"
        r1 = r2 = r3 = 0

        if start_is_register:
            _bounds(Commands.LOOP, "start", start, 0, MAX_REGISTERS)
            bit_field |= 0x4
            r1 = start
            cmd_string += f" start=reg[{start:d}],"
        else:
            _typebounds(Commands.LOOP, "start", start, DataType.INT32)
            length += 1
            encoded_values += _ONE_SIGNED_INT.pack(start)
            cmd_string += f" start={start:d},"

        if end_is_register:
            _bounds(Commands.LOOP, "end", end, 0, MAX_REGISTERS)
            bit_field |= 0x2
            r2 = end
            cmd_string += f" end=reg[{end:d}],"
        else:
            _typebounds(Commands.LOOP, "end", end, DataType.INT32)
            length += 1
            encoded_values += _ONE_SIGNED_INT.pack(end)
            cmd_string += f" end={end:d},"

        if increment_is_register:
            _bounds(Commands.LOOP, "increment", increment, 0, MAX_REGISTERS)
            bit_field |= 0x1
            r3 = increment
            cmd_string += f" increment=reg[{increment:d}],"
        else:
            _typebounds(Commands.LOOP, "increment", increment, DataType.INT32)
            length += 1
            encoded_values += _ONE_SIGNED_INT.pack(increment)
            cmd_string += f" increment={increment:d},"

        self._ongoing_loop = True

        cmd_word = _binencode(Commands.LOOP, {
            _Field.LENGTH: length,
            _Field.USAGE: bit_field,
            _Field.DESTINATION: r1,   # non-standard usage
            _Field.SOURCE_1: r2,      # non-standard usage
            _Field.SOURCE_2: r3,      # non-standard usage
            _Field.IMMEDIATE: counter_register_id})
        self._write_command_to_files(cmd_word + encoded_values, cmd_string)

    def break_loop(self):
        """
        Insert command to break out of a loop before it has completed.

        :raise DataUndefinedWriterException:
            If the binary specification file writer has not been initialised
        :raise IOError: If a write to external storage fails
        :raise InvalidCommandException:
            If there is no loop in operation at this point
        """
        if not self._ongoing_loop:
            raise InvalidCommandException(Commands.BREAK_LOOP.name)

        cmd_word = _binencode(Commands.BREAK_LOOP, {
            _Field.LENGTH: LEN1})
        cmd_string = Commands.BREAK_LOOP.name
        self._write_command_to_files(cmd_word, cmd_string)

    def end_loop(self):
        """
        Insert command to indicate that this is the end of the loop.
        Commands between the start of the loop and this command will be
        repeated.

        :raise DataUndefinedWriterException:
            If the binary specification file writer has not been initialised
        :raise IOError: If a write to external storage fails
        :raise InvalidCommandException:
            If there is no loop in operation at this point
        """
        if not self._ongoing_loop:
            raise InvalidCommandException(Commands.END_LOOP.name)
        cmd_word = _binencode(Commands.END_LOOP, {
            _Field.LENGTH: LEN1})
        cmd_string = Commands.END_LOOP.name
        self._ongoing_loop = False
        self._write_command_to_files(cmd_word, cmd_string)

    def start_conditional(self, register_id, condition, value,
                          value_is_register=False):
        """
        Insert command to start a conditional if...then...else construct. If
        the condition evaluates to true, the statement is executed up to the
        next else statement, or the end of the conditional, whichever comes
        first.

        :param int register_id: The ID of a register to compare the value of
        :param Condition condition:
            The condition which must be true to execute the following commands
        :param int value:
            * If ``value_is_register`` is False, the value to compare to the
              value in the register
            * If ``value_is_register`` is True, the ID of the register
              containing the value to compare, between 0 and 15
        :param bool value_is_register: Indicates if ``value`` is a register ID
        :raise DataUndefinedWriterException:
            If the binary specification file writer has not been initialised
        :raise IOError: If a write to external storage fails
        :raise ParameterOutOfBoundsException:
            * If ``register_id`` is not a valid register ID
            * if ``value_is_register`` is True and ``value`` is not a valid
              register ID
        :raise UnknownConditionException:
            If ``condition`` is not a valid condition
        """
        _bounds(Commands.IF, "register_id", register_id, 0, MAX_REGISTERS)
        if condition not in Condition:
            raise UnknownConditionException(condition, Commands.IF.name)

        data_encoded = bytearray()
        cmd_string = Commands.IF.name
        if value_is_register:
            _bounds(Commands.IF, "value", value, 0, MAX_REGISTERS)
            cmd_word = _binencode(Commands.IF, {
                _Field.LENGTH: LEN1,
                _Field.USAGE: 0x3,
                _Field.SOURCE_1: register_id,
                _Field.SOURCE_2: value,
                _Field.IMMEDIATE: condition})
            cmd_string += (
                f" reg[{register_id:d}] {condition.operator} reg[{value:d}]")
        else:
            _typebounds(Commands.IF, "value", value, DataType.INT32)
            cmd_word = _binencode(Commands.IF, {
                _Field.LENGTH: LEN2,
                _Field.USAGE: 0x2,
                _Field.SOURCE_1: register_id,
                _Field.IMMEDIATE: condition})
            data_encoded += _ONE_SIGNED_INT.pack(value)
            cmd_string += (
                f" reg[{register_id:d}] {condition.operator} {value:d}")

        self._conditionals.append(False)
        cmd_word_list = cmd_word + data_encoded
        self._write_command_to_files(cmd_word_list, cmd_string, indent=True)

    def else_conditional(self):
        """
        Insert command for the else of an if...then...else construct. If the
        condition of the conditional evaluates to false, the statements up
        between the conditional and the insertion of this "else" are skipped,
        and the statements from this point until the end of the conditional
        are executed.

        :raise DataUndefinedWriterException:
            If the binary specification file writer has not been initialised
        :raise IOError: If a write to external storage fails
        :raise InvalidCommandException:
            If there is no conditional in operation at this point
        """

        if not self._conditionals or \
                self._conditionals[len(self._conditionals) - 1] is True:
            raise InvalidCommandException(Commands.ELSE.name)

        self._conditionals[len(self._conditionals) - 1] = True
        cmd_word = _binencode(Commands.ELSE, {
            _Field.LENGTH: LEN1})
        cmd_string = Commands.ELSE.name
        self._write_command_to_files(
            cmd_word, cmd_string, indent=True, outdent=True)

    def end_conditional(self):
        """
        Insert command to mark the end of an if...then...else construct

        :raise DataUndefinedWriterException:
            If the binary specification file writer has not been initialised
        :raise IOError: If a write to external storage fails
        :raise InvalidCommandException:
            If there is no conditional in operation at this point
        """
        if not self._conditionals:
            raise InvalidCommandException(Commands.END_IF.name)

        self._conditionals.pop()
        cmd_word = _binencode(Commands.END_IF, {
            _Field.LENGTH: LEN1})
        cmd_string = Commands.END_IF.name
        self._write_command_to_files(cmd_word, cmd_string, outdent=True)

    def set_register_value(self, register_id, data, data_is_register=False,
                           data_type=DataType.UINT32):
        """
        Insert command to set the value of a register.

        :param int register_id:
            The ID of the register to assign, between 0 and 15
        :param data:
            * If ``data_is_register`` is True, the register ID containing
              the data to set, between 0 and 15
            * If ``data_is_register`` is False, the data is a value of the
              type given by ``data_type``
        :type data: int or float
        :param bool data_is_register: Indicates if ``data`` is a register ID
        :param DataType data_type: The type of the data to be assigned
        :raise DataUndefinedWriterException:
            If the binary specification file writer has not been initialised
        :raise IOError: If a write to external storage fails
        :raise ParameterOutOfBoundsException:
            * If ``register_id`` is not a valid register ID
            * If ``data_is_register`` is True, and ``data`` is not a valid
              register ID
            * If ``data_is_register`` is False, ``data_type`` is an integer
              type and ``data`` has a fractional part
            * If ``data_is_register`` if False, and ``data`` would overflow
              the data type
        :raise UnknownTypeException: If the data type is not known
        """
        _bounds(Commands.MV, "register_id", register_id, 0, MAX_REGISTERS)

        if data_is_register:
            # Build command to move between registers:
            _bounds(Commands.MV, "data", data, 0, MAX_REGISTERS)
            if data == register_id:
                raise DuplicateParameterException(
                    Commands.MV.name, [register_id, data])

            cmd_word = _binencode(Commands.MV, {
                _Field.LENGTH: LEN1,
                _Field.USAGE: DEST_AND_SRC1,
                _Field.DESTINATION: register_id,
                _Field.SOURCE_1: data})
            encoded_data = bytearray()
            cmd_string = f"reg[{register_id:d}] = reg[{data:d}]"
        else:
            # Build command to assign from an immediate:
            # command has a second word (the immediate)
            _typebounds(Commands.MV, "data", data, data_type)

            cmd_word = _binencode(Commands.MV, {
                _Field.LENGTH: LEN3 if data_type.size > 4 else LEN2,
                _Field.USAGE: DEST_ONLY,
                _Field.DESTINATION: register_id})
            encoded_data = data_type.encode(data)
            cmd_string = f"reg[{register_id:d}] = {data:d} (0x{data:X})"

        self._write_command_to_files(cmd_word + encoded_data, cmd_string)

    def save_write_pointer(self, register_id):
        """
        Insert command to save the write pointer to a register.

        :param int register_id:
            The ID of the register to assign, between 0 and 15
        :raise DataUndefinedWriterException:
            If the binary specification file writer has not been initialised
        :raise IOError: If a write to external storage fails
        :raise ParameterOutOfBoundsException:
            If the ``register_id`` is not a valid register ID
        :raise NoRegionSelectedException: If no region has been selected
        """
        _bounds(Commands.GET_WR_PTR, "register_id",
                register_id, 0, MAX_REGISTERS)
        if self._current_region is None:
            raise NoRegionSelectedException(Commands.GET_WR_PTR.name)

        cmd_word = _binencode(Commands.GET_WR_PTR, {
            _Field.LENGTH: LEN1,
            _Field.USAGE: 0x4,
            _Field.DESTINATION: register_id})
        cmd_string = Commands.GET_WR_PTR.name
        cmd_string += f" reg[{register_id:d}]"
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
        :raise DataUndefinedWriterException:
            If the binary specification file writer has not been initialised
        :raise IOError: If a write to external storage fails
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

    def align_write_pointer(self, log_block_size,
                            log_block_size_is_register=False,
                            return_register_id=None):
        """
        Insert command to align the write pointer against a power-of-2
        block size in bytes.  Zeros are inserted in the intervening space

        :param int log_block_size:
            * If ``log_block_size_is_register`` is False, log to base 2 of
              the block size (e.g. The write pointer will be moved so that
              it is a multiple of 2\\ :sup:`log_block_size`), between 0 and 32
            * If ``log_block_size_is_register`` is True, the ID of the
              register containing log to the base 2 of the block size,
              between 0 and 15
        :param bool log_block_size_is_register:
            Indicates if ``log_block_size`` is a register ID
        :param return_register_id: The ID of a register where the write
            pointer will be written to once it has been updated, between
            0 and 15, or `None` if no such writing is to be done
        :type return_register_id: int or None
        :raise DataUndefinedWriterException:
            If the binary specification file writer has not been initialised
        :raise IOError: If a write to external storage fails
        :raise ParameterOutOfBoundsException:
            * If ``log_block_size_is_register`` is False, and
              ``log_block_size`` is not within the allowed range
            * If ``log_block_size_is_register`` is True and
              ``log_block_size`` is not a valid register ID
        :raise RegionOutOfBoundsException:
            If the move of the pointer would put it outside of the current
            region
        :raise NoRegionSelectedException: If no region has been selected
        """
        if self._current_region is None:
            raise NoRegionSelectedException(Commands.ALIGN_WR_PTR.name)

        bit_field = 0
        imm_value = 0
        return_register_value = 0
        block_size_reg = 0
        cmd_string = Commands.ALIGN_WR_PTR.name

        if return_register_id is not None:
            _bounds(Commands.ALIGN_WR_PTR, "return_register_id",
                    return_register_id, 0, MAX_REGISTERS)
            bit_field |= 0x4
            return_register_value = return_register_id
            cmd_string = f" reg[{return_register_value:d}] ="

        if log_block_size_is_register:
            _bounds(Commands.ALIGN_WR_PTR, "log_block_size",
                    log_block_size, 0, MAX_REGISTERS)
            bit_field |= 0x2
            block_size_reg = log_block_size
            cmd_string += f" align(reg[{block_size_reg:d}])"
        else:
            _bounds(Commands.ALIGN_WR_PTR, "log_block_size",
                    log_block_size, 0, 32)
            imm_value = log_block_size
            cmd_string += f" align({imm_value:d})"

        cmd_word = _binencode(Commands.ALIGN_WR_PTR, {
            _Field.LENGTH: LEN1,
            _Field.USAGE: bit_field,
            _Field.DESTINATION: return_register_value,
            _Field.SOURCE_1: block_size_reg,
            _Field.IMMEDIATE: imm_value})
        self._write_command_to_files(cmd_word, cmd_string)

    def call_arithmetic_operation(self, register_id, operand_1, operation,
                                  operand_2, signed,
                                  operand_1_is_register=False,
                                  operand_2_is_register=False):
        """
        Insert command to perform an arithmetic operation on two signed or
        unsigned values and store the result in a register

        :param int register_id: The ID of the register to store the result in
        :param int operand_1:
            * If ``operand_1_is_register`` is True, the ID of a register where
              the first operand can be found, between 0 and 15
            * If ``operand_1_is_register`` is False, a 32-bit value
        :param ArithmeticOperation operation: The operation to perform
        :param int operand_2:
            * If ``operand_2_is_register`` is True, the ID of a register where
              the second operand can be found, between 0 and 15
            * If ``operand_2_is_register`` is False, a 32-bit value
        :param bool signed: Indicates if the values should be considered signed
        :param bool operand_1_is_register:
            Indicates if ``operand_1`` is a register ID
        :param bool operand_2_is_register:
            Indicates if ``operand_2`` is a register ID
        :raise DataUndefinedWriterException:
            If the binary specification file writer has not been initialised
        :raise IOError: If a write to external storage fails
        :raise ParameterOutOfBoundsException:
            * If ``register_id`` is not a valid register ID
            * If ``operand_1_is_register`` is True and ``operand_1`` is not a
              valid register ID
            * If ``operand_2_is_register`` is True and ``operand_2`` is not a
              valid register ID
        :raise InvalidOperationException:
            If ``operation`` is not a known operation
        """
        _bounds(Commands.ARITH_OP, "register_id",
                register_id, 0, MAX_REGISTERS)
        if operation not in ArithmeticOperation:
            raise InvalidOperationException(
                "arithmetic", operation.value, Commands.ARITH_OP.name)

        cmd_length = 0
        bit_field = 0x4
        register_op_1 = 0
        register_op_2 = 0
        encoded_operands = bytearray()

        cmd_string = Commands.ARITH_OP.name
        cmd_string += (
            f' {"SIGNED" if signed else "UNSIGNED"} reg[{register_id:d}] =')

        if operand_1_is_register:
            _bounds(Commands.ARITH_OP, "operand_1",
                    operand_1, 0, MAX_REGISTERS)
            bit_field |= 2
            register_op_1 = operand_1
            cmd_string += f" reg[{register_op_1:d}]"
        elif signed:
            _typebounds(Commands.ARITH_OP, "operand_1",
                        operand_1, DataType.INT32)
            cmd_length += 1
            encoded_operands += _ONE_SIGNED_INT.pack(operand_1)
            cmd_string += f" {operand_1:d}"
        else:
            _typebounds(Commands.ARITH_OP, "operand_1",
                        operand_1, DataType.UINT32)
            cmd_length += 1
            encoded_operands += _ONE_WORD.pack(operand_1)
            cmd_string += f" {operand_1:d}"

        cmd_string += f" {operation.operator}"

        if operand_2_is_register:
            _bounds(Commands.ARITH_OP, "operand_2",
                    operand_2, 0, MAX_REGISTERS)
            bit_field |= 1
            register_op_2 = operand_2
            cmd_string += f" reg[{register_op_2:d}]"
        elif signed:
            _typebounds(Commands.ARITH_OP, "operand_2",
                        operand_2, DataType.INT32)
            cmd_length += 1
            encoded_operands += _ONE_SIGNED_INT.pack(operand_2)
            cmd_string += f" {operand_2:d}"
        else:
            _typebounds(Commands.ARITH_OP, "operand_2",
                        operand_2, DataType.UINT32)
            cmd_length += 1
            encoded_operands += _ONE_WORD.pack(operand_2)
            cmd_string += f" {operand_2:d}"

        cmd_word = _binencode(Commands.ARITH_OP, {
            _Field.LENGTH: cmd_length,
            _Field.SIGNED: bool(signed),
            _Field.USAGE: bit_field,
            _Field.DESTINATION: register_id,
            _Field.SOURCE_1: register_op_1,
            _Field.SOURCE_2: register_op_2,
            _Field.IMMEDIATE: operation})
        self._write_command_to_files(cmd_word + encoded_operands, cmd_string)

    def logical_and(self, register_id, operand_1, operand_2,
                    operand_1_is_register=False, operand_2_is_register=False):
        """
        Insert command to perform a logical AND operation.

        :param int register_id: The ID of the register to store the result in
        :param int operand_1:
            * If ``operand_1_is_register`` is True, the ID of a register
              where the first operand can be found, between 0 and 15
            * If ``operand_1_is_register`` is False, a 32-bit value
        :param int operand_2:
            * If ``operand_2_is_register`` is True, the ID of a register
              where the second operand can be found. between 0 and 15
            * If ``operand_2_is_register`` is False, a 32-bit value
        :param bool operand_1_is_register:
            Indicates if ``operand_1`` is a register ID
        :param bool operand_2_is_register:
            Indicates if ``operand_2`` is a register ID
        :raise DataUndefinedWriterException:
            If the binary specification file writer has not been initialised
        :raise IOError: If a write to external storage fails
        :raise ParameterOutOfBoundsException:
            * If ``register_id`` is not a valid register ID
            * If ``operand_1_is_register`` is True and ``operand_1`` is not a
              valid register ID
            * If ``operand_2_is_register`` is True and ``operand_2`` is not a
              valid register ID
        """
        self._call_logic_operation(
            register_id, operand_1, LogicOperation.AND, operand_2,
            operand_1_is_register, operand_2_is_register)

    def logical_or(self, register_id, operand_1, operand_2,
                   operand_1_is_register=False, operand_2_is_register=False):
        """
        Insert command to perform a logical OR operation.

        :param int register_id: The ID of the register to store the result in
        :param int operand_1:
            * If ``operand_1_is_register`` is True, the ID of a register
              where the first operand can be found, between 0 and 15
            * If ``operand_1_is_register`` is False, a 32-bit value
        :param int operand_2:
            * If ``operand_2_is_register`` is True, the ID of a register
              where the second operand can be found. between 0 and 15
            * If ``operand_2_is_register`` is False, a 32-bit value
        :param bool operand_1_is_register:
            Indicates if ``operand_1`` is a register ID
        :param bool operand_2_is_register:
            Indicates if ``operand_2`` is a register ID
        :raise DataUndefinedWriterException:
            If the binary specification file writer has not been initialised
        :raise IOError: If a write to external storage fails
        :raise ParameterOutOfBoundsException:
            * If ``register_id`` is not a valid register ID
            * If ``operand_1_is_register`` is True and ``operand_1`` is not a
              valid register ID
            * If ``operand_2_is_register`` is True and ``operand_2`` is not a
              valid register ID
        """
        self._call_logic_operation(
            register_id, operand_1, LogicOperation.OR, operand_2,
            operand_1_is_register, operand_2_is_register)

    def logical_left_shift(self, register_id, operand_1, operand_2,
                           operand_1_is_register=False,
                           operand_2_is_register=False):
        """
        Insert command to perform a logical left shift operation.

        :param int register_id: The ID of the register to store the result in
        :param int operand_1:
            * If ``operand_1_is_register`` is True, the ID of a register
              where the first operand can be found, between 0 and 15
            * If ``operand_1_is_register`` is False, a 32-bit value
        :param int operand_2:
            * If ``operand_2_is_register`` is True, the ID of a register
              where the second operand can be found. between 0 and 15
            * If ``operand_2_is_register`` is False, a 32-bit value
        :param bool operand_1_is_register:
            Indicates if ``operand_1`` is a register ID
        :param bool operand_2_is_register:
            Indicates if ``operand_2`` is a register ID
        :raise DataUndefinedWriterException:
            If the binary specification file writer has not been initialised
        :raise IOError: If a write to external storage fails
        :raise ParameterOutOfBoundsException:
            * If ``register_id`` is not a valid register ID
            * If ``operand_1_is_register`` is True and ``operand_1`` is not a
              valid register ID
            * If ``operand_2_is_register`` is True and ``operand_2`` is not a
              valid register ID
        """
        self._call_logic_operation(
            register_id, operand_1, LogicOperation.LEFT_SHIFT, operand_2,
            operand_1_is_register, operand_2_is_register)

    def logical_right_shift(self, register_id, operand_1, operand_2,
                            operand_1_is_register=False,
                            operand_2_is_register=False):
        """
        Insert command to perform a logical right shift operation.

        :param int register_id: The ID of the register to store the result in
        :param int operand_1:
            * If ``operand_1_is_register`` is True, the ID of a register
              where the first operand can be found, between 0 and 15
            * If ``operand_1_is_register`` is False, a 32-bit value
        :param int operand_2:
            * If ``operand_2_is_register`` is True, the ID of a register
              where the second operand can be found. between 0 and 15
            * If ``operand_2_is_register`` is False, a 32-bit value
        :param bool operand_1_is_register:
            Indicates if ``operand_1`` is a register ID
        :param bool operand_2_is_register:
            Indicates if ``operand_2`` is a register ID
        :raise DataUndefinedWriterException:
            If the binary specification file writer has not been initialised
        :raise IOError: If a write to external storage fails
        :raise ParameterOutOfBoundsException:
            * If ``register_id`` is not a valid register ID
            * If ``operand_1_is_register`` is True and ``operand_1`` is not a
              valid register ID
            * If ``operand_2_is_register`` is True and ``operand_2`` is not a
              valid register ID
        """
        self._call_logic_operation(
            register_id, operand_1, LogicOperation.RIGHT_SHIFT, operand_2,
            operand_1_is_register, operand_2_is_register)

    def logical_xor(self, register_id, operand_1, operand_2,
                    operand_1_is_register=False, operand_2_is_register=False):
        """
        Insert command to perform a logical XOR operation.

        :param int register_id: The ID of the register to store the result in
        :param int operand_1:
            * If ``operand_1_is_register`` is True, the ID of a register
              where the first operand can be found, between 0 and 15
            * If ``operand_1_is_register`` is False, a 32-bit value
        :param int operand_2:
            * If ``operand_2_is_register`` is True, the ID of a register
              where the second operand can be found. between 0 and 15
            * If ``operand_2_is_register`` is False, a 32-bit value
        :param bool operand_1_is_register:
            Indicates if ``operand_1`` is a register ID
        :param bool operand_2_is_register:
            Indicates if ``operand_2`` is a register ID
        :raise DataUndefinedWriterException:
            If the binary specification file writer has not been initialised
        :raise IOError: If a write to external storage fails
        :raise ParameterOutOfBoundsException:
            * If ``register_id`` is not a valid register ID
            * If ``operand_1_is_register`` is True and ``operand_1`` is not a
              valid register ID
            * If ``operand_2_is_register`` is True and ``operand_2`` is not a
              valid register ID
        """
        self._call_logic_operation(
            register_id, operand_1, LogicOperation.XOR, operand_2,
            operand_1_is_register, operand_2_is_register)

    def logical_not(self, register_id, operand, operand_is_register=False):
        """
        Insert command to perform a logical NOT operation.

        :param int register_id: The ID of the register to store the result in
        :param int operand:
            * If ``operand_is_register`` is True, the ID of a register where
              the first operand can be found, between 0 and 15
            * If ``operand_is_register`` is False, a 32-bit value
        :param bool operand_is_register:
            Indicates if ``operand`` is a register ID
        :raise DataUndefinedWriterException:
            If the binary specification file writer has not been initialised
        :raise IOError: If a write to external storage fails
        :raise ParameterOutOfBoundsException:
            * If ``register_id`` is not a valid register ID
            * If ``operand_is_register`` is True and ``operand`` is not a
              valid register ID
        """
        self._call_logic_operation(
            register_id, operand, LogicOperation.NOT, 0,
            operand_is_register, False)

    def _call_logic_operation(self, register_id, operand_1, operation,
                              operand_2, operand_1_is_register=False,
                              operand_2_is_register=False):
        """
        Insert command to perform a logic operation on two signed or
        unsigned values and store the result in a register.

        :param int register_id: The ID of the register to store the result in
        :param int operand_1:
            * If ``operand_1_is_register`` is True, the ID of a register
              where the first operand can be found, between 0 and 15
            * If ``operand_1_is_register`` is False, a 32-bit value
        :param LogicOperation operation: The operation to perform
        :param int operand_2:
            * If ``operand_2_is_register`` is True, the ID of a register
              where the second operand can be found. between 0 and 15
            * If ``operand_2_is_register`` is False, a 32-bit value
        :param bool operand_1_is_register:
            Indicates if ``operand_1`` is a register ID
        :param bool operand_2_is_register:
            Indicates if ``operand_2`` is a register ID
        :raise DataUndefinedWriterException:
            If the binary specification file writer has not been initialised
        :raise IOError: If a write to external storage fails
        :raise ParameterOutOfBoundsException:
            * If ``register_id`` is not a valid register ID
            * If ``operand_1_is_register`` is True and ``operand_1`` is not a
              valid register ID
            * If ``operand_2_is_register`` is True and ``operand_2`` is not a
              valid register ID
        :raise InvalidOperationException:
            If ``operation`` is not a known operation
        """
        _bounds(Commands.LOGIC_OP, "register_id",
                register_id, 0, MAX_REGISTERS)
        if operation not in LogicOperation:
            raise InvalidOperationException(
                "logic", operation.value, Commands.LOGIC_OP.name)

        cmd_length = 0
        bit_field = 0x4
        register_op_1 = 0
        register_op_2 = 0
        encoded_operands = bytearray()

        cmd_string = Commands.LOGIC_OP.name
        cmd_string += f" reg[{register_id:d}] ="
        if operation.value == LogicOperation.NOT.value:
            cmd_string += f" {operation.operator}"

        if operand_1_is_register:
            _bounds(Commands.LOGIC_OP, "operand_1",
                    operand_1, 0, MAX_REGISTERS)
            bit_field |= 2
            register_op_1 = operand_1
            cmd_string += f" reg[{register_op_1:d}]"
        else:
            cmd_length += 1
            _typebounds(Commands.LOGIC_OP, "operand_1",
                        operand_1, DataType.UINT32)
            encoded_operands += _ONE_WORD.pack(operand_1)
            cmd_string += f" {operand_1}"

        if operation.value != LogicOperation.NOT.value:
            cmd_string += f" {operation.operator}"
            if operand_2_is_register:
                _bounds(Commands.LOGIC_OP, "operand_2",
                        operand_2, 0, MAX_REGISTERS)
                bit_field |= 1
                register_op_2 = operand_2
                cmd_string += f" reg[{register_op_2:d}]"
            else:
                cmd_length += 1
                _typebounds(Commands.LOGIC_OP, "operand_2",
                            operand_2, DataType.UINT32)
                encoded_operands += _ONE_WORD.pack(operand_2)
                cmd_string += f" {operand_2}"

        cmd_word = _binencode(Commands.LOGIC_OP, {
            _Field.LENGTH: cmd_length,
            _Field.USAGE: bit_field,
            _Field.DESTINATION: register_id,
            _Field.SOURCE_1: register_op_1,
            _Field.SOURCE_2: register_op_2,
            _Field.IMMEDIATE: operation})
        self._write_command_to_files(cmd_word + encoded_operands, cmd_string)

    def copy_structure(self, source_structure_id, destination_structure_id,
                       source_id_is_register=False,
                       destination_id_is_register=False):
        """
        Insert command to copy a structure, possibly overwriting another
        structure.

        :param int source_structure_id:
            * If ``source_id_is_register`` is True, the ID of the register
              holding the source structure ID, between 0 and 15
            * Otherwise, the ID of the source structure, between 0 and 15
        :param int destination_structure_id:
            * If ``destination_id_is_register`` is True, the ID of the
              register holding the destination structure ID, between 0 and 15
            * If ``destination_id_is_register`` is False, the ID of the
              destination structure, between 0 and 15
        :param bool source_id_is_register:
            Indicates if ``source_structure_id`` is a register ID
        :param bool destination_id_is_register:
            Indicates if ``destination_structure_id`` is a register ID
        :raise DataUndefinedWriterException:
            If the binary specification file writer has not been initialised
        :raise IOError: If a write to external storage fails
        :raise ParameterOutOfBoundsException:
            * If ``source_id_is_register`` is True and
              ``source_structure_id`` is not a valid register ID
            * If ``destination_id_is_register`` is True and
              ``destination_structure_id`` is not a valid register ID
            * If ``source_id_is_register`` is False and
              ``source_structure_id`` is not a valid structure ID
            * If ``destination_id_is_register`` is False and
              ``destination_structure_id`` is not a valid structure ID
        :raise NotAllocatedException:
            * If no structure with ID ``source_structure_id`` has been
              allocated
        """
        if source_structure_id == destination_structure_id and \
                destination_id_is_register == source_id_is_register:
            raise DuplicateParameterException(
                Commands.COPY_STRUCT.name,
                [source_structure_id, destination_structure_id])

        bit_field = 0
        cmd_string = Commands.COPY_STRUCT.name

        if source_id_is_register:
            _bounds(Commands.COPY_STRUCT, "source_structure_id",
                    source_structure_id, 0, MAX_REGISTERS)
            bit_field |= SRC1_ONLY
            cmd_string += f" source_struct=reg[{source_structure_id:d}]"
        else:
            _bounds(Commands.COPY_STRUCT, "source_structure_id",
                    source_structure_id, 0, MAX_STRUCT_SLOTS)
            if self._struct_slots[source_structure_id] is None:
                raise NotAllocatedException(
                    "struct", source_structure_id, Commands.COPY_STRUCT.name)
            cmd_string += f" source_struct={source_structure_id:d}"

        if destination_id_is_register:
            _bounds(Commands.COPY_STRUCT, "destination_structure_id",
                    destination_structure_id, 0, MAX_REGISTERS)
            bit_field |= DEST_ONLY
            cmd_string += (
                f" destination_struct=reg[{destination_structure_id:d}]")
        else:
            _bounds(Commands.COPY_STRUCT, "destination_structure_id",
                    destination_structure_id, 0, MAX_STRUCT_SLOTS)
            cmd_string += f" destination_struct={destination_structure_id:d}"

        cmd_word = _binencode(Commands.COPY_STRUCT, {
            _Field.LENGTH: LEN1,
            _Field.USAGE: bit_field,
            _Field.DESTINATION: destination_structure_id,
            _Field.SOURCE_1: source_structure_id})
        self._write_command_to_files(cmd_word, cmd_string)

    def copy_structure_parameter(
            self, source_structure_id, source_parameter_index,
            destination_id, destination_parameter_index=None,
            destination_is_register=False):
        """
        Insert command to copy the value of a parameter from one
        structure to another.

        :param int source_structure_id:
            The ID of the source structure, between 0 and 15
        :param int source_parameter_index:
            The index of the parameter in the source structure
        :param int destination_id: The ID of the destination structure, or
            the ID of the destination register, between 0 and 15
        :param int destination_parameter_index: The index of the parameter in
            the destination structure. Ignored when writing to a register.
        :param bool destination_is_register:
            Indicates whether the destination is a structure or a register.
        :raise DataUndefinedWriterException:
            If the binary specification file writer has not been initialised
        :raise IOError: If a write to external storage fails
        :raise ParameterOutOfBoundsException:
            * If ``source_structure_id`` is not a valid structure ID
            * If ``destination_id`` is not a valid structure ID
            * If ``source_parameter_index`` is not a valid parameter index
              in the source structure
            * If ``destination_parameter_index`` is not a valid parameter
              index in the destination structure
        :raise NotAllocatedException:
            * If no structure with ID ``destination_id`` has been allocated
            * If no structure with ID ``source_structure_id`` has been
              allocated
        """
        _bounds(Commands.COPY_PARAM, "source_structure_id",
                source_structure_id, 0, MAX_STRUCT_SLOTS)
        _bounds(Commands.COPY_PARAM, "source_parameter_index",
                source_parameter_index, 0, MAX_STRUCT_ELEMENTS)
        if self._struct_slots[source_structure_id] is None:
            raise NotAllocatedException(
                "structure", source_structure_id, Commands.COPY_PARAM.name)
        if (len(self._struct_slots[source_structure_id]) <=
                source_parameter_index):
            raise NotAllocatedException(
                "parameter", source_parameter_index, Commands.COPY_PARAM.name)

        cmd_string = Commands.COPY_PARAM.name
        if not destination_is_register:
            _bounds(Commands.COPY_PARAM, "destination_parameter_index",
                    destination_parameter_index, 0, MAX_STRUCT_ELEMENTS)
            _bounds(Commands.COPY_PARAM, "destination_structure_id",
                    destination_id, 0, MAX_STRUCT_SLOTS)
            if self._struct_slots[destination_id] is None:
                raise NotAllocatedException(
                    "structure", destination_id, Commands.COPY_PARAM.name)
            if (len(self._struct_slots[source_structure_id]) <=
                    source_parameter_index):
                raise NotAllocatedException(
                    "parameter", destination_parameter_index,
                    Commands.COPY_PARAM.name)
            if (len(self._struct_slots[destination_id]) <=
                    destination_parameter_index):
                raise NotAllocatedException(
                    "parameter", destination_parameter_index,
                    Commands.COPY_PARAM.name)
            if (self._struct_slots[source_structure_id]
                    [source_parameter_index][1] !=
                    self._struct_slots[destination_id]
                    [destination_parameter_index][1]):
                raise TypeMismatchException(Commands.COPY_PARAM.name)
            if (source_structure_id == destination_id and
                    destination_parameter_index == source_parameter_index):
                raise DuplicateParameterException(
                    Commands.COPY_PARAM.name, [
                        source_structure_id, source_parameter_index,
                        destination_id, destination_parameter_index])

            cmd_word_1 = _binencode(Commands.COPY_PARAM, {
                _Field.LENGTH: LEN2,
                _Field.USAGE: NO_REGS,
                _Field.DESTINATION: destination_id,
                _Field.SOURCE_1: source_structure_id})
            param_word = ((destination_parameter_index << 8) |
                          source_parameter_index)
            cmd_string += (
                f" source_structure_id = {source_structure_id:d}, "
                f"source_parameter_id = {source_parameter_index:d}, "
                f"destination_structure_id = {destination_id:d}, "
                f"destination_parameter_id = {destination_parameter_index:d}")
        else:
            _bounds(Commands.COPY_PARAM, "destination_register_id",
                    destination_id, 0, MAX_REGISTERS)

            cmd_word_1 = _binencode(Commands.COPY_PARAM, {
                _Field.LENGTH: LEN2,
                _Field.USAGE: DEST_ONLY,
                _Field.DESTINATION: destination_id,
                _Field.SOURCE_1: source_structure_id})
            param_word = source_parameter_index
            cmd_string += (
                f" source_structure_id = {source_structure_id:d}, "
                f"source_parameter_id = {source_parameter_index:d}, "
                f"destination_register_id = {destination_id:d}")

        cmd_word_list = cmd_word_1 + _ONE_WORD.pack(param_word)
        self._write_command_to_files(cmd_word_list, cmd_string)

    def print_value(self, value, value_is_register=False,
                    data_type=DataType.UINT32):
        """
        Insert command to print out a value (for debugging).

        :param value:
            * If ``value_is_register`` is True, the ID of the register
              containing the value to print
            * If ``value_is_register`` is False, the value to print as a
              value of type given by ``data_type``
        :type value: float or int
        :param bool value_is_register: Indicates if ``value`` is a register
        :param DataType data_type: The type of the data to be printed
        :raise DataUndefinedWriterException:
            If the binary specification file writer has not been initialised
        :raise IOError: If a write to external storage fails
        :raise ParameterOutOfBoundsException:
            * If ``value_is_register`` is True and ``value`` is not a valid
              register ID
            * If ``value_is_register`` is False, the ``data_type`` is an
              integer type and ``value`` has a fractional part
            * If ``value_is_register`` is False and the ``value`` would
              overflow the data type
        :raise UnknownTypeException: If ``data_type`` is not a valid data type
        """
        source_register_id = 0
        bit_field = 0
        data_encoded = bytearray()
        cmd_string = Commands.PRINT_VAL.name

        if value_is_register:
            _bounds(Commands.PRINT_VAL, "value", value, 0, MAX_REGISTERS)
            cmd_word_length = LEN1
            bit_field |= 2
            source_register_id = value
            cmd_string += f" reg[{source_register_id:d}]"
        else:
            _typebounds(Commands.PRINT_VAL, "value", value, data_type)
            cmd_word_length = LEN2 if data_type.size <= 4 else LEN3
            data_encoded += data_type.encode(value)
            cmd_string += f" {value:d}"

        cmd_word = _binencode(Commands.PRINT_VAL, {
            _Field.LENGTH: cmd_word_length,
            _Field.USAGE: bit_field,
            _Field.SOURCE_1: source_register_id,
            _Field.IMMEDIATE: data_type})
        self._write_command_to_files(cmd_word + data_encoded, cmd_string)

    def print_text(self, text, encoding="ASCII"):
        """
        Insert command to print some text (for debugging).

        :param str text: The text to write (max 12 *bytes* once encoded)
        :param str encoding:
            The character encoding to use for the string. Defaults to ASCII.
        :raise DataUndefinedWriterException:
            If the binary specification file writer has not been initialised
        :raise IOError: If a write to external storage fails
        """
        text_encoded = bytearray(text.encode(encoding=encoding))
        text_len = len(text_encoded)
        _bounds(Commands.PRINT_TXT, "len(text)", text_len, 1, 13)

        if text_len <= 4:
            cmd_word_len = LEN2
        elif text_len <= 8:
            cmd_word_len = LEN3
        else:
            cmd_word_len = LEN4

        # add final padding to the encoded text
        if text_len % 4 != 0:
            text_encoded += bytearray(4 - text_len % 4)

        cmd_string = Commands.PRINT_TXT.name
        cmd_string += f' "{text}"'
        cmd_word = _binencode(Commands.PRINT_TXT, {
            _Field.LENGTH: cmd_word_len,
            _Field.IMMEDIATE: text_len - 1})
        self._write_command_to_files(cmd_word + text_encoded, cmd_string)

    def print_struct(self, structure_id, structure_id_is_register=False):
        """
        Insert command to print out a structure (for debugging).

        :param int structure_id:
            * If ``structure_id_is_register`` is True, the ID of the register
              containing the ID of the structure to print, between 0 and 15
            * If ``structure_id_is_register`` is False, the ID of the
              structure to print, between 0 and 15
        :param bool structure_id_is_register:
            Indicates if the ``structure_id`` is a register
        :raise DataUndefinedWriterException:
            If the binary specification file writer has not been initialised
        :raise IOError: If a write to external storage fails
        :raise ParameterOutOfBoundsException:
            * If ``structure_id_is_register`` is True and ``structure_id`` is
              not a valid register ID
            * If ``structure_id_is_register`` is False and ``structure_id``
              is not a valid structure ID
        :raise NotAllocatedException:
            If ``structure_id_is_register`` is False and ``structure_id`` is
            the ID of a structure that has not been allocated
        """
        cmd_string = Commands.PRINT_STRUCT.name
        if structure_id_is_register:
            _bounds(Commands.PRINT_STRUCT, "structure_id",
                    structure_id, 0, MAX_REGISTERS)
            struct_register = structure_id
            structure_id = 0
            bit_field = 0x2
            cmd_string += f" struct(reg[{struct_register:d}])"
        else:
            _bounds(Commands.PRINT_STRUCT, "structure_id",
                    structure_id, 0, MAX_STRUCT_SLOTS)
            if self._struct_slots[structure_id] is None:
                raise NotAllocatedException(
                    "structure", structure_id, Commands.PRINT_STRUCT.name)
            struct_register = 0
            bit_field = 0
            cmd_string += f" struct({structure_id:d})"

        cmd_word = _binencode(Commands.PRINT_STRUCT, {
            _Field.LENGTH: LEN1,
            _Field.USAGE: bit_field,
            _Field.SOURCE_1: struct_register,
            _Field.IMMEDIATE: structure_id})
        self._write_command_to_files(cmd_word, cmd_string)

    def end_specification(self, close_writer=True):
        """
        Insert a command to indicate that the specification has finished
        and finish writing.

        :param bool close_writer:
            Indicates whether to close the underlying writer(s)
        :raise DataUndefinedWriterException:
            If the binary specification file writer has not been initialised
        :raise IOError: If a write to external storage fails
        """
        self.comment("\nEnd of specification:")

        cmd_word = _binencode(Commands.END_SPEC, {
            _Field.LENGTH: LEN1})
        encoded_parameter = _ONE_SIGNED_INT.pack(-1)
        cmd_string = Commands.END_SPEC.name
        self._write_command_to_files(cmd_word + encoded_parameter, cmd_string)

        if close_writer:
            self._spec_writer.close()
            self._spec_writer = None
            if self._report_writer is not None:
                self._report_writer.close()
                self._report_writer = None

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
        :raise DataUndefinedWriterException:
            If the binary specification file writer has not been initialised
        :raise IOError: If a write to external storage fails
        """
        if self._spec_writer is None:
            raise DataUndefinedWriterException(
                "The spec file writer has not been initialised")
        elif cmd_word_list:
            self._spec_writer.write(cmd_word_list)

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

    @property
    def current_region(self):
        """
        The ID of the current DSG region we're writing to.
        If not yet writing to any region, ``None``.

        :rtype: int or None
        """
        return self._current_region
