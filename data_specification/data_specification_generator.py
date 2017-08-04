import decimal
import logging
import numpy
import struct
from spinn_machine import sdram

from .constants import MAX_MEM_REGIONS, MAX_CONSTRUCTORS, MAX_REGISTERS, \
    MAX_STRUCT_ELEMENTS, MAX_STRUCT_SLOTS, MAX_RNGS, MAX_RANDOM_DISTS, \
    LEN1, LEN2, LEN3, LEN4, \
    NO_REGS, DEST_AND_SRC1, DEST_ONLY, SRC1_ONLY, SRC1_AND_SRC2
from .exceptions import DataSpecificationParameterOutOfBoundsException, \
    DataSpecificationNotAllocatedException, \
    DataSpecificationTypeMismatchException, \
    DataSpecificationRegionInUseException, DataUndefinedWriterException, \
    DataSpecificationInvalidCommandException, \
    DataSpecificationUnknownConditionException, \
    DataSpecificationUnknownTypeException, DataSpecificationRNGInUseException,\
    DataSpecificationRandomNumberDistributionInUseException, \
    DataSpecificationStructureInUseException, \
    DataSpecificationInvalidSizeException, DataSpecificationFunctionInUse, \
    DataSpecificationWrongParameterNumberException, \
    DataSpecificationDuplicateParameterException, \
    DataSpecificationNoRegionSelectedException, \
    DataSpecificationRegionUnfilledException, \
    DataSpecificationInvalidOperationException
from data_specification.enums import \
    DataType, RandomNumberGenerator, Commands, Condition, LogicOperation, \
    ArithmeticOperation
from enum import Enum

logger = logging.getLogger(__name__)


def _bounds(cmd, name, value, low, high):
    if value < low or value >= high:
        raise DataSpecificationParameterOutOfBoundsException(
            name, value, low, high - 1, cmd.name)


def _typebounds(cmd, name, value, type):  # @ReservedAssignment
    if value < type.min or value > type.max:
        raise DataSpecificationParameterOutOfBoundsException(
            name, value, type.min, type.max, cmd.name)


def _binencode(length, command, arguments=[]):
    if len(arguments) & 1 == 1:
        raise KeyError()
    cmd_word = (length << 28) | (command.value << 20)
    i = 0
    while i < len(arguments):
        val = arguments[i]
        i += 1
        if isinstance(val, Enum):
            val = val.value
        shift = arguments[i] if i < len(arguments) else 0
        i += 1
        if shift < 0 or shift > 31:
            raise KeyError()
        cmd_word |= val << shift
    return bytearray(struct.pack("<I", cmd_word))



