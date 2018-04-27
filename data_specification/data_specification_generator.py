import logging
import struct
import decimal

from data_specification.constants import \
    MAX_CONSTRUCTORS, MAX_MEM_REGIONS, MAX_RANDOM_DISTS, MAX_REGISTERS, \
    MAX_RNGS, MAX_STRUCT_ELEMENTS, MAX_STRUCT_SLOTS, LEN1, LEN2, LEN3, LEN4, \
    NO_REGS, DEST_AND_SRC1, DEST_ONLY, SRC1_ONLY, SRC1_AND_SRC2
from data_specification.exceptions import \
    DataUndefinedWriterException, DuplicateParameterException, \
    FunctionInUseException, InvalidCommandException, \
    InvalidOperationException, InvalidSizeException, NotAllocatedException, \
    NoRegionSelectedException, ParameterOutOfBoundsException, \
    RandomNumberDistributionInUseException, RegionInUseException, \
    RegionUnfilledException, RNGInUseException, StructureInUseException, \
    TypeMismatchException, UnknownConditionException, UnknownTypeException, \
    UnknownTypeLengthException, WrongParameterNumberException
from data_specification.enums import \
    DataType, RandomNumberGenerator, Commands, Condition, LogicOperation, \
    ArithmeticOperation
from spinn_machine import sdram
import numpy
from spinn_storage_handlers.abstract_classes import AbstractDataWriter

logger = logging.getLogger(__name__)
_ONE_SBYTE = struct.Struct("<b")
_ONE_WORD = struct.Struct("<I")
_ONE_SINT = struct.Struct("<i")
_TWO_WORDS = struct.Struct("<II")


def _rescale(data, data_type):
    data_value = decimal.Decimal(str(data)) * data_type.scale
    return int(data_value.to_integral_value())