class DataSpecificationGenerator(object):
    """ Used to generate a data specification language file that can be\
        executed to produce a memory image
    """

    __slots__ = [
        # The object to write the specification to
        "spec_writer",

        # the writer for the human readable report
        "report_writer",

        # ????????
        "txt_indent",

        # how many instructions has been executed ?????
        "instruction_counter",

        # ???????
        "mem_slot",

        # ???????
        "function",

        # ???????
        "struct_slot",

        # ????????
        "rng",

        # ????????
        "random_distribution",

        # ???????
        "conditionals",

        # the current dsg region we're writing to
        "current_region",

        # ?????????
        "ongoing_function_definition",

        # ????????
        "ongoing_loop"
    ]

    MAGIC_NUMBER = 0xAD130AD6
    VERSION = 1

    def __init__(self, spec_writer, report_writer=None):
        """
        :param spec_writer: The object to write the specification to
        :type spec_writer: Implementation of\
        :py:class:`data_specification.abstract_data_writer.AbstractDataWriter`
        :param report_writer: Determines if a text version of the\
                    specification is to be written
        :type report_writer: Implementation of\
        :py:class:`data_specification.abstract_data_writer.AbstractDataWriter`
        :raise spinn_storage_handlers.exceptions.DataWriteException:\
                    If a write to external storage fails
        """
        self.spec_writer = spec_writer
        self.report_writer = report_writer
        self.txt_indent = 0
        self.instruction_counter = 0
        self.mem_slot = [0] * MAX_MEM_REGIONS
        self.function = [0] * MAX_CONSTRUCTORS
        self.struct_slot = [0] * MAX_STRUCT_SLOTS
        self.rng = [0] * MAX_RNGS
        self.random_distribution = [0] * MAX_RANDOM_DISTS
        self.conditionals = []
        self.current_region = None
        self.ongoing_function_definition = False
        self.ongoing_loop = False

    def comment(self, comment):
        """ Write a comment to the text version of the specification.\
            Note that this is ignored by the binary file

        :param comment: The comment to write
        :type comment: str
        :return: Nothing is returned
        :raise data_specification.exceptions.DataUndefinedWriterException:\
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException:\
            If a write to external storage fails
        """
        self.write_command_to_files(
            bytearray(), comment, no_instruction_number=True)

    def define_break(self):
        """ Insert command to stop execution with an exception (for debugging)

        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException:\
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException:\
            If a write to external storage fails
        """
        cmd_word = _binencode(LEN1, Commands.BREAK)
        cmd_string = "BREAK"
        self.write_command_to_files(cmd_word, cmd_string)

    def no_operation(self):
        """ Insert command to execute nothing

        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException:\
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException:\
            If a write to external storage fails
        """
        cmd_word = _binencode(LEN1, Commands.NOP)
        cmd_string = "NOP"
        self.write_command_to_files(cmd_word, cmd_string)
        return

    def reserve_memory_region(
            self, region, size, label=None, empty=False, shrink=True):
        """ Insert command to reserve a memory region

        :param region: The number of the region to reserve, from 0 to 15
        :type region: int
        :param size: The size to reserve for the region in bytes
        :type size: int
        :param label: An optional label for the region
        :type label: str
        :param empty: Specifies if the region will be left empty
        :type empty: bool
        :param shrink: Specifies if the region will be compressed
        :type shrink: bool
        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException:\
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException:\
            If a write to external storage fails
        :raise data_specification.exceptions.\
            DataSpecificationRegionInUseException: If the region was already \
            reserved
        :raise data_specification.exceptions.\
            DataSpecificationParameterOutOfBoundsException: If the region
            requested was out of the allowed range, or that the size was too \
            big to fit in SDRAM
        """
        _bounds(Commands.RESERVE, "memory region identifier",
                region, 0, MAX_MEM_REGIONS)

        if self.mem_slot[region] != 0:
            error_string = "Error: Requested memory region ({0:d}) ".format(
                region)
            error_string += "is already allocated.\n"
            logger.error(error_string)
            raise DataSpecificationRegionInUseException(region)

        _bounds(Commands.RESERVE, "memory size",
                size, 1, sdram.SDRAM.DEFAULT_SDRAM_BYTES)

        self.mem_slot[region] = [size, label, empty]

        cmd_word = _binencode(LEN2, Commands.RESERVE, [
            NO_REGS, 16,
            bool(empty), 7,
            bool(shrink), 6,
            region])
        encoded_size = bytearray(struct.pack("<I", size))
        cmd_word_list = cmd_word + encoded_size

        if empty:
            unfilled_string = "UNFILLED"
        else:
            unfilled_string = ""

        if label is None:
            cmd_string = "RESERVE memRegion={0:d} size={1:d} {2:s}".format(
                region, size, unfilled_string)
        else:
            cmd_string = (
                "RESERVE memRegion={0:d} size={1:d} label='{2:s}' {3:s}"
                .format(region, size, label, unfilled_string))

        self.write_command_to_files(cmd_word_list, cmd_string)

    def free_memory_region(self, region):
        """ Insert command to free a previously reserved memory region

        :param region: The number of the region to free, from 0 to 15
        :type region: int
        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException:\
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException:\
            If a write to external storage fails
        :raise data_specification.exceptions.\
            DataSpecificationNotAllocatedException: If the region was not\
            reserved
        :raise data_specification.exceptions.\
            DataSpecificationParameterOutOfBoundsException: If the region \
            requested was out of the allowed range
        """
        _bounds(Commands.FREE, "memory region identifier",
                region, 0, MAX_MEM_REGIONS)
        if self.mem_slot[region] == 0:
            raise DataSpecificationNotAllocatedException(
                "region", region, Commands.FREE)

        self.mem_slot[region] = 0

        cmd_word = _binencode(LEN1, Commands.FREE, [
            NO_REGS, 16,
            region])
        cmd_string = "FREE memRegion={0:d}".format(region)

        self.write_command_to_files(cmd_word, cmd_string)

    def declare_random_number_generator(self, rng_id, rng_type, seed):
        """ Insert command to declare a random number generator

        :param rng_id: The id of the random number generator
        :type rng_id: int
        :param rng_type: The type of the random number generator
        :type rng_type: :py:class:`RandomNumberGenerator`
        :param seed: The seed of the random number generator >= 0
        :type seed: int
        :return: The id of the created random number generator,\
                    between 0 and 15
        :rtype: int
        :raise data_specification.exceptions.DataUndefinedWriterException:\
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException:\
            If a write to external storage fails
        :raise data_specification.exceptions.DataSpecification:\
            If there is no more space for a new generator
        :raise data_specification.exceptions.\
            DataSpecificationUnknownTypeException: If the rng_type is not one \
            of the allowed values
        :raise data_specification.exceptions.\
            DataSpecificationParameterOutOfBoundsException:
            * If the seed is too big or too small
            * If the rng_id is not in the allowed range
        :raise data_specification.exceptions\
            .DataSpecificationRNGInUseException:
            If the random number generator with the given id has already been\
            defined
        """

        _bounds(Commands.DECLARE_RNG, "random number generator id",
                rng_id, 0, MAX_RNGS)

        if rng_type not in RandomNumberGenerator:
            raise DataSpecificationUnknownTypeException(
                rng_type.value, Commands.DECLARE_RNG)

        if self.rng[rng_id] is not 0:
            raise DataSpecificationRNGInUseException(rng_id)

        _typebounds(Commands.DECLARE_RNG, "seed", seed, DataType.UINT32)

        self.rng[rng_id] = [rng_type, seed]

        cmd_word = _binencode(LEN2, Commands.DECLARE_RNG, [
            rng_id, 12,
            rng_type, 8])
        encoded_seed = bytearray(struct.pack("<i", seed))

        cmd_string = "DECLARE_RNG id={0:d}, source={1:d}, seed={2:d}".format(
            rng_id, rng_type.value, seed)
        self.write_command_to_files(cmd_word + encoded_seed, cmd_string)

    def declare_uniform_random_distribution(
            self, distribution_id, structure_id, rng_id, min_value, max_value):
        """ Insert commands to declare a uniform random distribution

        :param distribution_id: id of the distribution being set up
        :param distribution_id: int
        :param structure_id: id of an empty structure slot to fill with the
            uniform random distribution data
        :type structure_id: int
        :param rng_id: The id of the random number generator, between 0 and 15
        :type rng_id: int
        :param min_value: The minimum value that should be returned from the\
            distribution between -32768.0 and max_value
        :type min_value: float
        :param max_value: The maximum value that should be returned from the\
            distribution between min_value and 32767.9999847
        :type max_value: float
        :return: The id of the created uniform random distribution to be used\
            in future calls of the distribution between 0 and 63
        :rtype: int
        :raise data_specification.exceptions.DataUndefinedWriterException:\
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException:\
            If a write to external storage fails
        :raise data_specification.exceptions.DataSpecificationNoMoreException:\
            If there is no more space for a new random distribution
        :raise data_specification.exceptions.\
            DataSpecificationNotAllocatedException: If the requested rng_id \
            has not been allocated
        :raise data_specification.exceptions.\
            DataSpecificationParameterOutOfBoundsException: If rng_id, \
            structure_id, min_value or max_value is out of range
        :raise data_specification.exceptions.\
            DataSpecificationStructureInUseException: If structure \
            structure_id is already defined
        """
        _bounds(Commands.DECLARE_RANDOM_DIST, "distribution id",
                distribution_id, 0, MAX_RANDOM_DISTS)
        _bounds(Commands.DECLARE_RANDOM_DIST, "rng id",
                rng_id, 0, MAX_RNGS)

        if self.rng[rng_id] is 0:
            raise DataSpecificationNotAllocatedException(
                "RNG", rng_id, Commands.DECLARE_RANDOM_DIST)

        _typebounds(Commands.DECLARE_RANDOM_DIST, "min_value",
                    min_value, DataType.S1615)
        _typebounds(Commands.DECLARE_RANDOM_DIST, "max_value",
                    max_value, DataType.S1615)
        _bounds(Commands.DECLARE_RANDOM_DIST, "structure id",
                structure_id, 0, MAX_STRUCT_SLOTS)

        if self.random_distribution[distribution_id] is not 0:
            raise DataSpecificationRandomNumberDistributionInUseException(
                distribution_id)

        parameters = [("distType", DataType.UINT32, 0),
                      ("rngID", DataType.UINT32, rng_id),
                      ("param1", DataType.S1615, min_value),
                      ("param2", DataType.S1615, max_value)]

        self.random_distribution[distribution_id] = parameters
        self.define_structure(structure_id, parameters)

        cmd_word = _binencode(LEN1, Commands.DECLARE_RANDOM_DIST, [
            distribution_id, 8,
            structure_id])
        cmd_string = "DECLARE_RANDOM_DIST distribution_id={0:d} " \
                     "structure_id={1:d}".format(distribution_id, structure_id)
        self.write_command_to_files(cmd_word, cmd_string)

    def call_random_distribution(self, distribution_id, register_id):
        """ Insert command to get the next random number from  a random\
            distribution, placing the result in a register to be used in a\
            future call

        :param distribution_id: The id of the random distribution to call\
            between 0 and 63
        :type distribution_id: int
        :param register_id: The id of the register to store the result in\
            between 0 and 15
        :type register_id: int
        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException:\
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException:\
            If a write to external storage fails
        :raise data_specification.exceptions.\
            DataSpecificationNotAllocatedException: If the random distribution\
            id was not previously declared
        :raise data_specification.exceptions.\
            DataSpecificationParameterOutOfBoundsException: If the \
            distribution_id or register_id specified was out of range
        """
        _bounds(Commands.GET_RANDOM_NUMBER, "register_id",
                register_id, 0, MAX_REGISTERS)
        _bounds(Commands.GET_RANDOM_NUMBER, "distribution_id",
                distribution_id, 0, MAX_RANDOM_DISTS)

        if self.random_distribution[distribution_id] is 0:
            raise DataSpecificationNotAllocatedException(
                "random number distribution", distribution_id,
                Commands.GET_RANDOM_NUMBER)

        bit_field = 0x4

        cmd_string = "GET_RANDOM_NUMBER distribution={0:d} dest=reg[{1:d}]"\
            .format(distribution_id, register_id)
        cmd_word = _binencode(LEN1, Commands.GET_RANDOM_NUMBER, [
            bit_field, 16,
            register_id, 12,
            distribution_id])
        self.write_command_to_files(cmd_word, cmd_string)

    def define_structure(self, structure_id, parameters):
        """ Insert commands to define a data structure

        :param structure_id: the id of the structure to create,\
            between 0 and 15
        :type structure_id: int
        :param parameters: A list of between 1 and 255 tuples of (label,\
            data_type, value) where:
                * label is the label of the element (for debugging)
                * data_type is the data type of the element
                * value is the value of the element, or None if no value is to\
                  be assigned
        :type parameters: list of (str, :py:class:`DataType`, float)
        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException:\
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException:\
            If a write to external storage fails
        :raise data_specification.exceptions.DataSpecificationNoMoreException:\
            If there are no more spaces for new structures
        :raise data_specification.exceptions.\
            DataSpecificationParameterOutOfBoundsException:\
            * If there are an incorrect number of parameters
            * If the size of one of the tuples is incorrect
            * If one of the values to be assigned has an integer\
              data_type but has a fractional part
            * If one of the values to be assigned would overflow its\
              data_type
        :raise data_specification.exceptions.\
            DataSpecificationUnknownTypeException: If one of the data types in\
            the structure is unknown
        """
        # start of struct
        _bounds(Commands.START_STRUCT, "structure id",
                structure_id, 0, MAX_STRUCT_SLOTS)
        _bounds(Commands.WRITE_PARAM, "structure elements",
                len(parameters), 0, MAX_STRUCT_ELEMENTS)

        if self.struct_slot[structure_id] != 0:
            raise DataSpecificationStructureInUseException(structure_id)
        self.struct_slot[structure_id] = parameters

        cmd_word = _binencode(LEN1, Commands.START_STRUCT, [
            structure_id])
        cmd_string = "START_STRUCT id={0:d}".format(structure_id)
        self.write_command_to_files(cmd_word, cmd_string)

        # elements of the struct
        elem_index = 0
        for i in parameters:
            label = i[0]
            data_type = i[1]
            value = i[2]

            if data_type not in DataType:
                raise DataSpecificationUnknownTypeException(
                    data_type.value, Commands.WRITE_PARAM)

            if value is not None:
                _typebounds(Commands.WRITE_PARAM, "value", value, data_type)

                if data_type.size <= 4:
                    cmd_word = _binencode(LEN2, Commands.STRUCT_ELEM, [
                        data_type])
                elif data_type.size == 8:
                    cmd_word = _binencode(LEN3, Commands.STRUCT_ELEM, [
                        data_type])
                else:
                    raise DataSpecificationInvalidSizeException(
                        data_type.name, data_type.size, Commands.STRUCT_ELEM)

                data_format = "<{}".format(data_type.struct_encoding)
                text_value = "{}".format(value)
                data_value = decimal.Decimal(text_value) * data_type.scale
                value_encoded = bytearray(struct.pack(data_format, data_value))

                if data_type.size == 1:
                    padding = bytearray(3)
                elif data_type.size == 2:
                    padding = bytearray(2)
                else:
                    padding = bytearray()

                cmd_word_list = cmd_word + value_encoded + padding

                if len(label) == 0:
                    cmd_string = "STRUCT_ELEM element_id={0:d}, element_type="\
                                 "{1:s}, value = {2:d}".format(
                                     elem_index, data_type.name, value)
                else:
                    cmd_string = "STRUCT_ELEM element_id={0:d}, element_type="\
                                 "{1:s}, value = {2:f}, label = {3:s}"
                    cmd_string = cmd_string.format(
                        elem_index, data_type.name, value, label)

                self.write_command_to_files(cmd_word_list, cmd_string)

            else:
                label = i[0]
                data_type = i[1]

                cmd_word = _binencode(LEN1, Commands.STRUCT_ELEM, [
                    data_type])
                if len(label) == 0:
                    cmd_string = \
                        "STRUCT_ELEM element_id={0:d}, element_type={1:s}"\
                        .format(elem_index, data_type.name)
                else:
                    cmd_string = \
                        "STRUCT_ELEM element_id={0:d}, element_type="\
                        "{1:s}, label={2:s}".format(
                            elem_index, data_type.name, label)
                self.write_command_to_files(cmd_word, cmd_string)
            elem_index += 1

        # end of struct
        cmd_word = _binencode(LEN1, Commands.END_STRUCT)
        cmd_string = "END_STRUCT id={0:d}".format(structure_id)
        self.write_command_to_files(cmd_word, cmd_string)

    def get_structure_value(
            self, destination_id, structure_id, parameter_index,
            parameter_index_is_register=False):
        """ Insert command to get a value from a structure.\
            The value is copied in a register.

        :param destination_id: The id of the destination register
        :type destination_id: int
        :param structure_id: The id of the source structure
        :type structure_id: int
        :param parameter_index: The id of the parameter/element to copy
        :type parameter_index: int
        :param parameter_index_is_register: True if the index of the structure\
            is contained in a register
        :type parameter_index_is_register: bool
        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException:\
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException:\
            If a write to external storage fails
        :raise data_specification.exceptions.\
            DataSpecificationParameterOutOfBoundsException:\
            * If structure_id is not in the allowed range
            * If parameter_index is larger than the number of parameters\
              declared in the original structure
            * If destination_id is not the id of a valid register
            * If parameter_index_is_register is True and parameter_index is\
              not a valid register id
        :raise data_specification.exceptions.\
            DataSpecificationNotAllocatedException: If the structure requested\
            has not been declared
        """
        _bounds(Commands.READ_PARAM, "structure_id",
                structure_id, 0, MAX_STRUCT_SLOTS)
        _bounds(Commands.READ_PARAM, "destination_id",
                destination_id, 0, MAX_REGISTERS)

        if self.struct_slot[structure_id] is 0:
            raise DataSpecificationNotAllocatedException(
                "structure", structure_id, Commands.READ_PARAM)

        if parameter_index_is_register is True:
            _bounds(Commands.READ_PARAM, "parameter_index",
                    parameter_index, 0, MAX_REGISTERS)
            cmd_word = _binencode(LEN1, Commands.READ_PARAM, [
                DEST_AND_SRC1, 16,
                destination_id, 12,
                parameter_index, 8,
                structure_id])
            cmd_string = "READ_PARAM structure_id={0:d}, "  \
                         "element_id_from_register={1:d}, " \
                         "destination_register={2:d}".format(
                             structure_id, parameter_index, destination_id)
        else:
            _bounds(Commands.READ_PARAM, "parameter_index",
                    parameter_index, 0, MAX_STRUCT_ELEMENTS)
            if len(self.struct_slot[structure_id]) <= parameter_index:
                raise DataSpecificationNotAllocatedException(
                    "structure %d parameter" % structure_id,
                    parameter_index, Commands.READ_PARAM)

            cmd_word = _binencode(LEN1, Commands.READ_PARAM, [
                DEST_ONLY, 16,
                destination_id, 12,
                parameter_index, 4,
                structure_id])
            cmd_string = "READ_PARAM structure_id={0:d}, element_id={1:d}, " \
                         "destination_register={2:d}".\
                format(structure_id, parameter_index, destination_id)

        self.write_command_to_files(cmd_word, cmd_string)

    def set_structure_value(self, structure_id, parameter_index, value,
                            data_type, value_is_register=False):
        """ Insert command to set a value in a structure

        :param structure_id:
            * If called outside of a function, the id of the structure\
              between 0 and 15
            * If called within a function, the id of the structure
              argument, between 0 and 4
        :type structure_id: int
        :param parameter_index: The index of the value to assign in the\
            structure, between 0 and the number of parameters declared in the\
            structure
        :type parameter_index: int
        :param value:
            * If value_is_register is False, the value to assign at the\
              selected position as a float
            * If value_is_register is True, the id of the register containing\
              the value to assign to the position, between 0 and 15
        :type value: float
        :param data_type: type of the data to be stored in the structure.\
            If parameter value_is_register is set to true, this variable is\
            disregarded
        :type data_type: :py:class:`DataType`
        :param value_is_register: Identifies if value identifies a register
        :type value_is_register: bool
        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException:\
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException:\
            If a write to external storage fails
        :raise data_specification.exceptions.\
            DataSpecificationParameterOutOfBoundsException:\
            * If structure_id is not in the allowed range
            * If parameter_index is larger than the number of parameters\
              declared in the original structure
            * If value_is_register is False, and the data type of the\
              structure value is an integer, and the value has a fractional\
              part
            * If value_is_register is False, and value would overflow the\
              position in the structure
            * If value_is_register is True, and value is not a valid register\
              id
        :raise data_specification.exceptions.\
            DataSpecificationNotAllocatedException: If the structure requested\
            has not been declared
        """
        _bounds(Commands.WRITE_PARAM, "structure_id",
                structure_id, 0, MAX_STRUCT_SLOTS)
        _bounds(Commands.WRITE_PARAM, "parameter_index",
                parameter_index, 0, MAX_STRUCT_ELEMENTS)

        if self.struct_slot[structure_id] is 0:
            raise DataSpecificationNotAllocatedException(
                "structure", structure_id, Commands.WRITE_PARAM)
        if len(self.struct_slot[structure_id]) <= parameter_index:
            raise DataSpecificationNotAllocatedException(
                "structure %d parameter" % structure_id, parameter_index,
                Commands.WRITE_PARAM)
        if self.struct_slot[structure_id][parameter_index][1] is not data_type:
            raise DataSpecificationTypeMismatchException(Commands.WRITE_PARAM)

        if value_is_register:
            _bounds(Commands.WRITE_PARAM, "value", value, 0, MAX_REGISTERS)
            cmd_word = _binencode(LEN1, Commands.WRITE_PARAM, [
                SRC1_ONLY, 16,
                structure_id, 12,
                value, 8,
                parameter_index])
            value_encoded = bytearray()
            cmd_string = "WRITE_PARAM structure_id={0:d}, element_id={1:d}, " \
                         "value=reg[{2:d}]".format(
                             structure_id, parameter_index, value)
        else:
            _typebounds(Commands.WRITE_PARAM, "value", value, data_type)
            if data_type.size > 4 and data_type.size != 8:
                raise DataSpecificationInvalidSizeException(
                    data_type.name, data_type.size, Commands.WRITE_PARAM)

            cmd_word = _binencode((LEN2 if data_type.size <= 4 else LEN3),
                                  Commands.WRITE_PARAM, [
                                      NO_REGS, 16,
                                      structure_id, 12,
                                      parameter_index])
            encoding_string = "<{0:s}".format(data_type.struct_encoding)
            value_encoded = bytearray(struct.pack(encoding_string, value))
            if data_type.size == 1:
                value_encoded += bytearray(3)
            elif data_type.size == 2:
                value_encoded += bytearray(2)

            cmd_string = "WRITE_PARAM structure_id={0:d}, element_id={1:d}, " \
                         "value={2:d}".format(
                             structure_id, parameter_index, value)

        self.write_command_to_files(cmd_word + value_encoded, cmd_string)

    def write_structure(
            self, structure_id, repeats=1, repeats_is_register=False):
        """ Insert command to write a structure to the current write pointer,\
            causing the current write pointer to move on by the number of\
            bytes needed to represent the structure

        :param structure_id:
            * If called within a function, the id of the structure to write,\
              between 0 and 15
            * If called outside of a function, the id of the structure\
              argument, between 0 and 5
        :type structure_id: int
        :param repeats:
            * If repeats_is_register is True, the id of the register\
              containing the number of repeats, between 0 and 15
            * If repeats_is_register is False, the number of repeats to write,\
              between 0 and 255
        :type repeats: int
        :param repeats_is_register: Identifies if repeats identifies a register
        :type repeats_is_register: bool
        :return: No value returned
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException:\
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException:\
            If a write to external storage fails
        :raise data_specification.exceptions.\
            DataSpecificationParameterOutOfBoundsException:\
            * If repeats_is_register is False and structure_id is not\
              a valid id
            * If repeats_is_register is True and structure_id
            * If the number of repeats is out of range
        :raise data_specification.exceptions.\
            DataSpecificationNoRegionSelectedException: If no region has been \
            selected to write to
        :raise data_specification.exceptions.\
            DataSpecificationRegionExhaustedException: If the selected region \
            has no more space
        """
        _bounds(Commands.WRITE_STRUCT, "structure_id",
                structure_id, 0, MAX_STRUCT_SLOTS)
        if self.struct_slot[structure_id] is 0:
            raise DataSpecificationNotAllocatedException(
                "structure", structure_id, Commands.WRITE_STRUCT)

        if repeats_is_register:
            _bounds(Commands.WRITE_STRUCT, "repeats",
                    repeats, 0, MAX_REGISTERS)
            cmd_word = _binencode(LEN1, Commands.WRITE_STRUCT, [
                SRC1_ONLY, 16,
                repeats, 8,
                structure_id])
            cmd_string = "WRITE_STRUCT structure_id={0:d}, " \
                         "repeats=reg[{1:d}]".format(structure_id, repeats)
        else:
            _bounds(Commands.WRITE_STRUCT, "repeats", repeats, 0, 16)
            cmd_word = _binencode(LEN1, Commands.WRITE_STRUCT, [
                repeats, 8,
                structure_id])
            cmd_string = "WRITE_STRUCT structure_id={0:d}, " \
                         "repeats={1:d}".format(structure_id, repeats)
        self.write_command_to_files(cmd_word, cmd_string)

    def start_function(self, function_id, argument_by_value):
        """Insert command to start a function definition, with up to 5 \
        arguments, which are the ids of structures to be used within the \
        function, each of which can be passed by reference or by value. In \
        the commands following this command up to the end_function command, \
        structures can only be referenced using the numbers 1 to 5 which \
        address the arguments, rather than the original structure ids.

        :param function_id: The id of the function currently defined.
        :type function_id: int
        :param argument_by_value: A list of up to 5 booleans indicating if the\
            structure to be passed as an argument is to be passed by \
            reference (i.e. changes made within the function are persisted) \
            or by value (i.e. changes made within the function are lost when \
            the function exits. The number of arguments is determined by the \
            length of this list.
        :type argument_by_value: list of bool
        :return: The id of the function, between 0 and 31
        :rtype: int
        :raise data_specification.exceptions.\
            DataSpecificationParameterOutOfBoundsException: If there are too \
            many items in the list of arguments
        :raise data_specification.exceptions.\
            DataSpecificationInvalidCommandException: If there is already a \
            function being defined at this point
        :raise data_specification.exceptions.\
            DataSpecificationFunctionInUse: If the function is already defined
        """
        if self.ongoing_function_definition:
            raise DataSpecificationInvalidCommandException(
                Commands.START_CONSTRUCTOR)

        _bounds(Commands.START_CONSTRUCTOR, "number of arguments",
                len(argument_by_value), 0, 6)
        _bounds(Commands.START_CONSTRUCTOR, "function_id",
                function_id, 0, MAX_CONSTRUCTORS)
        if self.function[function_id] != 0:
            raise DataSpecificationFunctionInUse(function_id)

        self.function[function_id] = argument_by_value

        cmd_string = "START_CONSTRUCTOR id={0:d} number_of_args={1:d}".format(
            function_id, len(argument_by_value))

        self.ongoing_function_definition = True

        read_only_flags = 0
        for i in xrange(len(argument_by_value)):
            cmd_string = "{0:s} arg[{1:d}]=".format(cmd_string, i + 1)
            if argument_by_value[i]:
                read_only_flags |= 2 ** i
                cmd_string = "{0:s}read-only".format(cmd_string)
            else:
                cmd_string = "{0:s}read-write".format(cmd_string)

        cmd_word = _binencode(LEN1, Commands.START_CONSTRUCTOR, [
            function_id, 11,
            len(argument_by_value), 8,
            read_only_flags])
        self.write_command_to_files(cmd_word, cmd_string, indent=True)

    def end_function(self):
        """ Insert command to mark the end of a function definition

        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.\
            DataSpecificationInvalidCommandException: If there is no function \
            being defined at this point
        """

        if not self.ongoing_function_definition:
            raise DataSpecificationInvalidCommandException(
                Commands.END_CONSTRUCTOR)

        self.ongoing_function_definition = False

        cmd_word = _binencode(LEN1, Commands.END_CONSTRUCTOR)
        cmd_string = "END_CONSTRUCT"
        self.write_command_to_files(cmd_word, cmd_string, outdent=True)

    def call_function(self, function_id, structure_ids):
        """ Insert command to call a function

        :param function_id: The id of a previously defined function, between 0\
            and 31
        :type function_id: int
        :param structure_ids: A list of structure_ids that will be passed into\
            the function, each between 0 and 15
        :type structure_ids: list of int
        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException:\
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException:\
            If a write to external storage fails
        :raise data_specification.exceptions.\
            DataSpecificationParameterOutOfBoundsException:\
            * If the function id is not valid
            * If any of the structure ids are not valid
        :raise data_specification.exceptions.\
            DataSpecificationNotAllocatedException:\
            * If a function has not been defined with the given id
            * If no structure has been defined with one of the ids in\
              structure_ids
        :raise data_specification.exceptions.\
            DataSpecificationWrongParameterNumberException:\
            If a function is called with a wrong number of parameters
        :raise data_specification.exceptions.\
            DataSpecificationDuplicateParameterException:\
            If a function is called with duplicate parameters
        """
        _bounds(Commands.CONSTRUCT, "function",
                function_id, 0, MAX_CONSTRUCTORS)

        if self.function[function_id] == 0:
            raise DataSpecificationNotAllocatedException(
                "function", function_id, Commands.CONSTRUCT)
        if len(structure_ids) != len(self.function[function_id]):
            raise DataSpecificationWrongParameterNumberException(
                function_id, len(self.function[function_id]), structure_ids)
        if len(structure_ids) != len(set(structure_ids)):
            raise DataSpecificationDuplicateParameterException(
                "CONSTRUCT %d" % function_id, structure_ids)

        cmd_string = "CONSTRUCT function_id={0:d}".format(function_id)

        param_word = None
        if len(structure_ids) > 0:
            param_word = 0
            for i in xrange(len(structure_ids)):
                _bounds(Commands.CONSTRUCT,
                        "structure argument {0:d}".format(i),
                        structure_ids[i], 0, MAX_STRUCT_SLOTS)
                if self.struct_slot[structure_ids[i]] == 0:
                    raise DataSpecificationNotAllocatedException(
                        "structure argument {0:d}".format(i),
                        structure_ids[i], Commands.CONSTRUCT)

                param_word |= structure_ids[i] << (6 * i)
                cmd_string += " arg[{0:d}]=struct[{1:d}]".format(
                    i, structure_ids[i])

        if param_word is None:
            cmd_word_length = LEN1
            param_word_encoded = bytearray()
        else:
            cmd_word_length = LEN2
            param_word_encoded = bytearray(struct.pack("<I", param_word))

        cmd_word = _binencode(cmd_word_length, Commands.CONSTRUCT, [
            function_id, 8])
        self.write_command_to_files(cmd_word + param_word_encoded, cmd_string)

    def read_value(self, dest_id, data_type):
        """ Insert command to read a value from the current write pointer,\
            causing the write pointer to move by the number of bytes read.\
            The data is stored in a register passed as argument.

        :param dest_id: The id of the destination register.
        :type dest_id: int
        :param data_type: The type of the data to be read.
        :type data_type: :py:class:`DataType`
        :return: Nothing is returned
        :rtype: None
        """
        if data_type not in DataType:
            raise DataSpecificationUnknownTypeException(
                data_type.value, Commands.READ)
        _bounds(Commands.READ, "register", dest_id, 0, MAX_REGISTERS)

        cmd_word = _binencode(LEN1, Commands.READ, [
            DEST_ONLY, 16,
            dest_id, 12,
            data_type.size])
        cmd_string = "READ {0:d} bytes in register {0:d}".format(
            data_type.size, dest_id)
        self.write_command_to_files(cmd_word, cmd_string)

    def write_value(
            self, data, repeats=1, repeats_is_register=False,
            data_type=DataType.UINT32):
        """ Insert command to write a value one or more times to the current\
            write pointer, causing the write pointer to move on by the number\
            of bytes required to represent the data type. The data is passed\
            as a parameter to this function

        :param data: the data to write as a float.
        :type data: float
        :param repeats:
            * If repeats_is_register is False, this parameter identifies the\
              number of times to repeat the data, between 1 and 255\
              (default 1)
            * If repeats_is_register is True, this parameter identifies the\
              register that contains the number of repeats.
        :type repeats: int
        :param repeats_is_register: Indicates if the parameter repeats\
                                    identifies the register containing the\
                                    number of repeats of the value to write
        :type repeats_is_register: bool
        :param data_type: the type to convert data to
        :type data_type: :py:class:`DataType`
        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException:\
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException:\
            If a write to external storage fails
        :raise data_specification.exceptions.\
            DataSpecificationParameterOutOfBoundsException:\
            * If repeats_register is None, and repeats is out of range
            * If repeats_register is not a valid register id
            * If data_type is an integer type, and data has a fractional part
            * If data would overflow the data type
        :raise data_specification.exceptions.\
            DataSpecificationUnknownTypeException: If the data type is not\
            known
        :raise data_specification.exceptions.\
            DataSpecificationInvalidSizeException: If the data size is invalid
        :raise data_specification.exceptions.\
            DataSpecificationNoRegionSelectedException: If no region has been \
            selected to write to
        """
        if self.current_region is None:
            raise DataSpecificationNoRegionSelectedException(Commands.WRITE)
        if data_type not in DataType:
            raise DataSpecificationUnknownTypeException(
                data_type.value, Commands.WRITE)

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
            raise DataSpecificationInvalidSizeException(
                data_type.name, data_size, Commands.WRITE)

        if repeats_is_register is False:
            _bounds(Commands.WRITE, "repeats", repeats, 0, 256)
        else:
            _bounds(Commands.WRITE, "repeats", repeats, 0, MAX_REGISTERS)
        _typebounds(Commands.WRITE, "data", data, data_type)

        parameters = 0
        cmd_string = None
        if self.report_writer is not None:
            cmd_string = "WRITE data=0x%8.8X" % data

        if repeats_is_register is not False:
            repeat_reg_usage = 1
            parameters |= (repeats << 4)
            if self.report_writer is not None:
                cmd_string += ", repeats=reg[{0:d}]".format(repeats)
        else:
            repeat_reg_usage = NO_REGS
            parameters |= repeats
            if self.report_writer is not None:
                cmd_string += ", repeats={0:d}".format(repeats)

        cmd_word = _binencode(cmd_data_len, Commands.WRITE, [
            repeat_reg_usage, 16,
            data_len, 12,
            parameters])
        data_value = decimal.Decimal("{}".format(data)) * data_type.scale
        padding = 4 - data_type.size if data_type.size < 4 else 0
        data_word = struct.pack(
            "<{}{}x".format(data_type.struct_encoding, padding),
            data_value)
        if self.report_writer is not None:
            cmd_string += ", dataType={0:s}".format(data_type.name)
        self.write_command_to_files(cmd_word + data_word, cmd_string)

    def write_value_from_register(
            self, data_register, repeats=1, repeats_is_register=False,
            data_type=DataType.UINT32):
        """ Insert command to write a value one or more times at the write\
            pointer of the current memory region, causing it to move.\
            The data is contained in a register whose id is passed to the\
            function

        :param data_register: Identifies the register in which the data is\
                              stored.
        :type data_register: int
        :param repeats:
            * If repeats_register is None, this parameter identifies the\
              number of times to repeat the data, between 1 and 255\
              (default 1)
            * If repeats_register is not None (i.e. has an integer value), the\
              content of this parameter is disregarded
        :type repeats: int
        :param repeats_is_register: Identifies the register containing the\
            number of repeats of the value to write
        :type repeats_is_register: None or int
        :param data_type: the type of the data held in the register
        :type data_type: :py:class:`DataType`
        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException:\
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException:\
            If a write to external storage fails
        :raise data_specification.exceptions.\
            DataSpecificationParameterOutOfBoundsException:\
            * If repeats_register is None, and repeats is out of range
            * If repeats_register is not a valid register id
            * If data_register is not a valid register id
        :raise data_specification.exceptions.\
            DataSpecificationUnknownTypeException: If the data type is not\
            known
        :raise data_specification.exceptions.\
            DataSpecificationNoRegionSelectedException: If no region has been \
            selected to write to
        :raise data_specification.exceptions.\
            DataSpecificationRegionExhaustedException: If the selected region \
            has no more space
        """
        if data_type not in DataType:
            raise DataSpecificationUnknownTypeException(
                data_type.value, Commands.WRITE)

        if self.current_region is None:
            raise DataSpecificationNoRegionSelectedException(Commands.WRITE)

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
            raise DataSpecificationInvalidSizeException(
                data_type.name, data_size, Commands.WRITE)

        if repeats_is_register is False:
            _bounds(Commands.WRITE, "repeats", repeats, 0, 256)
        else:
            _bounds(Commands.WRITE, "repeats", repeats, 0, MAX_REGISTERS)

        _bounds(Commands.WRITE, "data_register",
                data_register, 0, MAX_REGISTERS)

        parameters = 0
        cmd_string = "WRITE data=reg[{0:d}]".format(data_register)

        if repeats_is_register:
            reg_usage = SRC1_AND_SRC2
            parameters |= repeats << 4
            cmd_string += ", repeats=reg[{0:d}]".format(repeats)
        else:
            reg_usage = SRC1_ONLY
            parameters |= repeats
            cmd_string += ", repeats={0:d}".format(repeats)

        cmd_word = _binencode(LEN1, Commands.WRITE, [
            reg_usage, 16,
            cmd_data_len, 12,
            data_register, 8,
            parameters])
        cmd_string += ", dataType={0:s}".format(data_type.name)
        self.write_command_to_files(cmd_word, cmd_string)

    def write_array(self, array_values, data_type=DataType.UINT32):
        """ Insert command to write an array, causing the write pointer\
            to move on by (data type size * the array size), in bytes.

        :param array_values: An array of words to be written
        :type array_values: list of unsigned int
        :param data_type: Type of data contained in the array
        :type data_type: data_specification.enums.DataType
        :return: The position of the write pointer within the current region,\
            in bytes from the start of the region
        :rtype: int
        :raise data_specification.exceptions.DataUndefinedWriterException:\
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException:\
            If a write to external storage fails
        :raise data_specification.exceptions.\
               DataSpecificationNoRegionSelectedException:
            If no region has been previously selected
        """

        if self.current_region is None:
            raise DataSpecificationNoRegionSelectedException(
                Commands.WRITE_ARRAY)

        cmd_word = _binencode(LEN2, Commands.WRITE_ARRAY, [
            data_type.size])
        data = numpy.array(array_values, dtype='uint32')
        cmd_string = "WRITE_ARRAY, %d elements\n" % (data.size)
        arg_word = bytearray(struct.pack("<I", cmd_word, data.size))
        self.write_command_to_files(cmd_word + arg_word, cmd_string)
        self.spec_writer.write(data.tostring())

    def switch_write_focus(self, region):
        """ Insert command to switch the region being written to

        :param region: The id of the region to switch to, between 0 and 15
        :type region: int
        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException:\
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException:\
            If a write to external storage fails
        :raise data_specification.exceptions.\
            DataSpecificationParameterOutOfBoundsException: If the region \
            identifier is not valid
        :raise data_specification.exceptions.\
            DataSpecificationNotAllocatedException: If the region has not been\
            allocated
        :raise data_specification.exceptions.\
            DataSpecificationRegionUnfilledException: If the selected region \
            should not be filled
        """
        _bounds(Commands.SWITCH_FOCUS, "region", region, 0, MAX_MEM_REGIONS)
        if self.mem_slot[region] == 0:
            raise DataSpecificationNotAllocatedException(
                "region", region, Commands.SWITCH_FOCUS) 
        if self.mem_slot[region][2]:
            raise DataSpecificationRegionUnfilledException(
                region, Commands.SWITCH_FOCUS)

        self.current_region = region

        cmd_string = "SWITCH_FOCUS memRegion = {0:d}".format(region)
        # Write command to switch focus:
        cmd_word = _binencode(LEN1, Commands.SWITCH_FOCUS, [
            0x0, 16,
            region & 0xF, 8])
        self.write_command_to_files(cmd_word, cmd_string)

    def start_loop(self, counter_register_id, start, end, increment=1,
                   start_is_register=False, end_is_register=False,
                   increment_is_register=False):
        """ Insert command to start a loop

        :param counter_register_id: The id of the register to use as the loop\
            counter, between 0 and 15
        :type counter_register_id: int
        :param start:
            * If start_is_register is False, the number at which to start\
              the loop counter, >= 0
            * If start_is_register is True, the id of the register containing\
              the number at which to start the loop counter, between 0 and 15
        :type start: int
        :param end:
            * If end_is_register is False, the number which the loop counter\
              must reach to stop the loop i.e. the loop will run while the\
              contents of counter_register < end, >= 0
            * If end_is_register is True, the id of the register containing\
              the number at which to stop the loop, between 0 and 15
        :type end: int
        :param increment:
            * If increment_is_register is False, the amount by which to\
              increment the loop counter on each run of the loop, >= 0
            * If increment_is_register is True, the id of the register\
              containing the amount by which to increment the loop counter on\
              each run of the loop, between 0 and 15
        :type increment: int
        :param start_is_register: Indicates if start is a register id
        :type start_is_register: bool
        :param end_is_register: Indicates if end is a register id
        :type end_is_register: bool
        :param increment_is_register: Indicates if increment is a register id
        :type increment_is_register: bool
        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException:\
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException:\
            If a write to external storage fails
        :raise data_specification.exceptions.\
            DataSpecificationParameterOutOfBoundsException:\
            * If counter_register_id is not a valid register id
            * If start_is_register is True and increment is not a valid\
              register_id
            * If end_is_register is True and increment is not a valid\
              register_id
            * If increment_is_register is True, and increment is not a valid\
              register_id
            * If start_is_register is False and start is not in the\
              allowed range
            * If end_is_register is False and end is not in the allowed range
            * If increment_is_register is False and increment is not in the\
              allowed range
        """
        _bounds(Commands.LOOP, "counter_register_id",
                counter_register_id, 0, MAX_REGISTERS)

        bit_field = 0
        length = LEN1
        encoded_values = bytearray()
        params = 0
        cmd_string = "LOOP counter_register_id=reg[{0:d}],".format(
            counter_register_id)

        if start_is_register:
            _bounds(Commands.LOOP, "start", start, 0, MAX_REGISTERS)
            bit_field |= 0x4
            params |= start << 8
            cmd_string += " start=reg[{0:d}],".format(start)
        else:
            _typebounds(Commands.LOOP, "start", start, DataType.INT32)
            length += 1
            encoded_values += bytearray(struct.pack("<i", start))
            cmd_string += " start={0:d},".format(start)

        if end_is_register:
            _bounds(Commands.LOOP, "end", end, 0, MAX_REGISTERS)
            bit_field |= 0x2
            params |= end << 4
            cmd_string += " end=reg[{0:d}],".format(end)
        else:
            _typebounds(Commands.LOOP, "end", end, DataType.INT32)
            length += 1
            encoded_values += bytearray(struct.pack("<i", end))
            cmd_string += " end={0:d},".format(end)

        if increment_is_register:
            _bounds(Commands.LOOP, "increment", increment, 0, MAX_REGISTERS)
            bit_field |= 0x1
            params |= increment
            cmd_string += " increment=reg[{0:d}],".format(increment)
        else:
            _typebounds(Commands.LOOP, "increment", increment, DataType.INT32)
            length += 1
            encoded_values += bytearray(struct.pack("<i", increment))
            cmd_string += " increment={0:d},".format(increment)

        self.ongoing_loop = True

        cmd_word = _binencode(length, Commands.LOOP, [
            bit_field, 16,
            params, 4,
            counter_register_id])
        self.write_command_to_files(cmd_word + encoded_values, cmd_string)

    def break_loop(self):
        """ Insert command to break out of a loop before it has completed

        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException:\
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException:\
            If a write to external storage fails
        :raise data_specification.exceptions.\
            DataSpecificationInvalidCommandException: If there is no loop in \
            operation at this point
        """
        if self.ongoing_loop is not True:
            raise DataSpecificationInvalidCommandException(Commands.BREAK_LOOP)
        cmd_word = _binencode(LEN1, Commands.BREAK_LOOP)
        cmd_string = "BREAK_LOOP"
        self.write_command_to_files(cmd_word, cmd_string)

    def end_loop(self):
        """ Insert command to indicate that this is the end of the loop.\
            Commands between the start of the loop and this command will be\
            repeated.

        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException:\
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException:\
            If a write to external storage fails
        :raise data_specification.exceptions.\
            DataSpecificationInvalidCommandException: If there is no loop in \
            operation at this point
        """
        if self.ongoing_loop is not True:
            raise DataSpecificationInvalidCommandException(Commands.END_LOOP)
        cmd_word = _binencode(LEN1, Commands.END_LOOP)
        cmd_string = "END_LOOP"
        self.ongoing_loop = False
        self.write_command_to_files(cmd_word, cmd_string)

    def start_conditional(self, register_id, condition, value,
                          value_is_register=False):
        """ Insert command to start a conditional if...then...else construct.\
            If the condition evaluates to true, the statement is executed up\
            to the next else statement, or the end of the conditional,\
            whichever comes first.

        :param register_id: The id of a register to compare the value of
        :type register_id: int
        :param condition: The condition which must be true to execute the\
            following commands
        :type condition: :py:class:`Condition`
        :param value:
            * If value_is_register is False, the value to compare to\
              the value in the register
            * If value_is_register is True, the id of the register\
              containing the value to compare, between 0 and 15
        :type value: int
        :param value_is_register: Indicates if value is a register id
        :type value_is_register: bool
        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException:\
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException:\
            If a write to external storage fails
        :raise data_specification.exceptions.\
            DataSpecificationParameterOutOfBoundsException:\
            * If the register_id is not a valid register id
            * if value_is_register is True and value is not a valid\
              register id
        :raise data_specification.exceptions.\
            DataSpecificationUnknownTypeException: If the condition is not a \
            valid condition
        """
        cmd_word = 0
        cmd_string = ""

        _bounds(Commands.IF, "register_id", register_id, 0, MAX_REGISTERS)
        if value_is_register:
            _bounds(Commands.IF, "value", value, 0, MAX_REGISTERS)
        else:
            _typebounds(Commands.IF, "value", value, DataType.INT32)

        if condition not in Condition:
            raise DataSpecificationUnknownConditionException(
                condition, Commands.IF)

        if value_is_register:
            bit_field = 0x3
            cmd_word = _binencode(LEN1, Commands.IF, [
                bit_field, 16,
                register_id, 8,
                value, 4,
                condition])
            data_encoded = bytearray()
            cmd_string = "IF reg[{0:d}] {1:s} reg[{2:d}]".format(
                register_id, condition.operator, value)
        else:
            bit_field = 0x2
            cmd_word = _binencode(LEN2, Commands.IF, [
                bit_field, 16,
                register_id, 8,
                condition])
            data_encoded = bytearray(struct.pack("<i", value))
            cmd_string = "IF reg[{0:d}] {1:s} {2:d}".format(
                register_id, condition.operator, value)

        self.conditionals.append(False)

        cmd_word_list = cmd_word + data_encoded
        self.write_command_to_files(cmd_word_list, cmd_string, indent=True)

    def else_conditional(self):
        """ Insert command for the else of an if...then...else construct.\
            If the condition of the conditional evaluates to false, the\
            statements up between the conditional and the insertion of this\
            "else" are skipped, and the statements from this point until the\
            end of the conditional are executed.

        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException:\
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException:\
            If a write to external storage fails
        :raise data_specification.exceptions.\
            DataSpecificationInvalidCommandException: If there is no \
            conditional in operation at this point
        """
        if len(self.conditionals) == 0 or \
                self.conditionals[len(self.conditionals) - 1] is True:
            raise DataSpecificationInvalidCommandException(Commands.ELSE)
        self.conditionals[len(self.conditionals) - 1] = True

        cmd_word = _binencode(LEN1, Commands.ELSE)
        cmd_string = "ELSE"
        self.write_command_to_files(
            cmd_word, cmd_string, indent=True, outdent=True)

    def end_conditional(self):
        """ Insert command to mark the end of an if...then...else construct

        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException:\
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException:\
            If a write to external storage fails
        :raise data_specification.exceptions.\
            DataSpecificationInvalidCommandException: If there is no \
            conditional in operation at this point
        """
        if len(self.conditionals) == 0:
            raise DataSpecificationInvalidCommandException(Commands.END_IF)

        self.conditionals.pop()

        cmd_word = _binencode(LEN1, Commands.END_IF)
        cmd_string = "END_IF"
        self.write_command_to_files(cmd_word, cmd_string, outdent=True)

    def set_register_value(self, register_id, data, data_is_register=False,
                           data_type=DataType.UINT32):
        """ Insert command to set the value of a register

        :param register_id: The id of the register to assign, between 0 and 15
        :type register_id: int
        :param data:
            * If data_is_register is True, the register id containing\
              the data to set, between 0 and 15
            * If data_is_register is False, the data as a float
        :type data: float
        :param data_is_register: Indicates if data is a register id
        :type data_is_register: bool
        :param data_type: The type of the data to be assigned
        :type data_type: :py:class:`DataType`
        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException:\
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException:\
            If a write to external storage fails
        :raise data_specification.exceptions.\
            DataSpecificationParameterOutOfBoundsException:\
            * If register_id is not a valid register_id
            * If data_is_register is True, and data is not a valid\
              register id
            * If data_is_register is False, data_type is an integer\
              type and data has a fractional part
            * If data_is_register if False, and data would overflow the\
              data type
        :raise data_specification.exceptions.\
            DataSpecificationUnknownTypeException: If the data type is not\
            known
        """
        _bounds(Commands.MV, "register_id", register_id, 0, MAX_REGISTERS)

        if data_is_register:
            # Build command to move between registers:
            _bounds(Commands.MV, "data", data, 0, MAX_REGISTERS)
            if data == register_id:
                raise DataSpecificationDuplicateParameterException(
                    Commands.MV, [register_id, data])
            dest_reg = register_id
            src_reg = data
            cmd_word = _binencode(LEN1, Commands.MV, [
                DEST_AND_SRC1, 16,
                dest_reg, 12,
                src_reg, 8])
            cmd_word_list = cmd_word
            cmd_string = "reg[{0:d}] = reg[{1:d}]".format(dest_reg, src_reg)
        else:

            # Build command to assign from an immediate:
            # command has a second word (the immediate)
            _typebounds(Commands.MV, "data", data, data_type)

            length = LEN3 if data_type.size > 4 else LEN2
            dest_reg = register_id
            cmd_word = _binencode(length, Commands.MV, [
                DEST_ONLY, 16,
                dest_reg, 12])
            scaled_data = int(data * data_type.scale)
            encoding_string = "<{0:s}".format(data_type.struct_encoding)
            encoded_data = bytearray(struct.pack(encoding_string, scaled_data))
            while len(encoded_data) % 4:
                encoded_data += bytearray(struct.pack("<b", 0))
            cmd_word_list = cmd_word + encoded_data
            cmd_string = "reg[{0:d}] = {1:d} (0x{2:X})".format(
                dest_reg, data, data)

        self.write_command_to_files(cmd_word_list, cmd_string)

    def save_write_pointer(self, register_id):
        """ Insert command to save the write pointer to a register

        :param register_id: The id of the register to assign, between 0 and 15
        :type register_id: int
        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException:\
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException:\
            If a write to external storage fails
        :raise data_specification.exceptions.\
            DataSpecificationParameterOutOfBoundsException: If the register_id\
            is not a valid register id
        :raise data_specification.exceptions.\
            DataSpecificationNoRegionSelectedException: If no region has been \
            selected
        """
        _bounds(Commands.GET_WR_PTR, "register_id",
                register_id, 0, MAX_REGISTERS)
        if self.current_region is None:
            raise DataSpecificationNoRegionSelectedException(
                Commands.GET_WR_PTR)
        bit_field = 0x4
        cmd_word = _binencode(LEN1, Commands.GET_WR_PTR, [
            bit_field, 16,
            register_id, 12])
        cmd_string = "GET_WR_PTR reg[{0:d}]".format(register_id)
        self.write_command_to_files(cmd_word, cmd_string)

    def set_write_pointer(self, address, address_is_register=False,
                          relative_to_current=False):
        """ Insert command to set the position of the write pointer within the\
            current region

        :param address:
            * If address_is_register is True, the id of the register\
              containing the address to move to
            * If address_is_register is False, the address to move the\
              write pointer to
        :type address: int
        :param address_is_register: Indicates if the the address is a\
            register id
        :type address_is_register: bool
        :param relative_to_current: Indicates if the address is to be added to\
            the current address, or used as an absolute address from\
            the start of the current region
        :type relative_to_current: bool
        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException:\
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException:\
            If a write to external storage fails
        :raise data_specification.exceptions.\
            DataSpecificationParameterOutOfBoundsException: If the \
            address_is_register is True and address is not a valid register id
        :raise data_specification.exceptions.\
            DataSpecificationNoRegionSelectedException: If no region has been \
            selected
        """
        if self.current_region is None:
            raise DataSpecificationNoRegionSelectedException(
                Commands.SET_WR_PTR)
        if relative_to_current:
            relative = 1
            relative_string = "RELATIVE"
        else:
            relative = 0
            relative_string = "ABSOLUTE"

        if address_is_register:
            _bounds(Commands.SET_WR_PTR, "address", address, 0, MAX_REGISTERS)
            data_encoded = bytearray()
            cmd_word = _binencode(LEN1, Commands.SET_WR_PTR, [
                SRC1_ONLY, 16,
                address, 8,
                relative])
            cmd_string = "SET_WR_PTR reg[{0:d}] {1:s}".format(
                address, relative_string)
        else:
            if not relative_to_current:
                _typebounds(Commands.SET_WR_PTR, "address",
                            address, DataType.UINT32)
                data_encoded = bytearray(struct.pack("<I", address))
            else:
                _typebounds(Commands.SET_WR_PTR, "address",
                            address, DataType.INT32)
                data_encoded = bytearray(struct.pack("<i", address))

            cmd_word = _binencode(LEN2, Commands.SET_WR_PTR, [
                NO_REGS, 16,
                relative])
            cmd_string = "SET_WR_PTR {0:d} {1:s}".format(
                address, relative_string)

        self.write_command_to_files(cmd_word + data_encoded, cmd_string)

    def align_write_pointer(self, log_block_size,
                            log_block_size_is_register=False,
                            return_register_id=None):
        """ Insert command to align the write pointer against a power-of-2\
            block size in bytes.  Zeros are inserted in the intervening space

        :param log_block_size:
            * If log_block_size_is_register is False, log to base 2 of\
              the block size (e.g. The write pointer will be moved so\
              that it is a multiple of 2^(log_block_size)),\
              between 0 and 32
            * If log_block_size_is_register is True, the id of the\
              register containing log to the base 2 of the block size,\
              between 0 and 15
        :type log_block_size: int
        :param log_block_size_is_register: Indicates if log_block_size is a\
            register id
        :type log_block_size_is_register: bool
        :param return_register_id: The id of a register where the write\
            pointer will be written to once it has been updated, between\
            0 and 15or None if no such writing is to be done
        :type return_register_id: int
        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException:\
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException:\
            If a write to external storage fails
        :raise data_specification.exceptions.\
            DataSpecificationParameterOutOfBoundsException:\
            * If log_block_size_is_register is False, and\
              log_block_size is not within the allowed range
            * If log_block_size_is_register is True and log_block_size\
              is not a valid register id
        :raise data_specification.exceptions.\
            DataSpecificationRegionOutOfBoundsException:\
            If the move of the pointer would put it outside of the\
            current region
        :raise data_specification.exceptions.\
            DataSpecificationNoRegionSelectedException: If no region has been \
            selected
        """
        bit_field = 0
        imm_value = 0
        return_register_value = 0
        block_size_reg = 0
        cmd_string = "ALIGN_WR_PTR"

        if self.current_region is None:
            raise DataSpecificationNoRegionSelectedException(
                Commands.ALIGN_WR_PTR)

        if return_register_id is not None:
            _bounds(Commands.ALIGN_WR_PTR, "return_register_id",
                    return_register_id, 0, MAX_REGISTERS)
            bit_field |= 0x4
            return_register_value = return_register_id
            cmd_string = " reg[{0:d}] =".format(return_register_value)

        if log_block_size_is_register:
            _bounds(Commands.ALIGN_WR_PTR, "log_block_size",
                    log_block_size, 0, MAX_REGISTERS)
            bit_field |= 0x2
            block_size_reg = log_block_size
            cmd_string += " align(reg[{0:d}])".format(block_size_reg)
        else:
            _bounds(Commands.ALIGN_WR_PTR, "log_block_size",
                    log_block_size, 0, 32)
            imm_value = log_block_size
            cmd_string += " align({0:d})".format(imm_value)

        cmd_word = _binencode(LEN1, Commands.ALIGN_WR_PTR, [
            bit_field, 16,
            return_register_value, 12,
            block_size_reg, 8,
            imm_value])
        self.write_command_to_files(cmd_word, cmd_string)

    def call_arithmetic_operation(self, register_id, operand_1, operation,
                                  operand_2, signed,
                                  operand_1_is_register=False,
                                  operand_2_is_register=False):
        """ Insert command to perform an arithmetic operation on two signed or\
            unsigned values and store the result in a register

        :param register_id: The id of the register to store the result in
        :type register_id: int
        :param operand_1:
            * If operand_1_is_register is True, the id of a register\
              where the first operand can be found, between 0 and 15
            * If operand_1_is_register is False, a 32-bit value
        :type operand_1: int
        :param operation: The operation to perform
        :type operation: :py:class:`ArithmeticOperation`
        :param operand_2:
            * If operand_2_is_register is True, the id of a register\
              where the second operand can be found, between 0 and 15
            * If operand_2_is_register is False, a 32-bit value
        :type operand_2: int
        :param signed: Indicates if the values should be considered signed
        :type signed: bool
        :param operand_1_is_register: Indicates if operand_1 is a register id
        :type operand_1_is_register: bool
        :param operand_2_is_register: Indicates if operand_2 is a register id
        :type operand_2_is_register: bool
        :raise data_specification.exceptions.DataUndefinedWriterException:\
            If the binary specification file writer has not been\
            initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException:\
            If a write to external storage fails
        :raise data_specification.exceptions.\
            DataSpecificationParameterOutOfBoundsException:\
            * If operand_1_is_register is True and operand_1 is not a\
              valid register id
            * If operand_2_is_register is True and operand_2 is not a\
              valid register id
        :raise data_specification.exceptions.\
            DataSpecificationUnknownTypeException: If operation is not a known\
            operation
        """
        cmd_length = 0
        bit_field = 0x4
        register_op_1 = 0
        register_op_2 = 0
        cmd_string = "ARTIH_OP"

        signed_value = 0
        if signed:
            signed_value = 1
            cmd_string += " SIGNED"
        else:
            cmd_string += " UNSIGNED"

        _bounds(Commands.ARITH_OP, "register_id",
                register_id, 0, MAX_REGISTERS)

        cmd_string += " reg[{0:d}] =".format(register_id)

        if operand_1_is_register:
            _bounds(Commands.ARITH_OP, "operand_1",
                    operand_1, 0, MAX_REGISTERS)
            bit_field |= 2
            register_op_1 = operand_1
            operand_1_encoded = bytearray()
            cmd_string += " reg[{0:d}]".format(register_op_1)
        elif signed:
            _typebounds(Commands.ARITH_OP, "operand_1",
                        operand_1, DataType.INT32)
            cmd_length += 1
            operand_1_encoded = bytearray(struct.pack("<i", operand_1))
            cmd_string += " {0:d}".format(operand_1)
        else:
            _typebounds(Commands.ARITH_OP, "operand_1",
                        operand_1, DataType.UINT32)
            cmd_length += 1
            operand_1_encoded = bytearray(struct.pack("<I", operand_1))
            cmd_string += " {0:d}".format(operand_1)

        if operation not in ArithmeticOperation:
            raise DataSpecificationInvalidOperationException(
                "arithmetic", operation.value, Commands.ARITH_OP)
        cmd_string += " {0:s}".format(operation.operator)

        if operand_2_is_register:
            _bounds(Commands.ARITH_OP, "operand_2",
                    operand_2, 0, MAX_REGISTERS)
            bit_field |= 1
            register_op_2 = operand_2
            operand_2_encoded = bytearray()
            cmd_string += " reg[{0:d}]".format(register_op_2)
        elif signed:
            _typebounds(Commands.ARITH_OP, "operand_2",
                        operand_2, DataType.INT32)
            cmd_length += 1
            operand_2_encoded = bytearray(struct.pack("<i", operand_2))
            cmd_string += " {0:d}".format(operand_2)
        else:
            _typebounds(Commands.ARITH_OP, "operand_2",
                        operand_2, DataType.UINT32)
            cmd_length += 1
            operand_2_encoded = bytearray(struct.pack("<I", operand_2))
            cmd_string += " {0:d}".format(operand_2)

        cmd_word = _binencode(cmd_length, Commands.ARITH_OP, [
            signed_value, 19,
            bit_field, 16,
            register_id, 12,
            register_op_1, 8,
            register_op_2, 4,
            operation])
        cmd_word_list = cmd_word + operand_1_encoded + operand_2_encoded
        self.write_command_to_files(cmd_word_list, cmd_string)

    def logical_and(self, register_id, operand_1, operand_2,
                    operand_1_is_register=False, operand_2_is_register=False):
        """ Insert command to perform a logical AND operation, using the\
             _call_logic_operation.

        :param register_id: The id of the register to store the result in
        :type register_id: int
        :param operand_1:
            * If operand_1_is_register is True, the id of a register\
              where the first operand can be found, between 0 and 15
            * If operand_1_is_register is False, a 32-bit value
        :type operand_1: int
        :param operand_2:
            * If operand_2_is_register is True, the id of a register\
              where the second operand can be found. between 0 and 15
            * If operand_2_is_register is False, a 32-bit value
        :type operand_2: int
        :param operand_1_is_register: Indicates if operand_1 is a register id
        :type operand_1_is_register: bool
        :param operand_2_is_register: Indicates if operand_2 is a register id
        :type operand_2_is_register: bool
        :raise data_specification.exceptions.DataUndefinedWriterException:\
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException:\
            If a write to external storage fails
        :raise data_specification.exceptions.\
            DataSpecificationParameterOutOfBoundsException:\
            * If operand_1_is_register is True and operand_1 is not a\
              valid register id
            * If operand_2_is_register is True and operand_2 is not a\
              valid register id
        """
        self._call_logic_operation(
            register_id, operand_1, LogicOperation.AND, operand_2,
            operand_1_is_register, operand_2_is_register)

    def logical_or(self, register_id, operand_1, operand_2,
                   operand_1_is_register=False, operand_2_is_register=False):
        """ Insert command to perform a logical OR operation, using the\
            _call_logic_operation.

        :param register_id: The id of the register to store the result in
        :type register_id: int
        :param operand_1:
            * If operand_1_is_register is True, the id of a register\
              where the first operand can be found, between 0 and 15
            * If operand_1_is_register is False, a 32-bit value
        :type operand_1: int
        :param operand_2:
            * If operand_2_is_register is True, the id of a register\
              where the second operand can be found. between 0 and 15
            * If operand_2_is_register is False, a 32-bit value
        :type operand_2: int
        :param operand_1_is_register: Indicates if operand_1 is a register id
        :type operand_1_is_register: bool
        :param operand_2_is_register: Indicates if operand_2 is a register id
        :type operand_2_is_register: bool
        :raise data_specification.exceptions.DataUndefinedWriterException:\
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException:\
            If a write to external storage fails
        :raise data_specification.exceptions.\
            DataSpecificationParameterOutOfBoundsException:\
            * If operand_1_is_register is True and operand_1 is not a\
              valid register id
            * If operand_2_is_register is True and operand_2 is not a\
              valid register id
        """
        self._call_logic_operation(
            register_id, operand_1, LogicOperation.OR, operand_2,
            operand_1_is_register, operand_2_is_register)

    def logical_left_shift(self, register_id, operand_1, operand_2,
                           operand_1_is_register=False,
                           operand_2_is_register=False):
        """ Insert command to perform a logical left shift operation, using\
            the _call_logic_operation.

        :param register_id: The id of the register to store the result in
        :type register_id: int
        :param operand_1:
            * If operand_1_is_register is True, the id of a register\
              where the first operand can be found, between 0 and 15
            * If operand_1_is_register is False, a 32-bit value
        :type operand_1: int
        :param operand_2:
            * If operand_2_is_register is True, the id of a register\
              where the second operand can be found. between 0 and 15
            * If operand_2_is_register is False, a 32-bit value
        :type operand_2: int
        :param operand_1_is_register: Indicates if operand_1 is a register id
        :type operand_1_is_register: bool
        :param operand_2_is_register: Indicates if operand_2 is a register id
        :type operand_2_is_register: bool
        :raise data_specification.exceptions.DataUndefinedWriterException:\
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException:\
            If a write to external storage fails
        :raise data_specification.exceptions.\
            DataSpecificationParameterOutOfBoundsException:\
            * If operand_1_is_register is True and operand_1 is not a\
              valid register id
            * If operand_2_is_register is True and operand_2 is not a\
              valid register id
        """
        self._call_logic_operation(
            register_id, operand_1, LogicOperation.LEFT_SHIFT, operand_2,
            operand_1_is_register, operand_2_is_register)

    def logical_right_shift(self, register_id, operand_1, operand_2,
                            operand_1_is_register=False,
                            operand_2_is_register=False):
        """ Insert command to perform a logical right shift operation, using\
            the _call_logic_operation.

        :param register_id: The id of the register to store the result in
        :type register_id: int
        :param operand_1:
            * If operand_1_is_register is True, the id of a register\
              where the first operand can be found, between 0 and 15
            * If operand_1_is_register is False, a 32-bit value
        :type operand_1: int
        :param operand_2:
            * If operand_2_is_register is True, the id of a register\
              where the second operand can be found. between 0 and 15
            * If operand_2_is_register is False, a 32-bit value
        :type operand_2: int
        :param operand_1_is_register: Indicates if operand_1 is a register id
        :type operand_1_is_register: bool
        :param operand_2_is_register: Indicates if operand_2 is a register id
        :type operand_2_is_register: bool
        :raise data_specification.exceptions.DataUndefinedWriterException:\
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException:\
            If a write to external storage fails
        :raise data_specification.exceptions.\
            DataSpecificationParameterOutOfBoundsException:\
            * If operand_1_is_register is True and operand_1 is not a\
              valid register id
            * If operand_2_is_register is True and operand_2 is not a\
              valid register id
        """
        self._call_logic_operation(
            register_id, operand_1, LogicOperation.RIGHT_SHIFT, operand_2,
            operand_1_is_register, operand_2_is_register)

    def logical_xor(self, register_id, operand_1, operand_2,
                    operand_1_is_register=False, operand_2_is_register=False):
        """ Insert command to perform a logical xor operation, using
            the _call_logic_operation.

        :param register_id: The id of the register to store the result in
        :type register_id: int
        :param operand_1:
            * If operand_1_is_register is True, the id of a register\
              where the first operand can be found, between 0 and 15
            * If operand_1_is_register is False, a 32-bit value
        :type operand_1: int
        :param operand_2:
            * If operand_2_is_register is True, the id of a register\
              where the second operand can be found. between 0 and 15
            * If operand_2_is_register is False, a 32-bit value
        :type operand_2: int
        :param operand_1_is_register: Indicates if operand_1 is a register id
        :type operand_1_is_register: bool
        :param operand_2_is_register: Indicates if operand_2 is a register id
        :type operand_2_is_register: bool
        :raise data_specification.exceptions.DataUndefinedWriterException:\
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException:\
            If a write to external storage fails
        :raise data_specification.exceptions.\
            DataSpecificationParameterOutOfBoundsException:\
            * If operand_1_is_register is True and operand_1 is not a\
              valid register id
            * If operand_2_is_register is True and operand_2 is not a\
              valid register id
        """
        self._call_logic_operation(
            register_id, operand_1, LogicOperation.XOR, operand_2,
            operand_1_is_register, operand_2_is_register)

    def logical_not(self, register_id, operand, operand_is_register=False):
        """ Insert command to perform a logical xor operation, using
            the _call_logic_operation.

        :param register_id: The id of the register to store the result in
        :type register_id: int
        :param operand:
            * If operand_is_register is True, the id of a register\
              where the first operand can be found, between 0 and 15
            * If operand_is_register is False, a 32-bit value
        :type operand: int
        :param operand_is_register: Indicates if operand_1 is a register id
        :type operand_is_register: bool
        :raise data_specification.exceptions.DataUndefinedWriterException:\
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException:\
            If a write to external storage fails
        :raise data_specification.exceptions.\
            DataSpecificationParameterOutOfBoundsException:\
            * If operand_is_register is True and operand_1 is not a\
              valid register id
        """
        self._call_logic_operation(
            register_id, operand, LogicOperation.NOT, 0,
            operand_is_register, False)

    def _call_logic_operation(self, register_id, operand_1, operation,
                              operand_2, operand_1_is_register=False,
                              operand_2_is_register=False):
        """ Insert command to perform a logic operation on two signed or\
            unsigned values and store the result in a register

        :param register_id: The id of the register to store the result in
        :type register_id: int
        :param operand_1:
            * If operand_1_is_register is True, the id of a register\
              where the first operand can be found, between 0 and 15
            * If operand_1_is_register is False, a 32-bit value
        :type operand_1: int
        :param operation: The operation to perform
        :type operation: :py:class:`LogicOperation`
        :param operand_2:
            * If operand_2_is_register is True, the id of a register\
              where the second operand can be found. between 0 and 15
            * If operand_2_is_register is False, a 32-bit value
        :type operand_2: int
        :param operand_1_is_register: Indicates if operand_1 is a register id
        :type operand_1_is_register: bool
        :param operand_2_is_register: Indicates if operand_2 is a register id
        :type operand_2_is_register: bool
        :raise data_specification.exceptions.DataUndefinedWriterException:\
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException:\
            If a write to external storage fails
        :raise data_specification.exceptions.\
            DataSpecificationParameterOutOfBoundsException:\
            * If operand_1_is_register is True and operand_1 is not a\
              valid register id
            * If operand_2_is_register is True and operand_2 is not a\
              valid register id
        :raise data_specification.exceptions.\
            DataSpecificationInvalidOperationException: If operation is not a\
            known operation
        """
        cmd_length = 0
        bit_field = 0x4
        register_op_1 = 0
        register_op_2 = 0
        operand_2_encoded = bytearray()
        cmd_string = "LOGIC_OP"

        _bounds(Commands.LOGIC_OP, "register_id",
                register_id, 0, MAX_REGISTERS)

        cmd_string += " reg[{0:d}] =".format(register_id)

        if operation not in LogicOperation:
            raise DataSpecificationInvalidOperationException(
                "logic", operation.value, Commands.LOGIC_OP)

        if operation.value == LogicOperation.NOT.value:  # @UndefinedVariable
            cmd_string += " {0:s}".format(operation.operator)

        if operand_1_is_register:
            _bounds(Commands.LOGIC_OP, "operand_1",
                    operand_1, 0, MAX_REGISTERS)
            bit_field |= 2
            register_op_1 = operand_1
            operand_1_encoded = bytearray()
            cmd_string += " reg[{0:d}]".format(register_op_1)
        else:
            cmd_length += 1
            _typebounds(Commands.LOGIC_OP, "operand_1",
                        operand_1, DataType.UINT32)
            operand_1_encoded = bytearray(struct.pack("<I", operand_1))
            cmd_string += " {0:d}".format(operand_1)

        if operation.value != LogicOperation.NOT.value:  # @UndefinedVariable
            cmd_string += " {0:s}".format(operation.operator)

            if operand_2_is_register:
                _bounds(Commands.LOGIC_OP, "operand_2",
                        operand_2, 0, MAX_REGISTERS)
                bit_field |= 1
                register_op_2 = operand_2
                cmd_string += " reg[{0:d}]".format(register_op_2)
            else:
                cmd_length += 1
                _typebounds(Commands.LOGIC_OP, "operand_2",
                            operand_2, DataType.UINT32)
                operand_2_encoded = bytearray(struct.pack("<I", operand_2))
                cmd_string += " {0:d}".format(operand_2)

        cmd_word = _binencode(cmd_length, Commands.LOGIC_OP, [
            bit_field, 16,
            register_id, 12,
            register_op_1, 8,
            register_op_2, 4,
            operation])
        cmd_word_list = cmd_word + operand_1_encoded + operand_2_encoded
        self.write_command_to_files(cmd_word_list, cmd_string)

    def copy_structure(self, source_structure_id, destination_structure_id,
                       source_id_is_register=False,
                       destination_id_is_register=False):
        """ Insert command to copy a structure, possibly overwriting another\
            structure

        :param source_structure_id:
            * If source_id_is_register is True, the id of the register
              holding the source structure id, between 0 and 15
            * Otherwise, the id of the source structure, between\
              0 and 15
        :type source_structure_id: int
        :param destination_structure_id:
            * If destination_id_is_register is True, the id of the\
              register holding the destination structure id, between\
              0 and 15
            * If destination_id_is_register is False, the id of the\
              destination structure, between 0 and 15
        :type destination_structure_id: int
        :param source_id_is_register: Indicates if source_structure_id is a\
            register id
        :type source_id_is_register: bool
        :param destination_id_is_register: Indicates if\
            destination_structure_id is a register id
        :type destination_id_is_register: bool
        :return: The id of the copied structure, between 0 and 15
        :rtype: int
        :raise data_specification.exceptions.DataUndefinedWriterException:\
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException:\
            If a write to external storage fails
        :raise data_specification.exceptions.\
            DataSpecificationParameterOutOfBoundsException:\
            * If source_id_is_register is True and source_structure_id\
              is not a valid register id
            * If destination_id_is_register is True and\
              destination_structure_id is not a valid register id
            * If source_id_is_register is False and source_structure_id\
              is not a valid structure id
            * If destination_id_is_register is False and\
              destination_structure_id is not a valid structure id
        :raise data_specification.exceptions.\
            DataSpecificationNotAllocatedException:\
            * If no structure with id source_structure_id has been\
              allocated
        """
        bit_field = 0
        cmd_string = "COPY_STRUCT"

        if source_structure_id == destination_structure_id and \
                destination_id_is_register == source_id_is_register:
            raise DataSpecificationDuplicateParameterException(
                Commands.COPY_STRUCT,
                [source_structure_id, destination_structure_id])

        if source_id_is_register:
            _bounds(Commands.COPY_STRUCT, "source_structure_id",
                    source_structure_id, 0, MAX_REGISTERS)
            bit_field |= SRC1_ONLY
            cmd_string += " source_struct=reg[{0:d}]".format(
                source_structure_id)
        else:
            _bounds(Commands.COPY_STRUCT, "source_structure_id",
                    source_structure_id, 0, MAX_STRUCT_SLOTS)
            if self.struct_slot[source_structure_id] == 0:
                raise DataSpecificationNotAllocatedException(
                    "struct", source_structure_id, Commands.COPY_STRUCT)
            cmd_string += " source_struct={0:d}".format(
                source_structure_id)

        if destination_id_is_register:
            _bounds(Commands.COPY_STRUCT, "destination_structure_id",
                    destination_structure_id, 0, MAX_REGISTERS)
            bit_field |= DEST_ONLY
            cmd_string += " destination_struct=reg[{0:d}]".format(
                destination_structure_id)
        else:
            _bounds(Commands.COPY_STRUCT, "destination_structure_id",
                    destination_structure_id, 0, MAX_STRUCT_SLOTS)
            cmd_string += " destination_struct={0:d}".format(
                destination_structure_id)

        cmd_word = _binencode(LEN1, Commands.COPY_STRUCT, [
            bit_field, 16,
            destination_structure_id, 12,
            source_structure_id, 8])
        self.write_command_to_files(cmd_word, cmd_string)

    def copy_structure_parameter(self, source_structure_id,
                                 source_parameter_index,
                                 destination_id,
                                 destination_parameter_index=None,
                                 destination_is_register=False):
        """ Insert command to copy the value of a parameter from one structure
        to another

        :param source_structure_id: The id of the source structure,\
            between 0 and 15
        :type source_structure_id: int
        :param source_parameter_index: The index of the parameter in the\
            source structure
        :type source_parameter_index: int
        :param destination_id: The id of the destination structure, or the
            id of the destination register, between 0 and 15
        :type destination_id: int
        :param destination_parameter_index: The index of the parameter in the\
            destination structure. Ignored when writing to a register.
        :type destination_parameter_index: int
        :return: Nothing is returned
        :param destination_is_register: Indicates whether the destination is
                                        a structure or a register.
        :type destination_is_register: boolean
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException:\
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException:\
            If a write to external storage fails
        :raise data_specification.exceptions.\
            DataSpecificationParameterOutOfBoundsException:\
            * If source_structure_id is not a valid structure id
            * If destination_id is not a valid structure id
            * If source_parameter_index is not a valid parameter index\
              in the source structure
            * If destination_parameter_index is not a valid parameter\
              index in the destination structure
        :raise data_specification.exceptions.\
            DataSpecificationNotAllocatedException:\
            * If no structure with id destination_id has been\
              allocated
            * If no structure with id source_structure_id has been
              allocated
        """
        _bounds(Commands.COPY_PARAM, "source_structure_id",
                source_structure_id, 0, MAX_STRUCT_SLOTS)
        _bounds(Commands.COPY_PARAM, "source_parameter_index",
                source_parameter_index, 0, MAX_STRUCT_ELEMENTS)
        if self.struct_slot[source_structure_id] == 0:
            raise DataSpecificationNotAllocatedException(
                "structure", source_structure_id, Commands.COPY_PARAM)
        if (len(self.struct_slot[source_structure_id]) <=
                source_parameter_index):
            raise DataSpecificationNotAllocatedException(
                "parameter", source_parameter_index, Commands.COPY_PARAM)

        if not destination_is_register:
            _bounds(Commands.COPY_PARAM, "destination_parameter_index",
                    destination_parameter_index, 0, MAX_STRUCT_ELEMENTS)
            _bounds(Commands.COPY_PARAM, "destination_structure_id",
                    destination_id, 0, MAX_STRUCT_SLOTS)
            if self.struct_slot[destination_id] == 0:
                raise DataSpecificationNotAllocatedException(
                    "structure", destination_id, Commands.COPY_PARAM)
            if (len(self.struct_slot[source_structure_id]) <=
                    source_parameter_index):
                raise DataSpecificationNotAllocatedException(
                    "parameter", destination_parameter_index,
                    Commands.COPY_PARAM)
            if (len(self.struct_slot[destination_id]) <=
                    destination_parameter_index):
                raise DataSpecificationNotAllocatedException(
                    "parameter", destination_parameter_index,
                    Commands.COPY_PARAM)
            if (self.struct_slot[source_structure_id]
                    [source_parameter_index][1] !=
                    self.struct_slot[destination_id]
                    [destination_parameter_index][1]):
                raise DataSpecificationTypeMismatchException(
                    Commands.COPY_PARAM)
            if (source_structure_id == destination_id and
                    destination_parameter_index == source_parameter_index):
                raise DataSpecificationDuplicateParameterException(
                    Commands.COPY_PARAM, [
                        source_structure_id, source_parameter_index,
                        destination_id, destination_parameter_index])

            cmd_word_1 = _binencode(LEN2, Commands.COPY_PARAM, [
                NO_REGS, 16,
                destination_id, 12,
                source_structure_id, 8])
            cmd_word_2 = ((destination_parameter_index << 8) |
                          source_parameter_index)
            cmd_string = (
                "COPY_PARAM source_structure_id = {0:d}, "
                "source_parameter_id = {1:d}, "
                "destination_structure_id = {2:d}, "
                "destination_parameter_id = {3:d}".format(
                    source_structure_id, source_parameter_index,
                    destination_id, destination_parameter_index))
        else:
            _bounds(Commands.COPY_PARAM, "destination_register_id",
                    destination_id, 0, MAX_REGISTERS)

            cmd_word_1 = _binencode(LEN2, Commands.COPY_PARAM, [
                DEST_ONLY, 16,
                destination_id, 12,
                source_structure_id, 8])
            cmd_word_2 = source_parameter_index
            cmd_string = "WRITE_PARAM source_structure_id = {0:d}, " \
                         "source_parameter_id = {1:d}, " \
                         "destination_register_id = {2:d}".format(
                             source_structure_id, source_parameter_index,
                             destination_id)

        cmd_word_list = cmd_word_1 + bytearray(struct.pack("<I", cmd_word_2))
        self.write_command_to_files(cmd_word_list, cmd_string)

    def print_value(self, value, value_is_register=False,
                    data_type=DataType.UINT32):
        """ Insert command to print out a value (for debugging)

        :param value:
            * If value_is_register is True, the id of the register\
              containing the value to print
            * If value_is_register is False, the value to print as a\
              float
        :type value: float
        :param value_is_register: Indicates if the value is a register
        :type value_is_register: bool
        :param data_type: The type of the data to be printed
        :type data_type: :py:class:`DataType`
        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException:\
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException:\
            If a write to external storage fails
        :raise data_specification.exceptions.\
            DataSpecificationParameterOutOfBoundsException:\
            * If value_is_register is True and value is not a valid\
              register id
            * If value_is_register is False, the data_type is an
              integer type and value has a fractional part
            * If value_is_register is False and the value would
              overflow the data type
        :raise data_specification.exceptions.\
            DataSpecificationUnknownTypeException:\
            * If data_type is not a valid data type
        """
        cmd_word_length = LEN1
        source_register_id = 0
        bit_field = 0
        data_encoded = bytearray()

        if value_is_register:
            _bounds(Commands.PRINT_VAL, "value", value, 0, MAX_REGISTERS)
            bit_field |= 2
            source_register_id = value
            cmd_string = "PRINT_VAL reg[{0:d}]".format(source_register_id)
        else:
            _typebounds(Commands.PRINT_VAL, "value", value, data_type)
            if data_type.size <= 4:
                cmd_word_length = LEN2
            else:
                cmd_word_length = LEN3
            data_encoding_string = "<{0:s}".format(data_type.struct_encoding)
            data_encoded = bytearray(struct.pack(data_encoding_string, value))
            while len(data_encoded) % 4:
                data_encoded += bytearray(struct.pack("<b", 0))
            cmd_string = "PRINT_VAL {0:d}".format(value)

        cmd_word = _binencode(cmd_word_length, Commands.PRINT_VAL, [
            bit_field, 16,
            source_register_id, 8,
            data_type])
        self.write_command_to_files(cmd_word + data_encoded, cmd_string)

    def print_text(self, text):
        """ Insert command to print some text (for debugging)

        :param text: The text to write (max 12 characters)
        :type text: str
        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException:\
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException:\
            If a write to external storage fails
        """
        text_len = len(text)
        _bounds(Commands.PRINT_TXT, "len(text)", text_len, 1, 13)

        if text_len <= 4:
            cmd_word_len = LEN2
        elif text_len <= 8:
            cmd_word_len = LEN3
        else:
            cmd_word_len = LEN4

        text_encoded = bytearray(text)
        # add final padding to the encoded text
        if text_len % 4 is not 0:
            text_encoded += bytearray(4 - (text_len % 4))

        cmd_string = "PRINT_TXT \"{0:s}\"".format(text)
        cmd_word = _binencode(cmd_word_len, Commands.PRINT_TXT, [
            text_len - 1])
        self.write_command_to_files(cmd_word + text_encoded, cmd_string)

    def print_struct(self, structure_id, structure_id_is_register=False):
        """ Insert command to print out a structure (for debugging)

        :param structure_id:
            * If structure_id_is_register is True, the id of the\
              register containing the id of the structure to print,\
              between 0 and 15
            * If structure_id_is_register is False, the id of the\
              structure to print, between 0 and 15
        :type structure_id: int
        :param structure_id_is_register: Indicates if the structure_id is a\
            register
        :type structure_id_is_register: bool
        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException:\
            If the binary specification file writer has not been\
            initialised
        :raise data_specification.exceptions.\
            DataSpecificationParameterOutOfBoundsException:\
            * If structure_id_is_register is True and structure_id is\
              not a valid register id
            * If structure_id_is_register is False and structure_id is\
              not a valid structure id
        :raise data_specification.exceptions.\
            DataSpecificationNotAllocatedException: If \
            structure_id_is_register is False and structure_id is the id of a \
            structure that has not been allocated
        """
        if structure_id_is_register:
            _bounds(Commands.PRINT_STRUCT, "structure_id",
                    structure_id, 0, MAX_REGISTERS)
            struct_register = structure_id
            structure_id = 0
            bit_field = 0x2
            cmd_string = "PRINT_STRUCT struct(reg[{0:d}])".format(
                struct_register)
        else:
            _bounds(Commands.PRINT_STRUCT, "structure_id",
                    structure_id, 0, MAX_STRUCT_SLOTS)
            if self.struct_slot[structure_id] == 0:
                raise DataSpecificationNotAllocatedException(
                    "structure", structure_id, Commands.PRINT_STRUCT)
            struct_register = 0
            bit_field = 0
            cmd_string = "PRINT_STRUCT struct({0:d})".format(structure_id)

        cmd_word = _binencode(LEN1, Commands.PRINT_STRUCT, [
            bit_field, 16,
            struct_register, 8,
            structure_id])
        self.write_command_to_files(cmd_word, cmd_string)

    def end_specification(self, close_writer=True):
        """ Insert a command to indicate that the specification has finished\
            and finish writing

        :param close_writer: Indicates whether to close the underlying\
            writer(s)
        :type close_writer: bool
        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException:\
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException:\
            If a write to external storage fails
        """
        self.comment("\nEnd of specification:")

        cmd_word = _binencode(LEN1, Commands.END_SPEC)
        parameter = -1
        encoded_parameter = struct.pack("<i", parameter)
        cmd_string = "END_SPEC"
        self.write_command_to_files(cmd_word + encoded_parameter, cmd_string)

        if close_writer:
            self.spec_writer.close()
            if self.report_writer is not None:
                self.report_writer.close()

    def write_command_to_files(self, cmd_word_list, cmd_string, indent=False,
                               outdent=False, no_instruction_number=False):
        """ Writes the binary command to the binary output file and, if the\
            user has requested a text output for debug purposes, also write\
            the text version to the text file.\
            Setting the optional parameter 'indent' to True causes subsequent\
            commands to be indented by two spaces relative to this one.\
            Similarly, setting 'outdent' to True, reverses this spacing.

        :param cmd_word_list: list of binary words to be added to the binary\
            data specification file
        :type cmd_word_list: bytearray
        :param cmd_string: string describing the command to be added to the\
            report for the data specification file
        :type cmd_string: str
        :param indent: if the following lines need to be indented
        :type indent: bool
        :param outdent: if the following lines need to be out-dented
        :type outdent: bool
        :param no_instruction_number: if each report line should include also\
            the address of the command in the file
        :param no_instruction_number: bool
        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException:\
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException:\
            If a write to external storage fails
        """

        if self.spec_writer is None:
            raise DataUndefinedWriterException(
                "The spec file writer has not been initialised")
        elif len(cmd_word_list) > 0:
            self.spec_writer.write(cmd_word_list)

        if self.report_writer is not None:
            if outdent is True:
                self.txt_indent -= 1
                if self.txt_indent < 0:
                    self.txt_indent = 0
            if no_instruction_number is True:
                formatted_cmd_string = "{0:s}{1:s}\n".format(
                    "   " * self.txt_indent, cmd_string)
            else:
                formatted_cmd_string = "%8.8X. %s%s\n" % (
                    self.instruction_counter,
                    "   " * self.txt_indent,
                    cmd_string)
                self.instruction_counter += len(cmd_word_list)
            self.report_writer.write(formatted_cmd_string)
            if indent is True:
                self.txt_indent += 1
        return

    @property
    def region_sizes(self):
        """ A list of sizes of each region that has been reserved.  Note that\
            the list will include 0s for each non-reserved region.
        """
        return [
            self.mem_slot[i] if self.mem_slot[i] == 0 else self.mem_slot[i][0]
            for i in range(len(self.mem_slot))
        ]