class DataSpecificationGenerator(object):
    """ Used to generate a SpiNNaker data specification language file that\
        can be executed to produce a memory image
    """
    # pylint: disable=too-many-arguments

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
        :type spec_writer: \
            :py:class:`~spinn_storage_handlers.abstract_classes.AbstractDataWriter`
        :param report_writer: \
            Determines if a text version of the specification is to be\
            written and, if so, where. No report is written if this is None.
        :type report_writer: \
            :py:class:`~spinn_storage_handlers.abstract_classes.AbstractDataWriter`
        """
        if not isinstance(spec_writer, AbstractDataWriter):
            raise TypeError("spec_writer must be an AbstractDataWriter")
        self.spec_writer = spec_writer
        if report_writer is not None and not isinstance(
                report_writer, AbstractDataWriter):
            raise TypeError(
                "report_writer must be an AbstractDataWriter or None")
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
        :raise data_specification.exceptions.DataUndefinedWriterException: \
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException: \
            If a write to external storage fails
        """
        self.write_command_to_files(
            bytearray(), comment, no_instruction_number=True)

    def define_break(self):
        """ Insert command to stop execution with an exception (for debugging)

        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException: \
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException: \
            If a write to external storage fails
        """
        cmd_word = (
            (LEN1 << 28) |
            (Commands.BREAK.value << 20))
        encoded_cmd_word = bytearray(_ONE_WORD.pack(cmd_word))
        cmd_word_list = encoded_cmd_word
        cmd_string = "BREAK"
        self.write_command_to_files(cmd_word_list, cmd_string)

    def no_operation(self):
        """ Insert command to execute nothing

        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException: \
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException: \
            If a write to external storage fails
        """
        cmd_word = (
            (LEN1 << 28) |
            (Commands.NOP.value << 20))
        encoded_cmd_word = bytearray(_ONE_WORD.pack(cmd_word))
        cmd_word_list = encoded_cmd_word
        cmd_string = "NOP"
        self.write_command_to_files(cmd_word_list, cmd_string)
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
        :raise data_specification.exceptions.DataUndefinedWriterException: \
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException: \
            If a write to external storage fails
        :raise data_specification.exceptions.RegionInUseException: \
            If the region was already reserved
        :raise data_specification.exceptions.ParameterOutOfBoundsException: \
            If the region requested was out of the allowed range, or that the\
            size was too big to fit in SDRAM
        """
        if region < 0 or region >= MAX_MEM_REGIONS:
            logger.error(
                "Error: Memory region requested ({0:d}) is out of range 0 "
                "to {1:d}.\n".format(region, MAX_MEM_REGIONS - 1))
            raise ParameterOutOfBoundsException(
                "memory region identifier", region, 0,
                MAX_MEM_REGIONS - 1, Commands.RESERVE.name)

        if self.mem_slot[region] != 0:
            error_string = "Error: Requested memory region ({0:d}) ".format(
                region)
            error_string += "is already allocated.\n"
            logger.error(error_string)
            raise RegionInUseException(region)

        if size > sdram.SDRAM.DEFAULT_SDRAM_BYTES:
            raise ParameterOutOfBoundsException(
                "memory size", size, 1, sdram.SDRAM.DEFAULT_SDRAM_BYTES,
                Commands.RESERVE.name)

        self.mem_slot[region] = [size, label, empty]

        cmd_word = ((LEN2 << 28) |
                    (Commands.RESERVE.value << 20) |
                    (NO_REGS << 16) |
                    (int(bool(empty)) << 7) |
                    (int(bool(shrink)) << 6) |
                    region)
        cmd_word_list = bytearray(_TWO_WORDS.pack(cmd_word, size))

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
        :raise data_specification.exceptions.DataUndefinedWriterException: \
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException: \
            If a write to external storage fails
        :raise data_specification.exceptions.NotAllocatedException: \
            If the region was not reserved
        :raise data_specification.exceptions.ParameterOutOfBoundsException: \
            If the region requested was out of the allowed range
        """
        if region < 0 or region >= MAX_MEM_REGIONS:
            raise ParameterOutOfBoundsException(
                "memory region identifier", region, 0,
                MAX_MEM_REGIONS - 1, Commands.RESERVE.name)
        if self.mem_slot[region] == 0:
            raise NotAllocatedException(
                "region", region, Commands.FREE.name)

        self.mem_slot[region] = 0

        cmd_word = (
            (LEN1 << 28) |
            (Commands.FREE.value << 20) |
            (NO_REGS << 16) |
            region)
        cmd_string = "FREE memRegion={0:d}".format(region)

        encoded_cmd_word = bytearray(_ONE_WORD.pack(cmd_word))
        self.write_command_to_files(encoded_cmd_word, cmd_string)

    def declare_random_number_generator(self, rng_id, rng_type, seed):
        """ Insert command to declare a random number generator

        :param rng_id: The ID of the random number generator
        :type rng_id: int
        :param rng_type: The type of the random number generator
        :type rng_type: :py:class:`~RandomNumberGenerator`
        :param seed: The seed of the random number generator >= 0
        :type seed: int
        :return: \
            The ID of the created random number generator, between 0 and 15
        :rtype: int
        :raise data_specification.exceptions.DataUndefinedWriterException: \
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException: \
            If a write to external storage fails
        :raise data_specification.exceptions.UnknownTypeException: \
            If the rng_type is not one of the allowed values
        :raise data_specification.exceptions.ParameterOutOfBoundsException:
            * If the seed is too big or too small
            * If the rng_id is not in the allowed range
        :raise data_specification.exceptions.RNGInUseException: \
            If the random number generator with the given ID has already been\
            defined
        """

        if rng_id < 0 or rng_id >= MAX_RNGS:
            raise ParameterOutOfBoundsException(
                "random number generator ID", rng_id, 0,
                MAX_RNGS - 1, Commands.DECLARE_RNG.name)

        if rng_type not in RandomNumberGenerator:
            raise UnknownTypeException(
                rng_type.value, Commands.DECLARE_RNG.name)

        if self.rng[rng_id] is not 0:
            raise RNGInUseException(rng_id)

        if (seed > DataType.UINT32.max or  # @UndefinedVariable
                seed < DataType.UINT32.min):  # @UndefinedVariable
            raise ParameterOutOfBoundsException(
                "seed", seed, DataType.UINT32.min,  # @UndefinedVariable
                DataType.UINT32.max,  # @UndefinedVariable
                Commands.DECLARE_RNG.name)

        self.rng[rng_id] = [rng_type, seed]

        cmd_word = (
            (LEN2 << 28) |
            (Commands.DECLARE_RNG.value << 20) |
            (rng_id << 12) |
            (rng_type.value << 8))

        encoded_cmd_word = bytearray(_ONE_WORD.pack(cmd_word))
        encoded_seed = bytearray(_ONE_SINT.pack(seed))
        cmd_word_list = encoded_cmd_word + encoded_seed

        cmd_string = "DECLARE_RNG ID={0:d}, source={1:d}, seed={2:d}".format(
            rng_id, rng_type.value, seed)

        self.write_command_to_files(cmd_word_list, cmd_string)

    def declare_uniform_random_distribution(
            self, distribution_id, structure_id, rng_id, min_value, max_value):
        """ Insert commands to declare a uniform random distribution

        :param distribution_id: ID of the distribution being set up
        :param distribution_id: int
        :param structure_id: ID of an empty structure slot to fill with the\
            uniform random distribution data
        :type structure_id: int
        :param rng_id: The ID of the random number generator, between 0 and 15
        :type rng_id: int
        :param min_value: The minimum value that should be returned from the\
            distribution between -32768.0 and max_value
        :type min_value: float
        :param max_value: The maximum value that should be returned from the\
            distribution between min_value and 32767.9999847
        :type max_value: float
        :return: The ID of the created uniform random distribution to be used\
            in future calls of the distribution between 0 and 63
        :rtype: int
        :raise data_specification.exceptions.DataUndefinedWriterException: \
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException: \
            If a write to external storage fails
        :raise data_specification.exceptions.NoMoreException: \
            If there is no more space for a new random distribution
        :raise data_specification.exceptions.NotAllocatedException: \
            If the requested rng_id has not been allocated
        :raise data_specification.exceptions.ParameterOutOfBoundsException: \
            If rng_id, structure_id, min_value or max_value is out of range
        :raise data_specification.exceptions.StructureInUseException: \
            If structure structure_id is already defined
        """
        if (distribution_id < 0 or
                distribution_id >= MAX_RANDOM_DISTS):
            raise ParameterOutOfBoundsException(
                "distribution ID", distribution_id, 0,
                MAX_RANDOM_DISTS - 1, Commands.DECLARE_RANDOM_DIST.name)

        if rng_id < 0 or rng_id >= MAX_RNGS:
            raise ParameterOutOfBoundsException(
                "rng", rng_id, 0, MAX_RNGS - 1,
                Commands.DECLARE_RANDOM_DIST.name)

        if self.rng[rng_id] is 0:
            raise NotAllocatedException(
                "RNG", rng_id, Commands.DECLARE_RANDOM_DIST.name)

        if min_value < DataType.S1615.min:  # @UndefinedVariable
            raise ParameterOutOfBoundsException(
                "min_value", min_value,
                DataType.S1615.min,  # @UndefinedVariable
                DataType.S1615.max,  # @UndefinedVariable
                Commands.DECLARE_RANDOM_DIST.name)

        if max_value > DataType.S1615.max:  # @UndefinedVariable
            raise ParameterOutOfBoundsException(
                "max_value", max_value,
                DataType.S1615.min,  # @UndefinedVariable
                DataType.S1615.max,  # @UndefinedVariable
                Commands.DECLARE_RANDOM_DIST.name)

        if structure_id < 0 or structure_id >= MAX_STRUCT_SLOTS:
            raise ParameterOutOfBoundsException(
                "structure ID", structure_id, 0, MAX_STRUCT_SLOTS - 1,
                Commands.DECLARE_RANDOM_DIST.name)

        if self.random_distribution[distribution_id] is not 0:
            raise RandomNumberDistributionInUseException(distribution_id)

        parameters = [("distType", DataType.UINT32, 0),
                      ("rngID", DataType.UINT32, rng_id),
                      ("param1", DataType.S1615, min_value),
                      ("param2", DataType.S1615, max_value)]

        self.random_distribution[distribution_id] = parameters

        self.define_structure(structure_id, parameters)

        cmd_word = (
            (LEN1 << 28) |
            (Commands.DECLARE_RANDOM_DIST.value << 20) |
            (distribution_id << 8) |
            structure_id)

        cmd_string = "DECLARE_RANDOM_DIST distribution_id={0:d} " \
                     "structure_id={1:d}".format(distribution_id, structure_id)

        cmd_word_encoded = bytearray(_ONE_WORD.pack(cmd_word))
        cmd_word_list = cmd_word_encoded

        self.write_command_to_files(cmd_word_list, cmd_string)

    def call_random_distribution(self, distribution_id, register_id):
        """ Insert command to get the next random number from a random\
            distribution, placing the result in a register to be used in a\
            future call

        :param distribution_id: \
            The ID of the random distribution to call between 0 and 63
        :type distribution_id: int
        :param register_id: \
            The ID of the register to store the result in between 0 and 15
        :type register_id: int
        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException: \
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException: \
            If a write to external storage fails
        :raise data_specification.exceptions.NotAllocatedException: \
            If the random distribution ID was not previously declared
        :raise data_specification.exceptions.ParameterOutOfBoundsException: \
            If the distribution_id or register_id specified was out of range
        """
        if register_id < 0 or register_id >= MAX_REGISTERS:
            raise ParameterOutOfBoundsException(
                "register_id", register_id, 0, MAX_REGISTERS - 1,
                Commands.GET_RANDOM_NUMBER.name)

        if (distribution_id < 0 or
                distribution_id >= MAX_RANDOM_DISTS):
            raise ParameterOutOfBoundsException(
                "distribution_id", distribution_id, 0, MAX_RANDOM_DISTS - 1,
                Commands.GET_RANDOM_NUMBER.name)

        if self.random_distribution[distribution_id] is 0:
            raise NotAllocatedException(
                "random number distribution", distribution_id,
                Commands.GET_RANDOM_NUMBER.name)

        bit_field = 0x4

        cmd_string = "GET_RANDOM_NUMBER distribution={0:d} " \
                     "dest=reg[{1:d}]".format(distribution_id, register_id)
        cmd_word = (
            (LEN1 << 28) |
            (Commands.GET_RANDOM_NUMBER.value << 20) |
            (bit_field << 16) |
            (register_id << 12) |
            distribution_id)
        cmd_word_encoded = bytearray(_ONE_WORD.pack(cmd_word))
        cmd_word_list = cmd_word_encoded

        self.write_command_to_files(cmd_word_list, cmd_string)

    def define_structure(self, structure_id, parameters):
        """ Insert commands to define a data structure

        :param structure_id: the ID of the structure to create,\
            between 0 and 15
        :type structure_id: int
        :param parameters: A list of between 1 and 255 tuples of (label,\
            data_type, value) where:
            * label is the label of the element (for debugging)
            * data_type is the data type of the element
            * value is the value of the element, or None if no value is to\
            be assigned
        :type parameters: list of (str, :py:class:`~DataType`, float)
        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException: \
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException: \
            If a write to external storage fails
        :raise data_specification.exceptions.NoMoreException: \
            If there are no more spaces for new structures
        :raise data_specification.exceptions.ParameterOutOfBoundsException: \
            * If there are an incorrect number of parameters
            * If the size of one of the tuples is incorrect
            * If one of the values to be assigned has an integer data_type \
            but has a fractional part
            * If one of the values to be assigned would overflow its data_type
        :raise data_specification.exceptions.UnknownTypeException: \
            If one of the data types in the structure is unknown
        """
        # start of struct
        if structure_id < 0 or structure_id >= MAX_STRUCT_SLOTS:
            raise ParameterOutOfBoundsException(
                "structure ID", structure_id, 0,
                MAX_STRUCT_SLOTS - 1, Commands.START_STRUCT.name)

        if not parameters or len(parameters) > MAX_STRUCT_ELEMENTS:
            raise ParameterOutOfBoundsException(
                "structure elements", len(parameters), 0, MAX_STRUCT_ELEMENTS,
                Commands.WRITE_PARAM.name)

        if self.struct_slot[structure_id] != 0:
            raise StructureInUseException(structure_id)
        self.struct_slot[structure_id] = parameters

        cmd_word = (
            (LEN1 << 28) |
            (Commands.START_STRUCT.value << 20) |
            structure_id)

        cmd_word_list = bytearray(_ONE_WORD.pack(cmd_word))
        cmd_string = "START_STRUCT ID={0:d}".format(structure_id)

        self.write_command_to_files(cmd_word_list, cmd_string)

        # elements of the struct
        for elem_index, i in enumerate(parameters):
            label, data_type, value = i
            if data_type not in DataType:
                raise UnknownTypeException(
                    data_type.value, Commands.WRITE_PARAM.name)

            cmd_string = ("STRUCT_ELEM element_id={0:d}, element_type={1:s}"
                          .format(elem_index, data_type.name))
            if value is not None:

                if value < data_type.min or value > data_type.max:
                    raise ParameterOutOfBoundsException(
                        "value", value, data_type.min, data_type.max,
                        Commands.WRITE_PARAM.name)

                if data_type.size <= 4:
                    cmd_word = (
                        (LEN2 << 28) |
                        (Commands.STRUCT_ELEM.value << 20) |
                        data_type.value)
                elif data_type.size == 8:
                    cmd_word = (
                        (LEN3 << 28) |
                        (Commands.STRUCT_ELEM.value << 20) |
                        data_type.value)
                else:
                    raise InvalidSizeException(
                        data_type.name, data_type.size,
                        Commands.STRUCT_ELEM.name)

                value_encoded = bytearray(struct.pack(
                    "<{}".format(data_type.struct_encoding),
                    _rescale(value, data_type)))

                cmd_word_list = bytearray(_ONE_WORD.pack(cmd_word)) + \
                    value_encoded + bytearray((4 - data_type.size % 4) % 4)
                cmd_string += ", value={0:d}".format(value)
            else:
                cmd_word = (
                    (LEN1 << 28) |
                    (Commands.STRUCT_ELEM.value << 20) |
                    data_type.value)

                cmd_word_list = bytearray(_ONE_WORD.pack(cmd_word))

            if label != "":
                cmd_string += ", label={0:s}".format(label)
            self.write_command_to_files(cmd_word_list, cmd_string)

        # end of struct
        cmd_word = (
            (LEN1 << 28) |
            (Commands.END_STRUCT.value << 20))
        cmd_word_list = bytearray(_ONE_WORD.pack(cmd_word))
        cmd_string = "END_STRUCT ID={0:d}".format(structure_id)
        self.write_command_to_files(cmd_word_list, cmd_string)

    def get_structure_value(
            self, destination_id, structure_id, parameter_index,
            parameter_index_is_register=False):
        """ Insert command to get a value from a structure.\
            The value is copied in a register.

        :param destination_id: The ID of the destination register
        :type destination_id: int
        :param structure_id: The ID of the source structure
        :type structure_id: int
        :param parameter_index: The ID of the parameter/element to copy
        :type parameter_index: int
        :param parameter_index_is_register: \
            True if the index of the structure is contained in a register
        :type parameter_index_is_register: bool
        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException: \
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException: \
            If a write to external storage fails
        :raise data_specification.exceptions.ParameterOutOfBoundsException: \
            * If structure_id is not in the allowed range
            * If parameter_index is larger than the number of parameters\
            declared in the original structure
            * If destination_id is not the ID of a valid register
            * If parameter_index_is_register is True and parameter_index is\
            not a valid register ID
        :raise data_specification.exceptions.NotAllocatedException: \
            If the structure requested has not been declared
        """
        if structure_id < 0 or structure_id >= MAX_STRUCT_SLOTS:
            raise ParameterOutOfBoundsException(
                "structure_id", structure_id, 0,
                MAX_STRUCT_SLOTS - 1, Commands.READ_PARAM.name)

        if destination_id < 0 or destination_id >= MAX_REGISTERS:
            raise ParameterOutOfBoundsException(
                "destination_id", destination_id, 0,
                MAX_REGISTERS - 1, Commands.READ_PARAM.name)

        if self.struct_slot[structure_id] is 0:
            raise NotAllocatedException(
                "structure", structure_id, Commands.READ_PARAM)

        cmd_string = "READ_PARAM structure_id={0:d}, ".format(structure_id)

        if parameter_index_is_register is True:
            if parameter_index < 0 or parameter_index >= MAX_REGISTERS:
                raise ParameterOutOfBoundsException(
                    "parameter_index", parameter_index, 0,
                    MAX_REGISTERS - 1, Commands.READ_PARAM.name)
            cmd_word = (
                (LEN1 << 28) |
                (Commands.READ_PARAM.value << 20) |
                (DEST_AND_SRC1 << 16) |
                (destination_id << 12) |
                (parameter_index << 8) |
                structure_id)
            cmd_string += ("element_id_from_register={0:d}, "
                           "destination_register={1:d}".format(
                               parameter_index, destination_id))
        else:
            if parameter_index < 0 or parameter_index >= MAX_STRUCT_ELEMENTS:
                raise ParameterOutOfBoundsException(
                    "parameter_index", parameter_index, 0,
                    MAX_STRUCT_ELEMENTS - 1, Commands.READ_PARAM.name)

            if len(self.struct_slot[structure_id]) <= parameter_index:
                raise NotAllocatedException(
                    "structure {0:d} parameter".format(structure_id),
                    parameter_index, Commands.READ_PARAM)

            cmd_word = (
                (LEN1 << 28) |
                (Commands.READ_PARAM.value << 20) |
                (DEST_ONLY << 16) |
                (destination_id << 12) |
                (parameter_index << 4) |
                structure_id)
            cmd_string += ("element_id={0:d}, destination_register={1:d}"
                           .format(parameter_index, destination_id))

        encoded_cmd_word = bytearray(_ONE_WORD.pack(cmd_word))
        self.write_command_to_files(encoded_cmd_word, cmd_string)

    def set_structure_value(self, structure_id, parameter_index, value,
                            data_type, value_is_register=False):
        """ Insert command to set a value in a structure

        :param structure_id:
            * If called outside of a function, the ID of the structure,\
              between 0 and 15
            * If called within a function, the ID of the structure\
              argument, between 0 and 4
        :type structure_id: int
        :param parameter_index: The index of the value to assign in the\
            structure, between 0 and the number of parameters declared in the\
            structure
        :type parameter_index: int
        :param value:
            * If value_is_register is False, the value to assign at the\
              selected position as a float
            * If value_is_register is True, the ID of the register containing\
              the value to assign to the position, between 0 and 15
        :type value: float
        :param data_type: type of the data to be stored in the structure.\
            If parameter value_is_register is set to true, this variable is\
            disregarded
        :type data_type: :py:class:`~DataType`
        :param value_is_register: Identifies if value identifies a register
        :type value_is_register: bool
        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException: \
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException: \
            If a write to external storage fails
        :raise data_specification.exceptions.ParameterOutOfBoundsException: \
            * If structure_id is not in the allowed range
            * If parameter_index is larger than the number of parameters\
              declared in the original structure
            * If value_is_register is False, and the data type of the\
              structure value is an integer, and the value has a fractional\
              part
            * If value_is_register is False, and value would overflow the\
              position in the structure
            * If value_is_register is True, and value is not a valid register\
              ID
        :raise data_specification.exceptions.NotAllocatedException: \
            If the structure requested has not been declared
        """

        if structure_id < 0 or structure_id >= MAX_STRUCT_SLOTS:
            raise ParameterOutOfBoundsException(
                "structure_id", structure_id, 0,
                MAX_STRUCT_SLOTS - 1, Commands.WRITE_PARAM.name)

        if parameter_index < 0 or parameter_index >= MAX_STRUCT_ELEMENTS:
            raise ParameterOutOfBoundsException(
                "parameter_index", parameter_index, 0,
                MAX_STRUCT_ELEMENTS - 1, Commands.WRITE_PARAM.name)

        if self.struct_slot[structure_id] is 0:
            raise NotAllocatedException(
                "structure", structure_id, Commands.WRITE_PARAM)

        if len(self.struct_slot[structure_id]) <= parameter_index:
            raise NotAllocatedException(
                "structure %d parameter" % structure_id, parameter_index,
                Commands.WRITE_PARAM.name)

        if self.struct_slot[structure_id][parameter_index][1] is not data_type:
            raise TypeMismatchException(Commands.WRITE_PARAM.name)

        cmd_string = ("WRITE_PARAM structure_id={0:d}, element_id={1:d}, "
                      .format(structure_id, parameter_index))

        if value_is_register:
            if value < 0 or value >= MAX_REGISTERS:
                raise ParameterOutOfBoundsException(
                    "value", value, 0, MAX_REGISTERS - 1,
                    Commands.WRITE_PARAM.name)
            cmd_word = (
                (LEN1 << 28) |
                (Commands.WRITE_PARAM.value << 20) |
                (SRC1_ONLY << 16) |
                (structure_id << 12) |
                (value << 8) |
                parameter_index)
            value_encoded = bytearray()
            cmd_string += "value=reg[{0:d}]".format(value)
        else:
            if value < data_type.min or value > data_type.max:
                raise ParameterOutOfBoundsException(
                    "value", value, data_type.min, data_type.max,
                    Commands.WRITE_PARAM.name)

            if data_type.size > 4 and data_type.size != 8:
                raise InvalidSizeException(
                    data_type.name, data_type.size, Commands.WRITE_PARAM.name)

            cmd_len = LEN2 if data_type.size <= 4 else LEN3

            cmd_word = (
                (cmd_len << 28) |
                (Commands.WRITE_PARAM.value << 20) |
                (NO_REGS << 16) |
                (structure_id << 12) |
                parameter_index)

            encoding_string = "<{0:s}".format(data_type.struct_encoding)
            value_encoded = bytearray(struct.pack(encoding_string, value))

            if data_type.size == 1:
                padding = bytearray(3)
            elif data_type.size == 2:
                padding = bytearray(2)
            else:
                padding = bytearray()

            value_encoded += padding
            cmd_string += "value={0:d}".format(value)

        encoded_cmd_word = bytearray(_ONE_WORD.pack(cmd_word))
        cmd_word_list = encoded_cmd_word + value_encoded

        self.write_command_to_files(cmd_word_list, cmd_string)

    def write_structure(
            self, structure_id, repeats=1, repeats_is_register=False):
        """ Insert command to write a structure to the current write pointer,\
            causing the current write pointer to move on by the number of\
            bytes needed to represent the structure

        :param structure_id:
            * If called within a function, the ID of the structure to write,\
              between 0 and 15
            * If called outside of a function, the ID of the structure\
              argument, between 0 and 5
        :type structure_id: int
        :param repeats:
            * If repeats_is_register is True, the ID of the register\
              containing the number of repeats, between 0 and 15
            * If repeats_is_register is False, the number of repeats to write,\
              between 0 and 255
        :type repeats: int
        :param repeats_is_register: Identifies if repeats identifies a register
        :type repeats_is_register: bool
        :return: No value returned
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException: \
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException: \
            If a write to external storage fails
        :raise data_specification.exceptions.ParameterOutOfBoundsException: \
            * If repeats_is_register is False and structure_id is not\
              a valid ID
            * If repeats_is_register is True and structure_id
            * If the number of repeats is out of range
        :raise data_specification.exceptions.NoRegionSelectedException: \
            If no region has been  selected to write to
        :raise data_specification.exceptions.RegionExhaustedException: \
            If the selected region has no more space
        """
        if structure_id < 0 or structure_id >= MAX_STRUCT_SLOTS:
            raise ParameterOutOfBoundsException(
                "structure_id", structure_id, 0,
                MAX_STRUCT_SLOTS - 1, Commands.WRITE_STRUCT.name)

        if self.struct_slot[structure_id] is 0:
            raise NotAllocatedException(
                "structure", structure_id, Commands.WRITE_STRUCT.name)

        if repeats_is_register:
            if repeats < 0 or repeats >= MAX_REGISTERS:
                raise ParameterOutOfBoundsException(
                    "repeats", repeats, 0, MAX_REGISTERS - 1,
                    Commands.WRITE_STRUCT.name)

            cmd_word = (
                (LEN1 << 28) |
                (Commands.WRITE_STRUCT.value << 20) |
                (SRC1_ONLY << 16) |
                (repeats << 8) |
                structure_id)

            cmd_word_encoded = bytearray(_ONE_WORD.pack(cmd_word))
            cmd_string = "WRITE_STRUCT structure_id={0:d}, " \
                         "repeats=reg[{1:d}]".format(structure_id, repeats)
            cmd_word_list = cmd_word_encoded

            self.write_command_to_files(cmd_word_list, cmd_string)

        else:
            if repeats < 0 or repeats >= 16:
                raise ParameterOutOfBoundsException(
                    "repeats", repeats, 0, 15, Commands.WRITE_STRUCT.name)

            cmd_word = (
                (LEN1 << 28) |
                (Commands.WRITE_STRUCT.value << 20) |
                (repeats << 8) |
                structure_id)

            cmd_word_encoded = bytearray(_ONE_WORD.pack(cmd_word))
            cmd_string = "WRITE_STRUCT structure_id={0:d}, " \
                         "repeats={1:d}".format(structure_id, repeats)
            cmd_word_list = cmd_word_encoded

            self.write_command_to_files(cmd_word_list, cmd_string)

    def start_function(self, function_id, argument_by_value):
        """ Insert command to start a function definition, with up to 5\
            arguments, which are the IDs of structures to be used within the\
            function, each of which can be passed by reference or by value.\
            In the commands following this command up to the end_function\
            command, structures can only be referenced using the numbers 1 to\
            5 which address the arguments, rather than the original structure\
            IDs

        :param function_id: The ID of the function currently defined.
        :type function_id: int
        :param argument_by_value: A list of up to 5 booleans indicating if the\
            structure to be passed as an argument is to be passed by\
            reference (i.e., changes made within the function are persisted)\
            or by value (i.e., changes made within the function are lost when\
            the function exits. The number of arguments is determined by the\
            length of this list.
        :type argument_by_value: list of bool
        :return: The ID of the function, between 0 and 31
        :rtype: int
        :raise data_specification.exceptions.ParameterOutOfBoundsException: \
            If there are too many items in the list of arguments
        :raise data_specification.exceptions.InvalidCommandException: \
            If there is already a function being defined at this point
        :raise data_specification.exceptions.FunctionInUseException: \
            If the function is already defined
        """
        if self.ongoing_function_definition:
            raise InvalidCommandException(Commands.START_CONSTRUCTOR.name)

        if len(argument_by_value) > 5:
            raise ParameterOutOfBoundsException(
                "number of arguments", len(argument_by_value), 0, 5,
                Commands.START_CONSTRUCTOR.name)

        if function_id < 0 or function_id >= MAX_CONSTRUCTORS:
            raise ParameterOutOfBoundsException(
                "function_id", function_id, 0, MAX_CONSTRUCTORS,
                Commands.START_CONSTRUCTOR.name)

        if self.function[function_id] != 0:
            raise FunctionInUseException(function_id)

        self.function[function_id] = argument_by_value

        cmd_string = "START_CONSTRUCTOR ID={0:d} number_of_args={1:d}".format(
            function_id, len(argument_by_value))

        self.ongoing_function_definition = True

        read_only_flags = 0
        for i, abv in enumerate(argument_by_value):
            cmd_string += " arg[{0:d}]=".format(i + 1)
            if abv:
                read_only_flags |= 1 << i
                cmd_string += "read-only"
            else:
                cmd_string += "read-write"

        cmd_word = (
            (LEN1 << 28) |
            (Commands.START_CONSTRUCTOR.value << 20) |
            (function_id << 11) |
            (len(argument_by_value) << 8) |
            read_only_flags)

        cmd_word_encoded = bytearray(_ONE_WORD.pack(cmd_word))
        cmd_word_list = cmd_word_encoded

        self.write_command_to_files(cmd_word_list, cmd_string, indent=True)

    def end_function(self):
        """ Insert command to mark the end of a function definition

        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.InvalidCommandException: \
            If there is no function being defined at this point
        """

        if not self.ongoing_function_definition:
            raise InvalidCommandException(Commands.END_CONSTRUCTOR.name)

        self.ongoing_function_definition = False

        cmd_word = (
            (LEN1 << 28) |
            (Commands.END_CONSTRUCTOR.value << 20))
        cmd_word_encoded = bytearray(_ONE_WORD.pack(cmd_word))
        cmd_word_list = cmd_word_encoded

        cmd_string = "END_CONSTRUCT"

        self.write_command_to_files(cmd_word_list, cmd_string, outdent=True)

    def call_function(self, function_id, structure_ids):
        """ Insert command to call a function

        :param function_id: \
            The ID of a previously defined function, between 0 and 31
        :type function_id: int
        :param structure_ids: A list of structure_ids that will be passed into\
            the function, each between 0 and 15
        :type structure_ids: list of int
        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException: \
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException: \
            If a write to external storage fails
        :raise data_specification.exceptions.ParameterOutOfBoundsException: \
            * If the function ID is not valid
            * If any of the structure IDs are not valid
        :raise data_specification.exceptions.NotAllocatedException: \
            * If a function has not been defined with the given ID
            * If no structure has been defined with one of the IDs in\
              structure_ids
        :raise data_specification.exceptions.WrongParameterNumberException: \
            If a function is called with a wrong number of parameters
        :raise data_specification.exceptions.DuplicateParameterException: \
            If a function is called with duplicate parameters
        """
        if function_id < 0 or function_id >= MAX_CONSTRUCTORS:
            raise ParameterOutOfBoundsException(
                "function_id", function_id, 0, MAX_CONSTRUCTORS - 1,
                Commands.CONSTRUCT.name)

        if self.function[function_id] == 0:
            raise NotAllocatedException(
                "function", function_id, Commands.CONSTRUCT.name)

        if len(structure_ids) != len(self.function[function_id]):
            raise WrongParameterNumberException(
                function_id, len(self.function[function_id]), structure_ids)

        if len(structure_ids) != len(set(structure_ids)):
            raise DuplicateParameterException(
                "CONSTRUCT %d" % function_id, structure_ids)

        cmd_string = "CONSTRUCT function_id={0:d}".format(function_id)

        param_word = None
        if structure_ids:
            param_word = 0
            for i, struct_id in enumerate(structure_ids):
                if struct_id < 0 or struct_id >= MAX_STRUCT_SLOTS:
                    raise ParameterOutOfBoundsException(
                        "structure argument {0:d}".format(i),
                        struct_id, 0, MAX_STRUCT_SLOTS - 1,
                        Commands.CONSTRUCT.name)
                if self.struct_slot[struct_id] == 0:
                    raise NotAllocatedException(
                        "structure argument {0:d}".format(i),
                        struct_id, Commands.CONSTRUCT.name)

                param_word |= struct_id << (6 * i)
                cmd_string += " arg[{0:d}]=struct[{1:d}]".format(i, struct_id)

        param_word_encoded = bytearray()
        if param_word is None:
            cmd_word_length = LEN1
        else:
            cmd_word_length = LEN2
            param_word_encoded = bytearray(_ONE_WORD.pack(param_word))

        cmd_word = (
            (cmd_word_length << 28) |
            (Commands.CONSTRUCT.value << 20) |
            (function_id << 8))
        cmd_word_encoded = bytearray(_ONE_WORD.pack(cmd_word))
        cmd_word_list = cmd_word_encoded + param_word_encoded

        self.write_command_to_files(cmd_word_list, cmd_string)

    def read_value(self, dest_id, data_type):
        """ Insert command to read a value from the current write pointer,\
            causing the write pointer to move by the number of bytes read.\
            The data is stored in a register passed as argument.

        :param dest_id: The ID of the destination register.
        :type dest_id: int
        :param data_type: The type of the data to be read.
        :type data_type: :py:class:`~DataType`
        :return: Nothing is returned
        :rtype: None
        """

        cmd_len = LEN1
        cmd_code = Commands.READ.value
        cmd_field_usage = DEST_ONLY

        if data_type not in DataType:
            raise UnknownTypeException(data_type.value, Commands.WRITE.name)

        if dest_id < 0 or dest_id >= MAX_REGISTERS:
            raise ParameterOutOfBoundsException(
                "register", dest_id, 0, MAX_REGISTERS - 1,
                Commands.READ.name)

        cmd_word = (
            (cmd_len << 28) |
            (cmd_code << 20) |
            (cmd_field_usage << 16) |
            (dest_id << 12) |
            data_type.size)

        encoded_cmd_word = bytearray(_ONE_WORD.pack(cmd_word))

        cmd_string = "READ {0:d} bytes in register {1:d}".format(
            data_type.size, dest_id)

        self.write_command_to_files(encoded_cmd_word, cmd_string)

    def create_cmd(self, data, data_type=DataType.UINT32):
        """ Creates command to write a value to the current write pointer,\
            causing the write pointer to move on by the number of bytes\
            required to represent the data type. The data is passed as a\
            parameter to this function.

        .. note::
            This does not actually insert the WRITE command in the spec;\
            that is done by :py:meth:`write_cmd`.

        :param data: the data to write.
        :type data: int or float
        :param data_type: the type to convert data to
        :type data_type: :py:class:`~DataType`
        :return: cmd_word_list; list of binary words to be added to the\
            binary data specification file, and
            cmd_string; string describing the command to be added to the\
            report for the data specification file
        :rtype: (bytearray, str)
        :raise data_specification.exceptions.ParameterOutOfBoundsException: \
            * If repeats_register is None, and repeats is out of range
            * If repeats_register is not a valid register ID
            * If data_type is an integer type, and data has a fractional part
            * If data would overflow the data type
        :raise data_specification.exceptions.UnknownTypeException: \
            If the data type is not known
        :raise data_specification.exceptions.InvalidSizeException: \
            If the data size is invalid
        """
        if data_type not in DataType:
            raise UnknownTypeException(data_type.value, Commands.WRITE.name)

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

        if data_type.min > data or data_type.max < data:
            raise ParameterOutOfBoundsException(
                "data", data, data_type.min, data_type.max,
                Commands.WRITE.name)

        cmd_string = None
        if self.report_writer is not None:
            cmd_string = "WRITE data=0x%8.8X" % data

        repeat_reg_usage = NO_REGS
        cmd_word = (
            (cmd_data_len << 28) |
            (Commands.WRITE.value << 20) |
            (repeat_reg_usage << 16) | (data_len << 12) | 1)
        # 1 is based on parameters = 0, repeats = 1 and parameters |= repeats

        padding = 4 - data_type.size if data_type.size < 4 else 0
        cmd_word_list = struct.pack(
            "<I{}{}x".format(data_type.struct_encoding, padding),
            cmd_word, _rescale(data, data_type))
        if self.report_writer is not None:
            cmd_string += ", dataType={0:s}".format(data_type.name)
        return (cmd_word_list, cmd_string)

    def write_value(self, data, data_type=DataType.UINT32):
        """ Insert command to write a value one or more times to the current\
            write pointer, causing the write pointer to move on by the number\
            of bytes required to represent the data type. The data is passed\
            as a parameter to this function

        .. note::
            This method used to have two extra parameters repeats and\
            repeats_is_register. They have been removed here. If you need\
            them, use write_repeated_value

        :param data: the data to write as a float.
        :type data: float
        :param data_type: the type to convert data to
        :type data_type: :py:class:`~DataType`
        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException: \
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException: \
            If a write to external storage fails
        :raise data_specification.exceptions.ParameterOutOfBoundsException: \
            * If repeats_register is None, and repeats is out of range
            * If repeats_register is not a valid register ID
            * If data_type is an integer type, and data has a fractional part
            * If data would overflow the data type
        :raise data_specification.exceptions.UnknownTypeException: \
            If the data type is not known
        :raise data_specification.exceptions.InvalidSizeException: \
            If the data size is invalid
        :raise data_specification.exceptions.NoRegionSelectedException: \
            If no region has been selected to write to
        """
        if self.current_region is None:
            raise NoRegionSelectedException("WRITE")

        cmd_word_list, cmd_string = self.create_cmd(data, data_type)
        self.write_command_to_files(cmd_word_list, cmd_string)

    def write_cmd(self, cmd_word_list, cmd_string):
        """ Applies write commands created previously created (and cached).

        .. note::
            See :py:meth:`create_cmd` for how to create the arguments to\
            this method.

        :param cmd_word_list: list of binary words to be added to the binary\
            data specification file
        :type cmd_word_list: bytearray
        :param cmd_string: string describing the command to be added to the\
            report for the data specification file
        :type cmd_string: str
        :return: Nothing is returned
        :rtype: None
        :raise spinn_storage_handlers.exceptions.DataWriteException: \
            If a write to external storage fails
        :raise data_specification.exceptions.NoRegionSelectedException: \
            If no region has been selected to write to
        """
        if self.current_region is None:
            raise NoRegionSelectedException("WRITE")
        self.write_command_to_files(cmd_word_list, cmd_string)

    def write_repeated_value(
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
        :param repeats_is_register: \
            Indicates if the parameter repeats identifies the register\
            containing the number of repeats of the value to write
        :type repeats_is_register: bool
        :param data_type: the type to convert data to
        :type data_type: :py:class:`~DataType`
        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException: \
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException: \
            If a write to external storage fails
        :raise data_specification.exceptions.ParameterOutOfBoundsException: \
            * If repeats_register is None, and repeats is out of range
            * If repeats_register is not a valid register ID
            * If data_type is an integer type, and data has a fractional part
            * If data would overflow the data type
        :raise data_specification.exceptions.UnknownTypeException: \
            If the data type is not known
        :raise data_specification.exceptions.InvalidSizeException: \
            If the data size is invalid
        :raise data_specification.exceptions.NoRegionSelectedException: \
            If no region has been selected to write to
        """
        if self.current_region is None:
            raise NoRegionSelectedException("WRITE")

        if data_type not in DataType:
            raise UnknownTypeException(data_type.value, Commands.WRITE.name)

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
            if repeats <= 0 or repeats > 255:
                raise ParameterOutOfBoundsException(
                    "repeats", repeats, 0, 255, Commands.WRITE.name)
        else:
            if repeats < 0 or repeats >= MAX_REGISTERS:
                raise ParameterOutOfBoundsException(
                    "repeats_is_register", repeats_is_register, 0,
                    MAX_REGISTERS - 1, Commands.WRITE.name)

        if data_type.min > data or data_type.max < data:
            raise ParameterOutOfBoundsException(
                "data", data, data_type.min, data_type.max,
                Commands.WRITE.name)

        parameters = 0
        cmd_string = "WRITE data=0x%8.8X" % data

        if repeats_is_register is not False:
            repeat_reg_usage = 1
            parameters |= (repeats << 4)
            cmd_string += ", repeats=reg[{0:d}]".format(repeats)
        else:
            repeat_reg_usage = NO_REGS
            parameters |= repeats
            cmd_string += ", repeats={0:d}".format(repeats)

        cmd_word = (
            (cmd_data_len << 28) |
            (Commands.WRITE.value << 20) |
            (repeat_reg_usage << 16) | (data_len << 12) | parameters)

        padding = 4 - data_type.size if data_type.size < 4 else 0
        cmd_word_list = struct.pack(
            "<I{}{}x".format(data_type.struct_encoding, padding),
            cmd_word, _rescale(data, data_type))
        cmd_string += ", dataType={0:s}".format(data_type.name)
        self.write_command_to_files(cmd_word_list, cmd_string)

    def write_value_from_register(
            self, data_register, repeats=1, repeats_is_register=False,
            data_type=DataType.UINT32):
        """ Insert command to write a value one or more times at the write\
            pointer of the current memory region, causing it to move.\
            The data is contained in a register whose ID is passed to the\
            function

        :param data_register: \
            Identifies the register in which the data is stored.
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
        :type data_type: :py:class:`~DataType`
        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException: \
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException: \
            If a write to external storage fails
        :raise data_specification.exceptions.ParameterOutOfBoundsException: \
            * If repeats_register is None, and repeats is out of range
            * If repeats_register is not a valid register ID
            * If data_register is not a valid register ID
        :raise data_specification.exceptions.UnknownTypeException: \
            If the data type is not known
        :raise data_specification.exceptions.NoRegionSelectedException: \
            If no region has been selected to write to
        :raise data_specification.exceptions.RegionExhaustedException: \
            If the selected region has no more space
        """
        if data_type not in DataType:
            raise UnknownTypeException(
                data_type.value, Commands.WRITE.name)

        if self.current_region is None:
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
            if repeats <= 0 or repeats > 255:
                raise ParameterOutOfBoundsException(
                    "repeats", repeats, 0, 255, Commands.WRITE.name)
        else:
            if repeats < 0 or repeats >= MAX_REGISTERS:
                raise ParameterOutOfBoundsException(
                    "repeats", repeats, 0, MAX_REGISTERS - 1,
                    Commands.WRITE.name)

        if data_register < 0 or data_register >= MAX_REGISTERS:
            raise ParameterOutOfBoundsException(
                "data_register", data_register, 0, MAX_REGISTERS - 1,
                Commands.WRITE.name)

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

        cmd_word = (
            (LEN1 << 28) |
            (Commands.WRITE.value << 20) |
            (reg_usage << 16) |
            (cmd_data_len << 12) |
            (data_register << 8) | parameters)

        encoded_cmd_word = bytearray(_ONE_WORD.pack(cmd_word))
        cmd_word_list = encoded_cmd_word
        cmd_string += ", dataType={0:s}".format(data_type.name)
        self.write_command_to_files(cmd_word_list, cmd_string)

    def write_array(self, array_values, data_type=DataType.UINT32):
        """ Insert command to write an array, causing the write pointer\
            to move on by (data type size * the array size), in bytes.

        :param array_values: An array of words to be written
        :type array_values: list of unsigned int
        :param data_type: Type of data contained in the array
        :type data_type: :py:class:`~data_specification.enums.DataType`
        :return: The position of the write pointer within the current region,\
            in bytes from the start of the region
        :rtype: int
        :raise data_specification.exceptions.DataUndefinedWriterException: \
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException: \
            If a write to external storage fails
        :raise data_specification.exceptions.NoRegionSelectedException: \
            If no region has been previously selected
        """
        cmd_len = LEN2

        if data_type.numpy_typename is None:
            raise TypeMismatchException(Commands.WRITE_ARRAY.name)
        if self.current_region is None:
            raise NoRegionSelectedException(Commands.WRITE_ARRAY.name)

        cmd_word = (
            (cmd_len << 28) |
            (Commands.WRITE_ARRAY.value << 20) |
            data_type.size)

        data = numpy.array(array_values, dtype=data_type.numpy_typename)
        size = data.size * data_type.size
        if size % 4 != 0:
            raise UnknownTypeLengthException(size, Commands.WRITE_ARRAY.name)

        cmd_string = "WRITE_ARRAY, {0:d} elements\n".format(size // 4)

        cmd_word_list = bytearray(_TWO_WORDS.pack(cmd_word, size // 4))
        self.write_command_to_files(cmd_word_list, cmd_string)
        self.spec_writer.write(data.tostring())

    def switch_write_focus(self, region):
        """ Insert command to switch the region being written to

        :param region: The ID of the region to switch to, between 0 and 15
        :type region: int
        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException: \
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException: \
            If a write to external storage fails
        :raise data_specification.exceptions.ParameterOutOfBoundsException: \
            If the region identifier is not valid
        :raise data_specification.exceptions.NotAllocatedException: \
            If the region has not been allocated
        :raise data_specification.exceptions.RegionUnfilledException: \
            If the selected region should not be filled
        """
        if region < 0 or region >= MAX_MEM_REGIONS:
            raise ParameterOutOfBoundsException(
                "region", region, 0, MAX_MEM_REGIONS - 1,
                Commands.SWITCH_FOCUS.name)

        if self.mem_slot[region] == 0:
            raise NotAllocatedException(
                "region", region, Commands.SWITCH_FOCUS.name)

        if self.mem_slot[region][2]:
            raise RegionUnfilledException(region, Commands.SWITCH_FOCUS.name)

        self.current_region = region

        reg_usage = 0x0
        parameters = region & 0xF
        cmd_string = "SWITCH_FOCUS memRegion = {0:d}".format(region)

        # Write command to switch focus:
        cmd_word = (
            (LEN1 << 28) |
            (Commands.SWITCH_FOCUS.value << 20) |
            (reg_usage << 16) |
            (parameters << 8))

        encoded_cmd_word = bytearray(_ONE_WORD.pack(cmd_word))

        cmd_word_string = encoded_cmd_word
        self.write_command_to_files(cmd_word_string, cmd_string)

    def start_loop(self, counter_register_id, start, end, increment=1,
                   start_is_register=False, end_is_register=False,
                   increment_is_register=False):
        """ Insert command to start a loop

        :param counter_register_id: The ID of the register to use as the loop\
            counter, between 0 and 15
        :type counter_register_id: int
        :param start:
            * If start_is_register is False, the number at which to start the\
              loop counter, >= 0
            * If start_is_register is True, the ID of the register containing\
              the number at which to start the loop counter, between 0 and 15
        :type start: int
        :param end:
            * If end_is_register is False, the number which the loop\
              counter must reach to stop the loop i.e. the loop will\
              run while the contents of counter_register < end, >= 0
            * If end_is_register is True, the ID of the register\
              containing the number at which to stop the loop,\
              between 0 and 15
        :type end: int
        :param increment:
            * If increment_is_register is False, the amount by which to\
              increment the loop counter on each run of the loop, >= 0
            * If increment_is_register is True, the ID of the register\
              containing the amount by which to increment the loop counter on\
              each run of the loop, between 0 and 15
        :type increment: int
        :param start_is_register: Indicates if start is a register ID
        :type start_is_register: bool
        :param end_is_register: Indicates if end is a register ID
        :type end_is_register: bool
        :param increment_is_register: Indicates if increment is a register ID
        :type increment_is_register: bool
        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException: \
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException: \
            If a write to external storage fails
        :raise data_specification.exceptions.ParameterOutOfBoundsException: \
            * If counter_register_id is not a valid register ID
            * If start_is_register is True and increment is not a valid\
              register_id
            * If end_is_register is True and increment is not a valid\
              register_id
            * If increment_is_register is True, and increment is not a\
              valid register_id
            * If start_is_register is False and start is not in the\
              allowed range
            * If end_is_register is False and end is not in the\
              allowed range
            * If increment_is_register is False and increment is not\
              in the allowed range
        """
        bit_field = 0
        length = LEN1
        encoded_values = bytearray()
        cmd_word = (Commands.LOOP.value << 20)
        cmd_string = "LOOP"

        if counter_register_id < 0 or counter_register_id >= MAX_REGISTERS:
            raise ParameterOutOfBoundsException(
                "counter_register_id", counter_register_id, 0,
                MAX_REGISTERS - 1, Commands.LOOP.name)
        cmd_word |= counter_register_id
        cmd_string += " counter_register_id=reg[{0:d}],".format(
            counter_register_id)

        if start_is_register:
            if start < 0 or start >= MAX_REGISTERS:
                raise ParameterOutOfBoundsException(
                    "start", start, 0, MAX_REGISTERS - 1, Commands.LOOP.name)
            bit_field |= 0x4
            cmd_word |= (start << 12)
            cmd_string += " start=reg[{0:d}],".format(start)
        else:
            if (start < DataType.INT32.min or  # @UndefinedVariable
                    start > DataType.INT32.max):  # @UndefinedVariable
                raise ParameterOutOfBoundsException(
                    "start", start,
                    DataType.INT32.min,  # @UndefinedVariable
                    DataType.INT32.max,  # @UndefinedVariable
                    Commands.LOOP.name)
            length += 1
            encoded_values += bytearray(_ONE_SINT.pack(start))
            cmd_string += " start={0:d},".format(start)

        if end_is_register:
            if end < 0 or end >= MAX_REGISTERS:
                raise ParameterOutOfBoundsException(
                    "end", end, 0, MAX_REGISTERS - 1, Commands.LOOP.name)
            bit_field |= 0x2
            cmd_word |= (end << 8)
            cmd_string += " end=reg[{0:d}],".format(end)
        else:
            if (end < DataType.INT32.min or  # @UndefinedVariable
                    end > DataType.INT32.max):  # @UndefinedVariable
                raise ParameterOutOfBoundsException(
                    "end", end,
                    DataType.INT32.min,  # @UndefinedVariable
                    DataType.INT32.max,  # @UndefinedVariable
                    Commands.LOOP.name)
            length += 1
            encoded_values += bytearray(_ONE_SINT.pack(end))
            cmd_string += " end={0:d},".format(end)

        if increment_is_register:
            if increment < 0 or increment >= MAX_REGISTERS:
                raise ParameterOutOfBoundsException(
                    "increment", increment, 0, MAX_REGISTERS - 1,
                    Commands.LOOP.name)
            bit_field |= 0x1
            cmd_word |= (increment << 4)
            cmd_string += " increment=reg[{0:d}],".format(increment)
        else:
            if (increment < DataType.INT32.min or  # @UndefinedVariable
                    increment > DataType.INT32.max):  # @UndefinedVariable
                raise ParameterOutOfBoundsException(
                    "increment", increment,
                    DataType.INT32.min,  # @UndefinedVariable
                    DataType.INT32.max,  # @UndefinedVariable
                    Commands.LOOP.name)
            length += 1
            encoded_values += bytearray(_ONE_SINT.pack(increment))
            cmd_string += " increment={0:d},".format(increment)

        self.ongoing_loop = True

        cmd_word |= (length << 28)
        cmd_word |= (bit_field << 16)

        encoded_cmd_word = bytearray(_ONE_WORD.pack(cmd_word))
        cmd_word_list = encoded_cmd_word + encoded_values
        self.write_command_to_files(cmd_word_list, cmd_string)

    def break_loop(self):
        """ Insert command to break out of a loop before it has completed

        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException: \
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException: \
            If a write to external storage fails
        :raise data_specification.exceptions.InvalidCommandException: \
            If there is no loop in operation at this point
        """

        if not self.ongoing_loop:
            raise InvalidCommandException("END_LOOP")
        cmd_word = (
            (LEN1 << 28) |
            (Commands.BREAK_LOOP.value << 20))
        cmd_string = "BREAK_LOOP"
        cmd_word_encoded = bytearray(_ONE_WORD.pack(cmd_word))
        cmd_word_list = cmd_word_encoded

        self.write_command_to_files(cmd_word_list, cmd_string)

    def end_loop(self):
        """ Insert command to indicate that this is the end of the loop.\
            Commands between the start of the loop and this command will be\
            repeated.

        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException: \
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException: \
            If a write to external storage fails
        :raise data_specification.exceptions.InvalidCommandException: \
            If there is no loop in operation at this point
        """
        cmd_word = (
            (LEN1 << 28) |
            (Commands.END_LOOP.value << 20))
        cmd_string = "END_LOOP"
        cmd_word_encoded = bytearray(_ONE_WORD.pack(cmd_word))
        cmd_word_list = cmd_word_encoded

        self.write_command_to_files(cmd_word_list, cmd_string)

    def start_conditional(self, register_id, condition, value,
                          value_is_register=False):
        """ Insert command to start a conditional if...then...else construct.\
            If the condition evaluates to true, the statement is executed up\
            to the next else statement, or the end of the conditional,\
            whichever comes first.

        :param register_id: The ID of a register to compare the value of
        :type register_id: int
        :param condition: \
            The condition which must be true to execute the following commands
        :type condition: :py:class:`Condition`
        :param value:
            * If value_is_register is False, the value to compare to the\
              value in the register
            * If value_is_register is True, the ID of the register containing\
              the value to compare, between 0 and 15
        :type value: int
        :param value_is_register: Indicates if value is a register ID
        :type value_is_register: bool
        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException: \
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException: \
            If a write to external storage fails
        :raise data_specification.exceptions.ParameterOutOfBoundsException: \
            * If the register_id is not a valid register ID
            * if value_is_register is True and value is not a valid\
              register ID
        :raise data_specification.exceptions.UnknownTypeException: \
            If the condition is not a valid condition
        """
        data_encoded = bytearray()
        cmd_word = 0
        cmd_string = ""

        if register_id < 0 or register_id >= MAX_REGISTERS:
            raise ParameterOutOfBoundsException(
                "register_id", register_id, 0, MAX_REGISTERS - 1,
                Commands.IF.name)
        if value_is_register:
            if value < 0 or value >= MAX_REGISTERS:
                raise ParameterOutOfBoundsException(
                    "value", value, 0, MAX_REGISTERS - 1, Commands.IF.name)
        else:
            if (value < DataType.INT32.min or  # @UndefinedVariable
                    value > DataType.INT32.max):  # @UndefinedVariable
                raise ParameterOutOfBoundsException(
                    "value", value,
                    DataType.INT32.min,  # @UndefinedVariable
                    DataType.INT32.max,  # @UndefinedVariable
                    Commands.IF.name)

        if condition not in Condition:
            raise UnknownConditionException(condition, Commands.IF.name)

        if value_is_register:
            bit_field = 0x3
            cmd_word = (
                (LEN1 << 28) |
                (Commands.IF.value << 20) |
                (bit_field << 16) |
                (register_id << 8) |
                (value << 4) |
                condition.value)
            cmd_string = "IF reg[{0:d}] {1:s} reg[{2:d}]".format(
                register_id, condition.operator, value)

        elif not value_is_register:
            bit_field = 0x2
            cmd_word = (
                (LEN2 << 28) |
                (Commands.IF.value << 20) |
                (bit_field << 16) |
                (register_id << 8) |
                condition.value)
            data_encoded = bytearray(_ONE_SINT.pack(value))
            cmd_string = "IF reg[{0:d}] {1:s} {2:d}".format(
                register_id, condition.operator, value)

        self.conditionals.append(False)

        cmd_word_encoded = bytearray(_ONE_WORD.pack(cmd_word))
        cmd_word_list = cmd_word_encoded + data_encoded
        self.write_command_to_files(cmd_word_list, cmd_string, indent=True)

    def else_conditional(self):
        """ Insert command for the else of an if...then...else construct.\
            If the condition of the conditional evaluates to false, the\
            statements up between the conditional and the insertion of this\
            "else" are skipped, and the statements from this point until the\
            end of the conditional are executed.

        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException: \
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException: \
            If a write to external storage fails
        :raise data_specification.exceptions.InvalidCommandException: \
            If there is no conditional in operation at this point
        """

        if not self.conditionals or \
                self.conditionals[len(self.conditionals) - 1] is True:
            raise InvalidCommandException("ELSE")

        self.conditionals[len(self.conditionals) - 1] = True

        cmd_word = (
            (LEN1 << 28) |
            (Commands.ELSE.value << 20))
        cmd_word_encoded = bytearray(_ONE_WORD.pack(cmd_word))
        cmd_word_list = cmd_word_encoded
        cmd_string = "ELSE"

        self.write_command_to_files(
            cmd_word_list, cmd_string, indent=True, outdent=True)

    def end_conditional(self):
        """ Insert command to mark the end of an if...then...else construct

        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException: \
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException: \
            If a write to external storage fails
        :raise data_specification.exceptions.InvalidCommandException: \
            If there is no conditional in operation at this point
        """

        if not self.conditionals:
            raise InvalidCommandException("END_IF")

        self.conditionals.pop()

        cmd_word = (
            (LEN1 << 28) |
            (Commands.END_IF.value << 20))
        cmd_word_encoded = bytearray(_ONE_WORD.pack(cmd_word))
        cmd_word_list = cmd_word_encoded
        cmd_string = "END_IF"

        self.write_command_to_files(cmd_word_list, cmd_string, outdent=True)

    def set_register_value(self, register_id, data, data_is_register=False,
                           data_type=DataType.UINT32):
        """ Insert command to set the value of a register

        :param register_id: The ID of the register to assign, between 0 and 15
        :type register_id: int
        :param data:
            * If data_is_register is True, the register ID containing\
              the data to set, between 0 and 15
            * If data_is_register is False, the data as a float
        :type data: float
        :param data_is_register: Indicates if data is a register ID
        :type data_is_register: bool
        :param data_type: The type of the data to be assigned
        :type data_type: :py:class:`~DataType`
        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException: \
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException: \
            If a write to external storage fails
        :raise data_specification.exceptions.ParameterOutOfBoundsException: \
            * If register_id is not a valid register_id
            * If data_is_register is True, and data is not a valid\
              register ID
            * If data_is_register is False, data_type is an integer type and\
              data has a fractional part
            * If data_is_register if False, and data would overflow the\
              data type
        :raise data_specification.exceptions.UnknownTypeException: \
            If the data type is not known
        """
        if register_id < 0 or register_id >= MAX_REGISTERS:
            raise ParameterOutOfBoundsException(
                "register_id", register_id, 0, MAX_REGISTERS - 1,
                Commands.MV.name)

        if data_is_register:

            # Build command to move between registers:
            if data < 0 or data >= MAX_REGISTERS:
                raise ParameterOutOfBoundsException(
                    "data", data, 0, MAX_REGISTERS - 1, Commands.MV.name)

            if data == register_id:
                raise DuplicateParameterException(
                    Commands.MV.name, [register_id, data])

            dest_reg = register_id
            src_reg = data
            cmd_word = (
                (LEN1 << 28) |
                (Commands.MV.value << 20) |
                (DEST_AND_SRC1 << 16) |
                (dest_reg << 12) |
                (src_reg << 8))
            encoded_cmd_word = bytearray(_ONE_WORD.pack(cmd_word))
            cmd_word_list = encoded_cmd_word
            cmd_string = "reg[{0:d}] = reg[{1:d}]".format(dest_reg, src_reg)
        else:

            # Build command to assign from an immediate:
            # command has a second word (the immediate)
            if data_type.min > data or data_type.max < data:
                raise ParameterOutOfBoundsException(
                    "data", data, data_type.min, data_type.max,
                    Commands.MV.name)

            if data_type.size > 4:
                length = LEN3
            else:
                length = LEN2

            dest_reg = register_id
            cmd_word = (
                (length << 28) |
                (Commands.MV.value << 20) |
                (DEST_ONLY << 16) |
                (dest_reg << 12))

            scaled_data = int(data * data_type.scale)
            encoding_string = "<{0:s}".format(data_type.struct_encoding)
            encoded_data = bytearray(struct.pack(encoding_string, scaled_data))
            while len(encoded_data) % 4:
                encoded_data += bytearray(_ONE_SBYTE.pack(0))

            encoded_cmd_word = bytearray(_ONE_WORD.pack(cmd_word))

            cmd_word_list = encoded_cmd_word + encoded_data
            cmd_string = "reg[{0:d}] = {1:d} (0x{2:X})".format(
                dest_reg, data, data)

        self.write_command_to_files(cmd_word_list, cmd_string)

    def save_write_pointer(self, register_id):
        """ Insert command to save the write pointer to a register

        :param register_id: The ID of the register to assign, between 0 and 15
        :type register_id: int
        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException: \
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException: \
            If a write to external storage fails
        :raise data_specification.exceptions.ParameterOutOfBoundsException: \
            If the register_id is not a valid register ID
        :raise data_specification.exceptions.NoRegionSelectedException: \
            If no region has been selected
        """
        if register_id < 0 or register_id >= MAX_REGISTERS:
            raise ParameterOutOfBoundsException(
                "register_id", register_id, 0, MAX_REGISTERS - 1,
                Commands.GET_WR_PTR.name)
        if self.current_region is None:
            raise NoRegionSelectedException(Commands.GET_WR_PTR.name)
        bit_field = 0x4
        cmd_word = (
            (LEN1 << 28) |
            (Commands.GET_WR_PTR.value << 20) |
            (bit_field << 16) |
            (register_id << 12))
        cmd_string = "GET_WR_PTR reg[{0:d}]".format(register_id)
        cmd_word_encoded = bytearray(_ONE_WORD.pack(cmd_word))
        cmd_word_list = cmd_word_encoded

        self.write_command_to_files(cmd_word_list, cmd_string)

    def set_write_pointer(self, address, address_is_register=False,
                          relative_to_current=False):
        """ Insert command to set the position of the write pointer within the\
            current region

        :param address:
            * If address_is_register is True, the ID of the register\
              containing the address to move to
            * If address_is_register is False, the address to move the\
              write pointer to
        :type address: int
        :param address_is_register: \
            Indicates if the the address is a register ID
        :type address_is_register: bool
        :param relative_to_current: \
            Indicates if the address is to be added to the current address,\
            or used as an absolute address from the start of the current region
        :type relative_to_current: bool
        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException: \
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException: \
            If a write to external storage fails
        :raise data_specification.exceptions.ParameterOutOfBoundsException: \
            If the address_is_register is True and address is not a valid\
            register ID
        :raise data_specification.exceptions.NoRegionSelectedException: \
            If no region has been selected
        """
        if self.current_region is None:
            raise NoRegionSelectedException(Commands.SET_WR_PTR.name)
        if relative_to_current:
            relative = 1
            relative_string = "RELATIVE"
        else:
            relative = 0
            relative_string = "ABSOLUTE"

        data_encoded = bytearray()
        if address_is_register:
            if address < 0 or address >= MAX_REGISTERS:
                raise ParameterOutOfBoundsException(
                    "address", address, 0, MAX_REGISTERS - 1,
                    Commands.SET_WR_PTR.name)
            cmd_word = (
                (LEN1 << 28) |
                (Commands.SET_WR_PTR.value << 20) |
                (SRC1_ONLY << 16) |
                (address << 8) |
                relative)
            cmd_string = "SET_WR_PTR reg[{0:d}] {1:s}".format(
                address, relative_string)
        else:
            if not relative_to_current:
                if (address < 0 or
                        address > DataType.UINT32.max):  # @UndefinedVariable
                    raise ParameterOutOfBoundsException(
                        "address", address, 0,
                        DataType.UINT32.max,  # @UndefinedVariable
                        Commands.SET_WR_PTR.name)
                else:
                    data_encoded = bytearray(_ONE_WORD.pack(address))
            else:
                if (address < DataType.INT32.min or  # @UndefinedVariable
                        address > DataType.INT32.max):  # @UndefinedVariable
                    raise ParameterOutOfBoundsException(
                        "address", address,
                        DataType.INT32.min,  # @UndefinedVariable
                        DataType.INT32.max,  # @UndefinedVariable
                        Commands.SET_WR_PTR.name)
                else:
                    data_encoded = bytearray(_ONE_SINT.pack(address))

            cmd_word = (
                (LEN2 << 28) |
                (Commands.SET_WR_PTR.value << 20) |
                (NO_REGS << 16) |
                relative)
            cmd_string = "SET_WR_PTR {0:d} {1:s}".format(
                address, relative_string)

        cmd_word_encoded = bytearray(_ONE_WORD.pack(cmd_word))
        cmd_word_list = cmd_word_encoded + data_encoded

        self.write_command_to_files(cmd_word_list, cmd_string)

    def align_write_pointer(self, log_block_size,
                            log_block_size_is_register=False,
                            return_register_id=None):
        """ Insert command to align the write pointer against a power-of-2\
            block size in bytes.  Zeros are inserted in the intervening space

        :param log_block_size:
            * If log_block_size_is_register is False, log to base 2 of\
              the block size (e.g. The write pointer will be moved so\
              that it is a multiple of 2^(log_block_size)), between 0 and 32
            * If log_block_size_is_register is True, the ID of the\
              register containing log to the base 2 of the block size,\
              between 0 and 15
        :type log_block_size: int
        :param log_block_size_is_register: \
            Indicates if log_block_size is a register ID
        :type log_block_size_is_register: bool
        :param return_register_id: The ID of a register where the write\
            pointer will be written to once it has been updated, between\
            0 and 15or None if no such writing is to be done
        :type return_register_id: int
        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException: \
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException: \
            If a write to external storage fails
        :raise data_specification.exceptions.ParameterOutOfBoundsException: \
            * If log_block_size_is_register is False, and\
              log_block_size is not within the allowed range
            * If log_block_size_is_register is True and log_block_size\
              is not a valid register ID
        :raise data_specification.exceptions.RegionOutOfBoundsException: \
            If the move of the pointer would put it outside of the\
            current region
        :raise data_specification.exceptions.NoRegionSelectedException: \
            If no region has been selected
        """
        bit_field = 0
        imm_value = 0
        return_register_value = 0
        block_size_reg = 0
        cmd_string = "ALIGN_WR_PTR"

        if self.current_region is None:
            raise NoRegionSelectedException(Commands.ALIGN_WR_PTR.name)

        if return_register_id is not None:
            if return_register_id < 0 or return_register_id >= MAX_REGISTERS:
                raise ParameterOutOfBoundsException(
                    "return_register_id", return_register_id, 0,
                    MAX_REGISTERS - 1, Commands.ALIGN_WR_PTR.name)
            bit_field |= 0x4
            return_register_value = return_register_id
            cmd_string += " reg[{0:d}] =".format(return_register_value)

        if log_block_size_is_register:
            if log_block_size < 0 or log_block_size >= MAX_REGISTERS:
                raise ParameterOutOfBoundsException(
                    "log_block_size", log_block_size, 0,
                    MAX_REGISTERS - 1, Commands.ALIGN_WR_PTR.name)
            bit_field |= 0x2
            block_size_reg = log_block_size
            cmd_string += " align(reg[{0:d}])".format(block_size_reg)
        else:
            if log_block_size < 0 or log_block_size > 31:
                raise ParameterOutOfBoundsException(
                    "log_block_size", log_block_size, 0, 31,
                    Commands.ALIGN_WR_PTR.name)
            imm_value = log_block_size
            cmd_string += " align({0:d})".format(imm_value)

        cmd_word = (
            (LEN1 << 28) |
            (Commands.ALIGN_WR_PTR.value << 20) |
            (bit_field << 16) |
            (return_register_value << 12) |
            (block_size_reg << 8) |
            imm_value)
        cmd_word_encoded = bytearray(_ONE_WORD.pack(cmd_word))
        cmd_word_list = cmd_word_encoded

        self.write_command_to_files(cmd_word_list, cmd_string)

    def call_arithmetic_operation(self, register_id, operand_1, operation,
                                  operand_2, signed,
                                  operand_1_is_register=False,
                                  operand_2_is_register=False):
        """ Insert command to perform an arithmetic operation on two signed or\
            unsigned values and store the result in a register

        :param register_id: The ID of the register to store the result in
        :type register_id: int
        :param operand_1:
            * If operand_1_is_register is True, the ID of a register where\
              the first operand can be found, between 0 and 15
            * If operand_1_is_register is False, a 32-bit value
        :type operand_1: int
        :param operation: The operation to perform
        :type operation: :py:class:`~ArithmeticOperation`
        :param operand_2:
            * If operand_2_is_register is True, the ID of a register where\
              the second operand can be found, between 0 and 15
            * If operand_2_is_register is False, a 32-bit value
        :type operand_2: int
        :param signed: Indicates if the values should be considered signed
        :type signed: bool
        :param operand_1_is_register: Indicates if operand_1 is a register ID
        :type operand_1_is_register: bool
        :param operand_2_is_register: Indicates if operand_2 is a register ID
        :type operand_2_is_register: bool
        :raise data_specification.exceptions.DataUndefinedWriterException: \
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException: \
            If a write to external storage fails
        :raise data_specification.exceptions.ParameterOutOfBoundsException: \
            * If operand_1_is_register is True and operand_1 is not a\
              valid register ID
            * If operand_2_is_register is True and operand_2 is not a\
              valid register ID
        :raise data_specification.exceptions.UnknownTypeException: \
            If operation is not a known operation
        """
        bit_field = 0x4
        register_op_1 = 0
        register_op_2 = 0
        payload = bytearray()

        if register_id < 0 or register_id >= MAX_REGISTERS:
            raise ParameterOutOfBoundsException(
                "register_id", register_id, 0, MAX_REGISTERS - 1,
                Commands.ARITH_OP.name)

        cmd_string = "ARTIH_OP {0:s} reg[{1:d}] =".format(
            "SIGNED" if signed else "UNSIGNED", register_id)

        if operand_1_is_register:
            if operand_1 < 0 or operand_1 >= MAX_REGISTERS:
                raise ParameterOutOfBoundsException(
                    "operand_1", operand_1, 0, MAX_REGISTERS - 1,
                    Commands.ARITH_OP.name)
            bit_field |= 2
            register_op_1 = operand_1
            cmd_string += " reg[{0:d}]".format(register_op_1)
        elif signed:
            if (operand_1 < DataType.INT32.min or  # @UndefinedVariable
                    operand_1 > DataType.INT32.max):  # @UndefinedVariable
                raise ParameterOutOfBoundsException(
                    "operand_1", operand_1,
                    DataType.INT32.min,  # @UndefinedVariable
                    DataType.INT32.max,  # @UndefinedVariable
                    Commands.ARITH_OP.name)
            payload += bytearray(_ONE_SINT.pack(operand_1))
            cmd_string += " " + str(operand_1)
        else:
            if (operand_1 < DataType.UINT32.min or  # @UndefinedVariable
                    operand_1 > DataType.UINT32.max):  # @UndefinedVariable
                raise ParameterOutOfBoundsException(
                    "operand_1", operand_1,
                    DataType.UINT32.min,  # @UndefinedVariable
                    DataType.UINT32.max,  # @UndefinedVariable
                    Commands.ARITH_OP.name)
            payload += bytearray(_ONE_WORD.pack(operand_1))
            cmd_string += " " + str(operand_1)

        if operation not in ArithmeticOperation:
            raise InvalidOperationException(
                "arithmetic", operation.value, Commands.ARITH_OP.name)

        cmd_string += " " + operation.operator

        if operand_2_is_register:
            if operand_2 < 0 or operand_2 >= MAX_REGISTERS:
                raise ParameterOutOfBoundsException(
                    "operand_2", operand_2, 0, MAX_REGISTERS - 1,
                    Commands.ARITH_OP.name)
            bit_field |= 1
            register_op_2 = operand_2
            cmd_string += " reg[{0:d}]".format(register_op_2)
        elif signed:
            if (operand_2 < DataType.INT32.min or  # @UndefinedVariable
                    operand_2 > DataType.INT32.max):  # @UndefinedVariable
                raise ParameterOutOfBoundsException(
                    "operand_2", operand_2,
                    DataType.INT32.min,  # @UndefinedVariable
                    DataType.INT32.max,  # @UndefinedVariable
                    Commands.ARITH_OP.name)
            payload += bytearray(_ONE_SINT.pack(operand_2))
            cmd_string += " " + str(operand_2)
        else:
            if (operand_2 < DataType.UINT32.min or  # @UndefinedVariable
                    operand_2 > DataType.UINT32.max):  # @UndefinedVariable
                raise ParameterOutOfBoundsException(
                    "operand_2", operand_2,
                    DataType.UINT32.min,  # @UndefinedVariable
                    DataType.UINT32.max,  # @UndefinedVariable
                    Commands.ARITH_OP.name)
            payload += bytearray(_ONE_WORD.pack(operand_2))
            cmd_string += " " + str(operand_2)

        cmd_word = (
            (len(payload) << 26) |
            (Commands.ARITH_OP.value << 20) |
            (int(signed) << 19) |
            (bit_field << 16) |
            (register_id << 12) |
            (register_op_1 << 8) |
            (register_op_2 << 4) |
            operation.value)

        self.write_command_to_files(
            bytearray(_ONE_WORD.pack(cmd_word)) + payload,
            cmd_string)

    def logical_and(self, register_id, operand_1, operand_2,
                    operand_1_is_register=False, operand_2_is_register=False):
        """ Insert command to perform a logical AND operation, using the\
             _call_logic_operation.

        :param register_id: The ID of the register to store the result in
        :type register_id: int
        :param operand_1:
            * If operand_1_is_register is True, the ID of a register\
              where the first operand can be found, between 0 and 15
            * If operand_1_is_register is False, a 32-bit value
        :type operand_1: int
        :param operand_2:
            * If operand_2_is_register is True, the ID of a register\
              where the second operand can be found. between 0 and 15
            * If operand_2_is_register is False, a 32-bit value
        :type operand_2: int
        :param operand_1_is_register: Indicates if operand_1 is a register ID
        :type operand_1_is_register: bool
        :param operand_2_is_register: Indicates if operand_2 is a register ID
        :type operand_2_is_register: bool
        :raise data_specification.exceptions.DataUndefinedWriterException: \
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException: \
            If a write to external storage fails
        :raise data_specification.exceptions.ParameterOutOfBoundsException: \
            * If operand_1_is_register is True and operand_1 is not a\
              valid register ID
            * If operand_2_is_register is True and operand_2 is not a\
              valid register ID
        """
        self._call_logic_operation(register_id, operand_1, LogicOperation.AND,
                                   operand_2, operand_1_is_register,
                                   operand_2_is_register)

    def logical_or(self, register_id, operand_1, operand_2,
                   operand_1_is_register=False, operand_2_is_register=False):
        """ Insert command to perform a logical OR operation, using the\
            _call_logic_operation.

        :param register_id: The ID of the register to store the result in
        :type register_id: int
        :param operand_1:
            * If operand_1_is_register is True, the ID of a register\
              where the first operand can be found, between 0 and 15
            * If operand_1_is_register is False, a 32-bit value
        :type operand_1: int
        :param operand_2:
            * If operand_2_is_register is True, the ID of a register\
              where the second operand can be found. between 0 and 15
            * If operand_2_is_register is False, a 32-bit value
        :type operand_2: int
        :param operand_1_is_register: Indicates if operand_1 is a register ID
        :type operand_1_is_register: bool
        :param operand_2_is_register: Indicates if operand_2 is a register ID
        :type operand_2_is_register: bool
        :raise data_specification.exceptions.DataUndefinedWriterException: \
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException: \
            If a write to external storage fails
        :raise data_specification.exceptions.ParameterOutOfBoundsException: \
            * If operand_1_is_register is True and operand_1 is not a\
              valid register ID
            * If operand_2_is_register is True and operand_2 is not a\
              valid register ID
        """
        self._call_logic_operation(register_id, operand_1, LogicOperation.OR,
                                   operand_2, operand_1_is_register,
                                   operand_2_is_register)

    def logical_left_shift(self, register_id, operand_1, operand_2,
                           operand_1_is_register=False,
                           operand_2_is_register=False):
        """ Insert command to perform a logical left shift operation, using\
            the _call_logic_operation.

        :param register_id: The ID of the register to store the result in
        :type register_id: int
        :param operand_1:
            * If operand_1_is_register is True, the ID of a register\
              where the first operand can be found, between 0 and 15
            * If operand_1_is_register is False, a 32-bit value
        :type operand_1: int
        :param operand_2:
            * If operand_2_is_register is True, the ID of a register\
              where the second operand can be found. between 0 and 15
            * If operand_2_is_register is False, a 32-bit value
        :type operand_2: int
        :param operand_1_is_register: Indicates if operand_1 is a register ID
        :type operand_1_is_register: bool
        :param operand_2_is_register: Indicates if operand_2 is a register ID
        :type operand_2_is_register: bool
        :raise data_specification.exceptions.DataUndefinedWriterException: \
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException: \
            If a write to external storage fails
        :raise data_specification.exceptions.ParameterOutOfBoundsException: \
            * If operand_1_is_register is True and operand_1 is not a\
              valid register ID
            * If operand_2_is_register is True and operand_2 is not a\
              valid register ID
        """
        self._call_logic_operation(register_id, operand_1,
                                   LogicOperation.LEFT_SHIFT,
                                   operand_2, operand_1_is_register,
                                   operand_2_is_register)

    def logical_right_shift(self, register_id, operand_1, operand_2,
                            operand_1_is_register=False,
                            operand_2_is_register=False):
        """ Insert command to perform a logical right shift operation, using\
            the _call_logic_operation.

        :param register_id: The ID of the register to store the result in
        :type register_id: int
        :param operand_1:
            * If operand_1_is_register is True, the ID of a register\
              where the first operand can be found, between 0 and 15
            * If operand_1_is_register is False, a 32-bit value
        :type operand_1: int
        :param operand_2:
            * If operand_2_is_register is True, the ID of a register\
              where the second operand can be found. between 0 and 15
            * If operand_2_is_register is False, a 32-bit value
        :type operand_2: int
        :param operand_1_is_register: Indicates if operand_1 is a register ID
        :type operand_1_is_register: bool
        :param operand_2_is_register: Indicates if operand_2 is a register ID
        :type operand_2_is_register: bool
        :raise data_specification.exceptions.DataUndefinedWriterException: \
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException: \
            If a write to external storage fails
        :raise data_specification.exceptions.ParameterOutOfBoundsException: \
            * If operand_1_is_register is True and operand_1 is not a\
              valid register ID
            * If operand_2_is_register is True and operand_2 is not a\
              valid register ID
        """
        self._call_logic_operation(register_id, operand_1,
                                   LogicOperation.RIGHT_SHIFT,
                                   operand_2, operand_1_is_register,
                                   operand_2_is_register)

    def logical_xor(self, register_id, operand_1, operand_2,
                    operand_1_is_register=False, operand_2_is_register=False):
        """ Insert command to perform a logical xor operation, using
            the _call_logic_operation.

        :param register_id: The ID of the register to store the result in
        :type register_id: int
        :param operand_1:
            * If operand_1_is_register is True, the ID of a register\
              where the first operand can be found, between 0 and 15
            * If operand_1_is_register is False, a 32-bit value
        :type operand_1: int
        :param operand_2:
            * If operand_2_is_register is True, the ID of a register\
              where the second operand can be found. between 0 and 15
            * If operand_2_is_register is False, a 32-bit value
        :type operand_2: int
        :param operand_1_is_register: Indicates if operand_1 is a register ID
        :type operand_1_is_register: bool
        :param operand_2_is_register: Indicates if operand_2 is a register ID
        :type operand_2_is_register: bool
        :raise data_specification.exceptions.DataUndefinedWriterException: \
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException: \
            If a write to external storage fails
        :raise data_specification.exceptions.ParameterOutOfBoundsException: \
            * If operand_1_is_register is True and operand_1 is not a\
              valid register ID
            * If operand_2_is_register is True and operand_2 is not a\
              valid register ID
        """
        self._call_logic_operation(register_id, operand_1,
                                   LogicOperation.XOR,
                                   operand_2, operand_1_is_register,
                                   operand_2_is_register)

    def logical_not(self, register_id, operand, operand_is_register=False):
        """ Insert command to perform a logical xor operation, using
            the _call_logic_operation.

        :param register_id: The ID of the register to store the result in
        :type register_id: int
        :param operand:
            * If operand_is_register is True, the ID of a register where the\
              first operand can be found, between 0 and 15
            * If operand_is_register is False, a 32-bit value
        :type operand: int
        :param operand_is_register: Indicates if operand_1 is a register ID
        :type operand_is_register: bool
        :raise data_specification.exceptions.DataUndefinedWriterException: \
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException: \
            If a write to external storage fails
        :raise data_specification.exceptions.ParameterOutOfBoundsException: \
            * If operand_is_register is True and operand_1 is not a\
              valid register ID
        """
        self._call_logic_operation(register_id, operand, LogicOperation.NOT,
                                   0, operand_is_register, False)

    def _call_logic_operation(self, register_id, operand_1, operation,
                              operand_2, operand_1_is_register=False,
                              operand_2_is_register=False):
        """ Insert command to perform a logic operation on two signed or\
            unsigned values and store the result in a register

        :param register_id: The ID of the register to store the result in
        :type register_id: int
        :param operand_1:
            * If operand_1_is_register is True, the ID of a register\
              where the first operand can be found, between 0 and 15
            * If operand_1_is_register is False, a 32-bit value
        :type operand_1: int
        :param operation: The operation to perform
        :type operation: :py:class:`~LogicOperation`
        :param operand_2:
            * If operand_2_is_register is True, the ID of a register\
              where the second operand can be found. between 0 and 15
            * If operand_2_is_register is False, a 32-bit value
        :type operand_2: int
        :param operand_1_is_register: Indicates if operand_1 is a register ID
        :type operand_1_is_register: bool
        :param operand_2_is_register: Indicates if operand_2 is a register ID
        :type operand_2_is_register: bool
        :raise data_specification.exceptions.DataUndefinedWriterException: \
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException: \
            If a write to external storage fails
        :raise data_specification.exceptions.ParameterOutOfBoundsException: \
            * If operand_1_is_register is True and operand_1 is not a\
              valid register ID
            * If operand_2_is_register is True and operand_2 is not a\
              valid register ID
        :raise data_specification.exceptions.InvalidOperationException: \
            If operation is not a known operation
        """
        bit_field = 0x4
        register_op_1 = 0
        register_op_2 = 0
        payload = bytearray()

        if register_id < 0 or register_id >= MAX_REGISTERS:
            raise ParameterOutOfBoundsException(
                "register_id", register_id, 0, MAX_REGISTERS - 1,
                Commands.LOGIC_OP.name)

        cmd_string = "LOGIC_OP reg[{0:d}] =".format(register_id)

        if operation not in LogicOperation:
            raise InvalidOperationException(
                "logic", operation.value, Commands.LOGIC_OP.name)

        if operation.value == LogicOperation.NOT.value:
            cmd_string += " " + operation.operator

        if operand_1_is_register:
            if operand_1 < 0 or operand_1 >= MAX_REGISTERS:
                raise ParameterOutOfBoundsException(
                    "operand_1", operand_1, 0, MAX_REGISTERS - 1,
                    Commands.LOGIC_OP.name)
            bit_field |= 2
            register_op_1 = operand_1
            cmd_string += " reg[{0:d}]".format(register_op_1)
        else:
            if (operand_1 < DataType.UINT32.min or  # @UndefinedVariable
                    operand_1 > DataType.UINT32.max):  # @UndefinedVariable
                raise ParameterOutOfBoundsException(
                    "operand_1", operand_1,
                    DataType.UINT32.min,  # @UndefinedVariable
                    DataType.UINT32.max,  # @UndefinedVariable
                    Commands.LOGIC_OP.name)
            payload += bytearray(_ONE_WORD.pack(operand_1))
            cmd_string += " " + str(operand_1)

        if operation.value != LogicOperation.NOT.value:
            cmd_string += " " + operation.operator

            if operand_2_is_register:
                if operand_2 < 0 or operand_2 >= MAX_REGISTERS:
                    raise ParameterOutOfBoundsException(
                        "operand_2", operand_2, 0, MAX_REGISTERS - 1,
                        Commands.LOGIC_OP.name)
                bit_field |= 1
                register_op_2 = operand_2
                cmd_string += " reg[{0:d}]".format(register_op_2)
            else:
                if (operand_2 < DataType.UINT32.min or  # @UndefinedVariable
                        operand_2 > DataType.UINT32.max):  # @UndefinedVariable
                    raise ParameterOutOfBoundsException(
                        "operand_2", operand_2,
                        DataType.UINT32.min,  # @UndefinedVariable
                        DataType.UINT32.max,  # @UndefinedVariable
                        Commands.LOGIC_OP.name)
                payload += bytearray(_ONE_WORD.pack(operand_2))
                cmd_string += " " + str(operand_2)

        cmd_word = (
            (len(payload) << 26) |
            (Commands.LOGIC_OP.value << 20) |
            (bit_field << 16) |
            (register_id << 12) |
            (register_op_1 << 8) |
            (register_op_2 << 4) |
            operation.value)

        self.write_command_to_files(
            bytearray(_ONE_WORD.pack(cmd_word)) + payload, cmd_string)

    def copy_structure(self, source_structure_id, destination_structure_id,
                       source_id_is_register=False,
                       destination_id_is_register=False):
        """ Insert command to copy a structure, possibly overwriting another\
            structure

        :param source_structure_id:
            * If source_id_is_register is True, the ID of the register\
              holding the source structure ID, between 0 and 15
            * Otherwise, the ID of the source structure, between 0 and 15
        :type source_structure_id: int
        :param destination_structure_id:
            * If destination_id_is_register is True, the ID of the register\
              holding the destination structure ID, between 0 and 15
            * If destination_id_is_register is False, the ID of the\
              destination structure, between 0 and 15
        :type destination_structure_id: int
        :param source_id_is_register: \
            Indicates if source_structure_id is a register ID
        :type source_id_is_register: bool
        :param destination_id_is_register: \
            Indicates if destination_structure_id is a register ID
        :type destination_id_is_register: bool
        :return: The ID of the copied structure, between 0 and 15
        :rtype: int
        :raise data_specification.exceptions.DataUndefinedWriterException: \
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException: \
            If a write to external storage fails
        :raise data_specification.exceptions.ParameterOutOfBoundsException: \
            * If source_id_is_register is True and source_structure_id\
              is not a valid register ID
            * If destination_id_is_register is True and\
              destination_structure_id is not a valid register ID
            * If source_id_is_register is False and source_structure_id\
              is not a valid structure ID
            * If destination_id_is_register is False and\
              destination_structure_id is not a valid structure ID
        :raise data_specification.exceptions.NotAllocatedException: \
            * If no structure with ID source_structure_id has been allocated
        """
        bit_field = 0
        cmd_string = "COPY_STRUCT"

        if source_structure_id == destination_structure_id and \
                destination_id_is_register == source_id_is_register:
            raise DuplicateParameterException(
                "COPY_STRUCT",
                [source_structure_id, destination_structure_id])

        if source_id_is_register:
            if source_structure_id < 0 or source_structure_id >= MAX_REGISTERS:
                raise ParameterOutOfBoundsException(
                    "source_structure_id", source_structure_id, 0,
                    MAX_REGISTERS - 1, Commands.COPY_STRUCT.name)
            bit_field |= SRC1_ONLY
            cmd_string += " source_struct = reg[{0:d}]".format(
                source_structure_id)
        else:
            if source_structure_id < 0 \
                    or source_structure_id >= MAX_STRUCT_SLOTS:
                raise ParameterOutOfBoundsException(
                    "source_structure_id", source_structure_id, 0,
                    MAX_STRUCT_SLOTS - 1, Commands.COPY_STRUCT.name)
            if self.struct_slot[source_structure_id] == 0:
                raise NotAllocatedException(
                    "struct", source_structure_id, "COPY_STRUCT")
            cmd_string += " source_struct = {0:d}".format(source_structure_id)

        if destination_id_is_register:
            if destination_structure_id < 0 \
                    or destination_structure_id >= MAX_REGISTERS:
                raise ParameterOutOfBoundsException(
                    "destination_structure_id", destination_structure_id,
                    0, MAX_REGISTERS - 1, Commands.COPY_STRUCT.name)
            bit_field |= DEST_ONLY
            cmd_string += " destination_struct = reg[{0:d}]".format(
                destination_structure_id)
        else:
            if destination_structure_id < 0 \
                    or destination_structure_id >= MAX_STRUCT_SLOTS:
                raise ParameterOutOfBoundsException(
                    "destination_structure_id", destination_structure_id,
                    0, MAX_STRUCT_SLOTS - 1,
                    Commands.COPY_STRUCT.name)
            cmd_string += " destination_struct = {0:d}".format(
                destination_structure_id)

        cmd_word = (
            (LEN1 << 28) |
            (Commands.COPY_STRUCT.value << 20) |
            (bit_field << 16) |
            (destination_structure_id << 12) |
            (source_structure_id << 8))

        cmd_word_encoded = bytearray(_ONE_WORD.pack(cmd_word))
        cmd_word_list = cmd_word_encoded
        self.write_command_to_files(cmd_word_list, cmd_string)

    def copy_structure_parameter(self, source_structure_id,
                                 source_parameter_index,
                                 destination_id,
                                 destination_parameter_index=None,
                                 destination_is_register=False):
        """ Insert command to copy the value of a parameter from one\
            structure to another.

        :param source_structure_id: \
            The ID of the source structure, between 0 and 15
        :type source_structure_id: int
        :param source_parameter_index: \
            The index of the parameter in the source structure
        :type source_parameter_index: int
        :param destination_id: The ID of the destination structure, or the
            ID of the destination register, between 0 and 15
        :type destination_id: int
        :param destination_parameter_index: The index of the parameter in the\
            destination structure. Ignored when writing to a register.
        :type destination_parameter_index: int
        :return: Nothing is returned
        :param destination_is_register: \
            Indicates whether the destination is a structure or a register.
        :type destination_is_register: bool
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException: \
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException: \
            If a write to external storage fails
        :raise data_specification.exceptions.ParameterOutOfBoundsException: \
            * If source_structure_id is not a valid structure ID
            * If destination_id is not a valid structure ID
            * If source_parameter_index is not a valid parameter index\
              in the source structure
            * If destination_parameter_index is not a valid parameter\
              index in the destination structure
        :raise data_specification.exceptions.NotAllocatedException: \
            * If no structure with ID destination_id has been allocated
            * If no structure with ID source_structure_id has been allocated
        """
        if source_structure_id < 0 or source_structure_id >= MAX_STRUCT_SLOTS:
            raise ParameterOutOfBoundsException(
                "source_structure_id", source_structure_id, 0,
                MAX_STRUCT_SLOTS - 1, Commands.COPY_PARAM.name)

        if source_parameter_index < 0 \
                or source_parameter_index >= MAX_STRUCT_ELEMENTS:
            raise ParameterOutOfBoundsException(
                "source_parameter_index", source_parameter_index, 0,
                MAX_STRUCT_ELEMENTS - 1, Commands.COPY_PARAM.name)

        if self.struct_slot[source_structure_id] == 0:
            raise NotAllocatedException(
                "structure", source_structure_id, "COPY_PARAM")

        if (len(self.struct_slot[source_structure_id]) <=
                source_parameter_index):
            raise NotAllocatedException(
                "parameter", source_parameter_index, "COPY_PARAM")

        if not destination_is_register:
            if (destination_parameter_index < 0 or
                    destination_parameter_index >= MAX_STRUCT_ELEMENTS):
                raise ParameterOutOfBoundsException(
                    "destination_parameter_index", destination_parameter_index,
                    0, MAX_STRUCT_ELEMENTS - 1, Commands.COPY_PARAM.name)

            if destination_id < 0 or destination_id >= MAX_STRUCT_SLOTS:
                raise ParameterOutOfBoundsException(
                    "destination_structure_id", destination_id, 0,
                    MAX_STRUCT_SLOTS - 1, Commands.COPY_PARAM.name)

            if self.struct_slot[destination_id] == 0:
                raise NotAllocatedException(
                    "structure", destination_id, "COPY_PARAM")

            if (len(self.struct_slot[source_structure_id]) <=
                    source_parameter_index):
                raise NotAllocatedException(
                    "parameter", destination_parameter_index, "COPY_PARAM")

            if (len(self.struct_slot[destination_id]) <=
                    destination_parameter_index):
                raise NotAllocatedException(
                    "parameter", destination_parameter_index, "COPY_PARAM")

            if (self.struct_slot[source_structure_id]
                    [source_parameter_index][1] !=
                    self.struct_slot[destination_id]
                    [destination_parameter_index][1]):
                raise TypeMismatchException(
                    "COPY_PARAM")

            if (source_structure_id == destination_id and
                    destination_parameter_index == source_parameter_index):
                raise DuplicateParameterException(
                    "COPY_PARAM", [source_structure_id,
                                   source_parameter_index,
                                   destination_id,
                                   destination_parameter_index])

            cmd_word_1 = (
                (LEN2 << 28) |
                (Commands.COPY_PARAM.value << 20) |
                (NO_REGS << 16) |
                (destination_id << 12) |
                (source_structure_id << 8))
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
            if destination_id < 0 or destination_id >= MAX_REGISTERS:
                raise ParameterOutOfBoundsException(
                    "destination_register_id", destination_id, 0,
                    MAX_REGISTERS - 1, Commands.COPY_PARAM.name)

            cmd_word_1 = (
                (LEN2 << 28) |
                (Commands.COPY_PARAM.value << 20) |
                (DEST_ONLY << 16) |
                (destination_id << 12) |
                (source_structure_id << 8))
            cmd_word_2 = source_parameter_index

            cmd_string = "WRITE_PARAM source_structure_id = {0:d}, " \
                         "source_parameter_id = {1:d}, " \
                         "destination_register_id = {2:d}"\
                .format(source_structure_id,
                        source_parameter_index, destination_id)

        cmd_word_1_encoded = bytearray(_ONE_WORD.pack(cmd_word_1))
        cmd_word_2_encoded = bytearray(_ONE_WORD.pack(cmd_word_2))

        cmd_word_list = cmd_word_1_encoded + cmd_word_2_encoded

        self.write_command_to_files(cmd_word_list, cmd_string)

    def print_value(self, value, value_is_register=False,
                    data_type=DataType.UINT32):
        """ Insert command to print out a value (for debugging)

        :param value:
            * If value_is_register is True, the ID of the register containing\
              the value to print
            * If value_is_register is False, the value to print as a float
        :type value: float
        :param value_is_register: Indicates if the value is a register
        :type value_is_register: bool
        :param data_type: The type of the data to be printed
        :type data_type: :py:class:`~DataType`
        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException: \
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException: \
            If a write to external storage fails
        :raise data_specification.exceptions.ParameterOutOfBoundsException: \
            * If value_is_register is True and value is not a valid\
              register ID
            * If value_is_register is False, the data_type is an integer type\
              and value has a fractional part
            * If value_is_register is False and the value would overflow the\
              data type
        :raise data_specification.exceptions.UnknownTypeException: \
            * If data_type is not a valid data type
        """
        cmd_word_length = LEN1
        source_register_id = 0
        bit_field = 0
        data_encoded = bytearray()

        if value_is_register:
            if value < 0 or value >= MAX_REGISTERS:
                raise ParameterOutOfBoundsException(
                    "value", value, 0, MAX_REGISTERS - 1,
                    Commands.PRINT_VAL.name)
            bit_field |= 2
            source_register_id = value
            cmd_string = "PRINT_VAL reg[{0:d}]".format(source_register_id)
        else:
            if value < data_type.min or value > data_type.max:
                raise ParameterOutOfBoundsException(
                    "value", value, data_type.min, data_type.max,
                    Commands.PRINT_VAL.name)
            if data_type.size <= 4:
                cmd_word_length = LEN2
            else:
                cmd_word_length = LEN3
            data_encoding_string = "<{0:s}".format(data_type.struct_encoding)
            data_encoded = bytearray(struct.pack(data_encoding_string, value))
            while len(data_encoded) % 4:
                data_encoded += bytearray(_ONE_SBYTE.pack(0))
            cmd_string = "PRINT_VAL {0:d}".format(value)

        cmd_word = (
            (cmd_word_length << 28) |
            (Commands.PRINT_VAL.value << 20) |
            (bit_field << 16) |
            (source_register_id << 8) |
            data_type.value)
        cmd_word_encoded = bytearray(_ONE_WORD.pack(cmd_word))

        cmd_word_list = cmd_word_encoded + data_encoded

        self.write_command_to_files(cmd_word_list, cmd_string)

    def print_text(self, text, encoding="ASCII"):
        """ Insert command to print some text (for debugging)

        :param text: The text to write (max 12 characters)
        :type text: str
        :param encoding: \
            The character encoding to use for the string. Defaults to ASCII.
        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException: \
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException: \
            If a write to external storage fails
        """
        text_encoded = bytearray(text.encode(encoding=encoding))
        text_len = len(text_encoded)
        if text_len > 12:
            raise ParameterOutOfBoundsException(
                "len(text)", text_len, 1, 12, Commands.PRINT_TXT.name)

        if text_len <= 4:
            cmd_word_len = LEN2
        elif text_len <= 8:
            cmd_word_len = LEN3
        else:
            cmd_word_len = LEN4

        # add final padding to the encoded text
        if text_len % 4 is not 0:
            text_encoded += bytearray(4 - (text_len % 4))

        cmd_string = "PRINT_TXT \"{0:s}\"".format(text)

        cmd_word = (
            (cmd_word_len << 28) |
            (Commands.PRINT_TXT.value << 20) |
            (text_len - 1))
        cmd_word_encoded = bytearray(_ONE_WORD.pack(cmd_word))
        cmd_word_list = cmd_word_encoded + text_encoded

        self.write_command_to_files(cmd_word_list, cmd_string)

    def print_struct(self, structure_id, structure_id_is_register=False):
        """ Insert command to print out a structure (for debugging)

        :param structure_id:
            * If structure_id_is_register is True, the ID of the register\
              containing the ID of the structure to print, between 0 and 15
            * If structure_id_is_register is False, the ID of the structure\
              to print, between 0 and 15
        :type structure_id: int
        :param structure_id_is_register: \
            Indicates if the structure_id is a register
        :type structure_id_is_register: bool
        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException: \
            If the binary specification file writer has not been initialised
        :raise data_specification.exceptions.ParameterOutOfBoundsException: \
            * If structure_id_is_register is True and structure_id is not a\
              valid register ID
            * If structure_id_is_register is False and structure_id is not a\
              valid structure ID
        :raise data_specification.exceptions.NotAllocatedException: \
            If structure_id_is_register is False and structure_id is the ID\
            of a structure that has not been allocated
        """
        struct_register = 0
        bit_field = 0
        cmd_string = "PRINT_STRUCT"

        if structure_id_is_register:
            if structure_id < 0 or structure_id >= MAX_REGISTERS:
                raise ParameterOutOfBoundsException(
                    "structure_id", structure_id, 0,
                    MAX_REGISTERS - 1, Commands.PRINT_STRUCT.name)
            struct_register = structure_id
            structure_id = 0
            bit_field = 0x2
            cmd_string += " struct(reg[{0:d}])".format(struct_register)
        else:
            if structure_id < 0 or structure_id >= MAX_STRUCT_SLOTS:
                raise ParameterOutOfBoundsException(
                    "structure_id", structure_id, 0,
                    MAX_STRUCT_SLOTS - 1, Commands.PRINT_STRUCT.name)

            if self.struct_slot[structure_id] == 0:
                raise NotAllocatedException(
                    "structure", structure_id, "PRINT_STRUCT")

            cmd_string += " struct({0:d})".format(structure_id)

        cmd_word = (
            (LEN1 << 28) |
            (Commands.PRINT_STRUCT.value << 20) |
            (bit_field << 16) |
            (struct_register << 8) |
            structure_id)

        cmd_word_encoded = bytearray(_ONE_WORD.pack(cmd_word))
        cmd_word_list = cmd_word_encoded

        self.write_command_to_files(cmd_word_list, cmd_string)

    def end_specification(self, close_writer=True):
        """ Insert a command to indicate that the specification has finished\
            and finish writing

        :param close_writer: \
            Indicates whether to close the underlying writer(s)
        :type close_writer: bool
        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException: \
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException: \
            If a write to external storage fails
        """
        self.comment("\nEnd of specification:")

        cmd_word = (
            (LEN1 << 28) |
            (Commands.END_SPEC.value << 20))
        encoded_cmd_word = bytearray(_ONE_WORD.pack(cmd_word))
        parameter = -1
        encoded_parameter = _ONE_SINT.pack(parameter)
        cmd_word_list = encoded_cmd_word + encoded_parameter
        cmd_string = "END_SPEC"
        self.write_command_to_files(cmd_word_list, cmd_string)

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
        :raise data_specification.exceptions.DataUndefinedWriterException: \
            If the binary specification file writer has not been initialised
        :raise spinn_storage_handlers.exceptions.DataWriteException: \
            If a write to external storage fails
        """
        if self.spec_writer is None:
            raise DataUndefinedWriterException(
                "The spec file writer has not been initialised")
        elif cmd_word_list:
            self.spec_writer.write(cmd_word_list)

        if self.report_writer is not None:
            if outdent is True:
                self.txt_indent = min(self.txt_indent - 1, 0)
            indent_string = "   " * self.txt_indent
            if no_instruction_number is True:
                formatted_cmd_string = "{0:s}{1:s}\n".format(
                    indent_string, cmd_string)
            else:
                pc = "%8.8X" % self.instruction_counter
                formatted_cmd_string = "{}. {}{}\n".format(
                    pc, indent_string, cmd_string)
                self.instruction_counter += len(cmd_word_list)
            self.report_writer.write(formatted_cmd_string.encode("UTF-8"))
            if indent is True:
                self.txt_indent += 1
        return

    @property
    def region_sizes(self):
        """ A list of sizes of each region that has been reserved. Note that\
            the list will include 0s for each non-reserved region.
        """
        return [0 if slot == 0 else slot[0] for slot in self.mem_slot]
