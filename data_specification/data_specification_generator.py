from enums.data_type import DataType
from enums.commands import Commands
from data_specification import constants, exceptions
from spinn_machine import sdram
import logging
import struct
import math
import decimal


logger = logging.getLogger(__name__)


class DataSpecificationGenerator(object):
    """ Used to generate a data specification language file that can be\
        executed to produce a memory image
    """

    def __init__(self, spec_writer, magic=None, report_writer=None):
        """
        :param spec_writer: The object to write the specification to
        :type spec_writer: Implementation of\
            :py:class:`data_specification.abstract_data_writer.AbstractDataWriter`
        :param magic: Magic number to write to the header or None to use default
        :type magic: int
        :param report_writer: Determines if a text version of the specification\
            is to be written
        :type report_writer: Implementation of\
            :py:class:`data_specification.abstract_data_writer.AbstractDataWriter`
        :raise data_specification.exceptions.DataWriteException:\
            If a write to external storage fails
        """
        self.spec_writer = spec_writer
        self.report_writer = report_writer
        self.magic_number = magic
        self.txt_indent = 0
        self.instruction_counter = 0
        self.mem_slot = [0 for i in xrange(constants.MAX_MEM_REGIONS)]
        self.distribution_id = 0

    def comment(self, comment):
        """ Write a comment to the text version of the specification.\
            Note that this is ignored by the binary file
        
        :param comment: The comment to write
        :type comment: str
        :return: Nothing is returned
        :raise data_specification.exceptions.DataUndefinedWriterException:\
            If the binary specification file writer has not been initialized
        :raise data_specification.exceptions.DataWriteException:\
            If a write to external storage fails
        """
        self.write_command_to_files(bytearray(), comment, no_instruction_number=True)

    def define_break(self):
        """ Insert command to stop execution with an exception (for debugging)

        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException:\
            If the binary specification file writer has not been initialized
        :raise data_specification.exceptions.DataWriteException:\
            If a write to external storage fails
        """
        cmd_word = (constants.LEN1 << 28) | (Commands.DSG_BREAK.value << 20)
        encoded_cmd_word = bytearray(struct.pack("<I", cmd_word))
        cmd_word_list = encoded_cmd_word
        cmd_string = "BREAK"
        self.write_command_to_files(cmd_word_list, cmd_string)
        return

    def no_operation(self):
        """ Insert command to execute nothing
        
        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException:\
            If the binary specification file writer has not been initialized
        :raise data_specification.exceptions.DataWriteException:\
            If a write to external storage fails
        """
        cmd_word = (constants.LEN1 << 28) | (Commands.NOP.value << 20)
        encoded_cmd_word = bytearray(struct.pack("<I", cmd_word))
        cmd_word_list = encoded_cmd_word
        cmd_string = "NOP"
        self.write_command_to_files(cmd_word_list, cmd_string)
        return

    def reserve_memory_region(self, region, size, label=None, empty=False):
        """ Insert command to reserve a memory region
        
        :param region: The number of the region to reserve, from 0 to 15
        :type region: int
        :param size: The size to reserve for the region in bytes
        :type size: int
        :param label: An optional label for the region
        :type label: str
        :param empty: Specifies if the region will be left empty
        :type empty: bool
        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException:\
            If the binary specification file writer has not been initialized
        :raise data_specification.exceptions.DataWriteException:\
            If a write to external storage fails
        :raise data_specification.exceptions.DataSpecificationRegionInUseException:\
            If the region was already reserved
        :raise data_specification.exceptions.DataSpecificationParameterOutOfBoundsException:\
            If the region requested was out of the allowed range, or that the\
            size was too big to fit in SDRAM
        """
        if (region < 0) or (region >= constants.MAX_MEM_REGIONS):
            logger.error(
                "Error: Memory region requested ({0:d}) is out of range 0 to {1:d}.\n".format(
                    region, constants.MAX_MEM_REGIONS - 1))
            raise exceptions.DataSpecificationParameterOutOfBoundsException(
                "memory region identifier", region, 0,
                (constants.MAX_MEM_REGIONS - 1), Commands.RESERVE.name)

        if self.mem_slot[region] != 0:
            error_string = "Error: Requested memory region ({0:d}) ".format(
                region)
            error_string += "is already allocated.\n"
            logger.error(error_string)
            raise exceptions.DataSpecificationRegionInUseException(region)

        if size > sdram.SDRAM.DEFAULT_SDRAM_BYTES:
            raise exceptions.DataSpecificationParameterOutOfBoundsException(
                "memory size", size, 1,
                sdram.SDRAM.DEFAULT_SDRAM_BYTES,
                Commands.RESERVE.name)

        unfilled = False
        if empty:
            unfilled = True
        self.mem_slot[region] = [size, label, unfilled]

        # Length [29:28], command[27:20], field_use[18:16], unfilled[7],
        # region ID [4:0]:

        cmd_word = (constants.LEN2 << 28) | (Commands.RESERVE.value << 20) | \
                   (constants.NO_REGS << 16) | (unfilled << 7) | region
        encoded_cmd_word = bytearray(struct.pack("<I", cmd_word))
        encoded_size = bytearray(struct.pack("<I", size))
        cmd_word_list = encoded_cmd_word + encoded_size

        if unfilled:
            unfilled_string = "UNFILLED"
        else:
            unfilled_string = ""

        if label is None:
            cmd_string = "RESERVE memRegion={0:d} size={1:d} {2:s}".format(
                region, size, unfilled_string)
        else:
            cmd_string = "RESERVE memRegion={0:d} size={1:d} label='{2:s}' {3:s}".format(
                region, size, label, unfilled_string)
        # Send the command to the output files:
        self.write_command_to_files(cmd_word_list, cmd_string)

    def free_memory_region(self, region):
        """ Insert command to free a previously reserved memory region

        :param region: The number of the region to free, from 0 to 15
        :type region: int
        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException:\
            If the binary specification file writer has not been initialized
        :raise data_specification.exceptions.DataWriteException:\
            If a write to external storage fails
        :raise data_specification.exceptions.DataSpecificationNotAllocatedException:\
            If the region was not reserved
        :raise data_specification.exceptions.DataSpecificationParameterOutOfBoundsException:\
            If the region requested was out of the allowed range
        """
        raise exceptions.UnimplementedDSGCommand("free_memory_region")

    def declare_random_number_generator(self, rng_type, seed):
        """ Insert command to declare a random number generator

        :param rng_type: The type of the random number generator
        :type rng_type: :py:class:`RandomNumberGenerator`
        :param seed: The seed of the random number generator >= 0
        :type seed: int
        :return: The id of the created random number generator, between 0 and 15
        :rtype: int
        :raise data_specification.exceptions.DataUndefinedWriterException:\
            If the binary specification file writer has not been initialized
        :raise data_specification.exceptions.DataWriteException:\
            If a write to external storage fails
        :raise data_specification.exceptions.DataSpecificationNoMoreException:\
            If there is no more space for a new generator
        :raise data_specification.exceptions.DataSpecificationUnknownTypeException:\
            If the rng_type is not one of the allowed values
        :raise data_specification.exceptions.DataSpecificationParameterOutOfBoundsException:\
            If the seed is too big or too small
        """
        raise exceptions.UnimplementedDSGCommand("declare_random_number_generator")

#        if rng_type < 0 or rng_type >= constants.MAX_RNGS:
#            raise exceptions.DataSpecificationParameterOutOfBoundsException(
#                "random number generator type", rng_type, 0,
#                (constants.MAX_RNGS - 1), Commands.DECLARE_RNG.name)
#        # Source field is constant for now, may allow multiple different
#        # sources of random numbers later.
#        rng_source = 0x0
#        cmd_word = (constants.LEN2 << 28) | (Commands.DECLARE_RNG.value << 20)
#        cmd_word = cmd_word | (rng_type << 12) | (rng_source << 8)
#        cmd_word_list = [cmd_word, seed]
#        cmd_string = "DECLARE_RNG id={0:d}, source={1:d}, seed={2:d}".format(
#            rng_type, rng_source, seed)
#        self.write_command_to_files(cmd_word_list, cmd_string)

    def declare_uniform_random_distribution(self, rng_id, min_value, max_value):
        """ Insert commands to declare a uniform random distribution

        :param rng_id: The id of the random number generator, between 0 and 15
        :type rng_id: int
        :param min_value: The minimum value that should be returned from the\
            distribution between -32768.0 and max_value
        :type min_value: float
        :param max_value: The maximum value that should be returned from the\
            distribution between min_value and 32767.0
        :type max_value: float
        :return: The id of the created uniform random distribution to be used\
            in future calls of the distribution between 0 and 63
        :rtype: int
        :raise data_specification.exceptions.DataUndefinedWriterException:\
            If the binary specification file writer has not been initialized
        :raise data_specification.exceptions.DataWriteException:\
            If a write to external storage fails
        :raise data_specification.exceptions.DataSpecificationNoMoreException:\
            If there is no more space for a new random distribution
        :raise data_specification.exceptions.DataSpecificationNotAllocatedException:\
            If the requested rng_id has not been allocated
        :raise data_specification.exceptions.DataSpecificationParameterOutOfBoundsException:\
            If rng_id, min_value or max_value is out of range
        """
        raise exceptions.UnimplementedDSGCommand(
            "declare_uniform_random_distribution")

        # if self.distribution_id > 63:
        # raise exceptions.DataSpecificationNoMoreException(
        #                "Random distribution", self.distribution_id)
        #        cmd_word = (constants.LEN1 << 28) | \
        #                   (Commands.DECLARE_RANDOM_DIST.value << 20)
        #        cmd_word = cmd_word | (self.distribution_id << 8) | paramList
        #        cmd_word_list = [cmd_word]
        #        cmd_string= "DECLARE_RANDOM_DIST distId=%d, paramList=%d" \
        #               % (distId, paramList)
        #        self.writeCommandToFiles(cmd_word_list, cmd_string)

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
            If the binary specification file writer has not been initialized
        :raise data_specification.exceptions.DataWriteException:\
            If a write to external storage fails
        :raise data_specification.exceptions.DataSpecificationNotAllocatedException:\
            If the random distribution id was not previously declared
        :raise data_specification.exceptions.DataSpecificationParameterOutOfBoundsException:\
            If the distribution_id or register_id specified was out of range
        """
        raise exceptions.UnimplementedDSGCommand("call_random_distribution")

    def define_structure(self, parameters):
        """ Insert commands to define a data structure

        :param parameters: A list of between 1 and 255 tuples of (label,\
            data_type, value) where:
                * label is the label of the element (for debugging)
                * data_type is the data type of the element
                * value is the value of the element, or None if no value is to\
                  be assigned
        :type parameters: list of (str, :py:class:`DataType`, float)
        :return: The id of the new structure, between 0 and 15
        :rtype: int
        :raise data_specification.exceptions.DataUndefinedWriterException:\
            If the binary specification file writer has not been initialized
        :raise data_specification.exceptions.DataWriteException:\
            If a write to external storage fails
        :raise data_specification.exceptions.DataSpecificationNoMoreException:\
            If there are no more spaces for new structures
        :raise data_specification.exceptions.DataSpecificationParameterOutOfBoundsException:\
            * If there are an incorrect number of parameters
            * If the size of one of the tuples is incorrect
            * If one of the values to be assigned has an integer\
              data_type but has a fractional part
            * If one of the values to be assigned would overflow its\
              data_type
        :raise data_specification.exceptions.DataSpecificationUnknownTypeException:\
            If one of the data types in the structure is unknown
        """
        raise exceptions.UnimplementedDSGCommand("define_structure")

    def set_structure_value(self, structure_id, parameter_index, value,
                            value_is_register=False):
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
        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException:\
            If the binary specification file writer has not been initialized
        :raise data_specification.exceptions.DataWriteException:\
            If a write to external storage fails
        :raise data_specification.exceptions.DataSpecificationParameterOutOfBoundsException:\
            * If structure_id is not in the allowed range
            * If parameter_index is larger than the number of parameters\
              declared in the original structure
            * If value_is_register is False, and the data type of the structure\
              value is an integer, and the value has a fractional part
            * If value_is_register is False, and value would overflow the\
              position in the structure
            * If value_is_register is True, and value is not a valid register id
        :raise data_specification.exceptions.DataSpecificationNotAllocatedException:\
            If the structure requested has not been declared
        """
        raise exceptions.UnimplementedDSGCommand("set_structure_value")

    def write_structure(
            self, structure_id, repeats=1, repeats_is_register=False):
        """ Insert command to write a structure to the current write pointer,
        causing the current write pointer to move on by the number of
        bytes needed to represent the structure

        :param structure_id:
            * If called within a function, the id of the structure to write,\
              between 0 and 15
            * If called outside of a function, the id of the structure\
              argument, between 0 and 5
        :type structure_id: int
        :param repeats:
            * If repeats_is_register is True, the id of the register containing\
              the number of repeats, between 0 and 15
            * If repeats_is_register is False, the number of repeats to write,\
              between 0 and 255
        :type repeats: int
        :param repeats_is_register: Identifies if repeats identifies a register
        :type repeats_is_register: bool
        :return: The position of the write pointer within the current region,\
            in bytes from the start of the region
        :rtype: int
        :raise data_specification.exceptions.DataUndefinedWriterException:\
            If the binary specification file writer has not been initialized
        :raise data_specification.exceptions.DataWriteException:\
            If a write to external storage fails
        :raise data_specification.exceptions.DataSpecificationParameterOutOfBoundsException:\
            * If repeats_is_register is False and structure_id is not\
              a valid id
            * If repeats_is_register is True and structure_id
            * If the number of repeats is out of range
        :raise data_specification.exceptions.DataSpecificationNotAllocatedException:\
            If the structure requested has not been declared
        :raise data_specification.exceptions.DataSpecificationNoRegionSelectedException:\
            If no region has been selected to write to
        :raise data_specification.exceptions.DataSpecificationRegionExhaustedException:\
            If the selected region has no more space
        """
        raise exceptions.UnimplementedDSGCommand("write_structure")

    def start_function(self, argument_by_value):
        """ Insert command to start a function definition, with up to 5\
        arguments, which are the ids of structures to be used within the\
        function, each of which can be passed by reference or by value.\
        In the commands following this command up to the end_function\
        command, structures can only be referenced using the numbers 1 to 5\
        which address the arguments, rather than the original structure ids

        :param argument_by_value: A list of up to 5 booleans indicating if the\
            structure to be passed as an argument is to be passed by\
            reference (i.e. changes made within the function are\
            persisited) or by value (i.e. changes made within the\
            function are lost when the function exits.  The number of\
            arguments is determined by the length of this list.
        :type argument_by_value: list of bool
        :return: The id of the function, between 0 and 31
        :rtype: int
        :raise data_specification.exceptions.DataUndefinedWriterException:\
            If the binary specification file writer has not been initialized
        :raise data_specification.exceptions.DataWriteException:\
            If a write to external storage fails
        :raise data_specification.exceptions.DataSpecificationNoMoreException:\
            If there are no more spaces for new functions
        :raise data_specification.exceptions.DataSpecificationParameterOutOfBoundsException:\
            If there are too many items in the list of arguments
        :raise data_specification.exceptions.DataSpecificationInvalidCommandException:\
            If there is already a function being defined at this point
        """
        raise exceptions.UnimplementedDSGCommand("start_function")

    def end_function(self):
        """ Insert command to mark the end of a function definition

        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException:\
            If the binary specification file writer has not been initialized
        :raise data_specification.exceptions.DataWriteException:\
            If a write to external storage fails
        :raise data_specification.exceptions.DataSpecificationInvalidCommandException:\
            If there is no function being defined at this point
        """
        raise exceptions.UnimplementedDSGCommand("end_function")

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
            If the binary specification file writer has not been initialized
        :raise data_specification.exceptions.DataWriteException:\
            If a write to external storage fails
        :raise data_specification.exceptions.DataSpecificationParameterOutOfBoundsException:\
            * If the function id is not valid
            * If any of the structure ids are not valid
        :raise data_specification.exceptions.DataSpecificationNotAllocatedException:\
            * If a function has not been defined with the given id
            * If no structure has been defined with one of the ids in\
              structure_ids
        """
        raise exceptions.UnimplementedDSGCommand("call_function")

    def write_value(
            self, data, repeats=1, repeats_register=None,
            data_type=DataType.UINT32):
        """ Insert command to write a value one or more times to the current
        write pointer, causing the write pointer to move on by the number
        of bytes required to represent the data type. The data is passed as a
        parameter to this function

        :param data: the data to write as a float.
        :type data: float
        :param repeats:
            * If repeats_register is None, this parameter identifies the\
              number of times to repeat the data, between 1 and 255\
              (default 1)
            * If repeats_register is not None (i.e. has an integer value), the
              content of this parameter is disregarded
        :type repeats: int
        :param repeats_register: Identifies the register containing the number\
                                 of repeats of the value to write
        :type repeats_register: None or int
        :param data_type: the type to convert data to
        :type data_type: :py:class:`DataType`
        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException:\
            If the binary specification file writer has not been initialized
        :raise data_specification.exceptions.DataWriteException:\
            If a write to external storage fails
        :raise data_specification.exceptions.DataSpecificationParameterOutOfBoundsException:\
            * If repeats_register is None, and repeats is out of range
            * If repeats_register is not a valid register id
            * If data_type is an integer type, and data has a fractional part
            * If data would overflow the data type
        :raise data_specification.exceptions.DataSpecificationUnknownTypeException:\
            If the data type is not known
        :raise data_specification.exceptions.DataSpecificationInvalidSizeException:\
            If the data size is invalid
        :raise data_specification.exceptions.DataSpecificationNoRegionSelectedException:\
            If no region has been selected to write to
        :raise data_specification.exceptions.DataSpecificationRegionExhaustedException:\
            If the selected region has no more space
        """
        if data_type not in DataType:
            raise exceptions.DataSpecificationUnknownTypeException(
                data_type, data, Commands.WRITE.name)

        data_size = data_type.size
        if data_size == 1:
            cmd_data_len = constants.LEN1
            data_len = 0
        elif data_size == 2:
            cmd_data_len = constants.LEN1
            data_len = 1
        elif data_size == 4:
            cmd_data_len = constants.LEN1
            data_len = 2
        elif data_size == 8:
            cmd_data_len = constants.LEN2
            data_len = 3
        else:
            raise exceptions.DataSpecificationInvalidSizeException(
                data_type.name, data_size, Commands.WRITE.name)

        if repeats_register is None:
            if (repeats < 0) or (repeats > 255):
                raise exceptions.DataSpecificationParameterOutOfBoundsException(
                    "repeats", repeats, 0, 255, Commands.WRITE.name)
        else:
            if (repeats_register < 0) or (
                        repeats_register >= constants.MAX_REGISTERS):
                raise exceptions.DataSpecificationParameterOutOfBoundsException(
                    "repeats_register", repeats_register, 0,
                    (constants.MAX_REGISTERS - 1), Commands.WRITE.name)

        if (data_type.min > data) or (data_type.max < data):
            raise exceptions.DataSpecificationParameterOutOfBoundsException(
                "data", data, data_type.min, data_type.max,
                Commands.WRITE.name)

        parameters = 0
        cmd_string = "WRITE data=0x%8.8X"%(data)

        if repeats_register is not None:
            repeat_reg_usage = 1
            parameters |= (repeats_register << 4)
            cmd_string = "{0:s}, repeats=reg[{1:d}]".format(cmd_string,
                                                            repeats_register)
        else:
            repeat_reg_usage = 0
            parameters |= repeats
            cmd_string = "{0:s}, repeats={1:d}".format(cmd_string, repeats)

        cmd_word = (cmd_data_len << 28) | (Commands.WRITE.value << 20) | \
                   (repeat_reg_usage << 16) | (data_len << 12) | parameters

        encoded_cmd_word = bytearray(struct.pack("<I", cmd_word))

        data_format = "<{0:s}".format(data_type.struct_encoding)
        data_value = decimal.Decimal(data) * data_type.scale
        data_encoded = bytearray(struct.pack(data_format, data_value))

        if data_type.size == 1:
            data_encoded.append([0,0,0])
        elif data_type.size == 2:
            data_encoded.append([0,0])

        cmd_word_list = encoded_cmd_word + data_encoded
        cmd_string = "{0:s}, dataType={1:s}".format(cmd_string, data_type.name)
        self.write_command_to_files(cmd_word_list, cmd_string)

    def write_value_from_register(
            self, data_register, repeats=1, repeats_register=None,
            data_type=DataType.UINT32):
        """ Insert command to write a value one or more times to the current
        write pointer, causing the write pointer to move on by the number
        of bytes required to represent the data type. The data is contained in
        a register whose id is passed to the function

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
        :param repeats_register: Identifies the register containing the number\
            of repeats of the value to write
        :type repeats_register: None or int
        :param data_type: the type of the data held in the register
        :type data_type: :py:class:`DataType`
        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException:\
            If the binary specification file writer has not been initialized
        :raise data_specification.exceptions.DataWriteException:\
            If a write to external storage fails
        :raise data_specification.exceptions.DataSpecificationParameterOutOfBoundsException:\
            * If repeats_register is None, and repeats is out of range
            * If repeats_register is not a valid register id
            * If data_register is not a valid register id
        :raise data_specification.exceptions.DataSpecificationUnknownTypeException:\
            If the data type is not known
        :raise data_specification.exceptions.DataSpecificationNoRegionSelectedException:\
            If no region has been selected to write to
        :raise data_specification.exceptions.DataSpecificationRegionExhaustedException:\
            If the selected region has no more space
        """
        if data_type not in DataType:
            raise exceptions.DataSpecificationUnknownTypeException(
                data_type, 0, Commands.WRITE.name)

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
            raise exceptions.DataSpecificationInvalidSizeException(
                data_type.name, data_size, Commands.WRITE.name)

        if repeats_register is None:
            if (repeats < 0) or (repeats > 255):
                raise exceptions.DataSpecificationParameterOutOfBoundsException(
                    "repeats", repeats, 0, 255, Commands.WRITE.name)
        else:
            if (repeats_register < 0) or (
                        repeats_register >= constants.MAX_REGISTERS):
                raise exceptions.DataSpecificationParameterOutOfBoundsException(
                    "repeats_register", repeats_register, 0,
                    (constants.MAX_REGISTERS - 1), Commands.WRITE.name)

        if (data_register < 0) or (data_register >= constants.MAX_REGISTERS):
            raise exceptions.DataSpecificationParameterOutOfBoundsException(
                "data_register", data_register, 0,
                (constants.MAX_REGISTERS - 1), Commands.WRITE.name)

        cmd_len = 0
        parameters = 0
        data_reg = 1
        cmd_string = "WRITE data=reg[{0:d}]".format(data_register)

        if repeats_register is not None:
            repeat_reg_usage = 1
            parameters |= (repeats_register << 4)
            cmd_string = "{0:s}, repeats=reg[{1:d}]".format(cmd_string,
                                                            repeats_register)
        else:
            repeat_reg_usage = 0
            parameters |= repeats
            cmd_string = "{0:s}, repeats={1:u}".format(cmd_string, repeats)

        cmd_word = (cmd_len << 28) | (Commands.WRITE.value << 20) | \
                   (data_reg << 17) | (repeat_reg_usage << 16) | \
                   (cmd_data_len << 12) | (data_register << 8) | parameters
        encoded_cmd_word = bytearray(struct.pack("<I", cmd_word))
        cmd_word_list = encoded_cmd_word
        cmd_string = "{0:s}, dataType={1:s}".format(cmd_string, data_type.name)
        self.write_command_to_files(cmd_word_list, cmd_string)

    def write_array(self, array_values):
        """ Insert command to write an array of words, causing the write pointer
        to move on by (4 * the array size), in bytes

        :param array: An array of words to be written
        :type array: array
        :return: The position of the write pointer within the current region,\
            in bytes from the start of the region
        :rtype: int
        :raise data_specification.exceptions.DataUndefinedWriterException:\
            If the binary specification file writer has not been initialized
        :raise data_specification.exceptions.DataWriteException:\
            If a write to external storage fails
        :raise data_specification.exceptions.DataSpecificationNoRegionSelectedException:\
            If no region has been selected to write to
        :raise data_specification.exceptions.DataSpecificationRegionExhaustedException:\
            If the selected region has no more space
        """
        cmd_len = 0xF
        cmd_word = (cmd_len << 28) | (Commands.WRITE_ARRAY.value << 20)
        len_array = len(array_values)
        size = len_array + 1

        encoded_cmd_word = bytearray(struct.pack("<I", cmd_word))
        encoded_size = bytearray(struct.pack("<I", size))

        encoded_array = bytearray()
        cmd_string = "WRITE_ARRAY, %d elements:\n" % len_array
        index = 0
        for i in array_values:
            cmd_string += "%16d %8.8X\n" % (index, i)
            index += 1
            encoded_array += bytearray(struct.pack("<I", i))

        cmd_word_list = encoded_cmd_word + encoded_size + encoded_array

        self.write_command_to_files(cmd_word_list, cmd_string)

    def switch_write_focus(self, region):
        """ Insert command to switch the region being written to

        :param region: The id of the region to switch to, between 0 and 15
        :type region: int
        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException:\
            If the binary specification file writer has not been initialized
        :raise data_specification.exceptions.DataWriteException:\
            If a write to external storage fails
        :raise data_specification.exceptions.DataSpecificationParameterOutOfBoundsException:\
            If the region identifier is not valid
        :raise data_specification.exceptions.DataSpecificationNotAllocatedException:\
            If the region has not been allocated
        :raise data_specification.exceptions.DataSpecificationRegionUnfilledException:\
            If the selected region should not be filled
        """
        if region < 0 or region >= constants.MAX_MEM_REGIONS:
            raise exceptions.DataSpecificationParameterOutOfBoundsException(
                "region", region, 0, (constants.MAX_MEM_REGIONS - 1),
                Commands.SWITCH_FOCUS.name)

        if self.mem_slot[region] == 0:
            raise exceptions.DataSpecificationNotAllocatedException(
                "region", region, Commands.SWITCH_FOCUS.name)

        if self.mem_slot[region][2]:
            raise exceptions.DataSpecificationRegionUnfilledException(
                region, Commands.SWITCH_FOCUS.name)

        reg_usage = 0x0
        parameters = region & 0xF
        cmd_string = "SWITCH_FOCUS memRegion = {0:d}".format(region)

        # Write command to switch focus:
        cmd_word = (constants.LEN1 << 28) | \
                   (Commands.SWITCH_FOCUS.value << 20) | \
                   (reg_usage << 16) | \
                   (parameters << 8)

        encoded_cmd_word = bytearray(struct.pack("<I", cmd_word))

        cmd_word_string = encoded_cmd_word
        self.write_command_to_files(cmd_word_string, cmd_string)

    def start_loop(self, counter_register_id, start, end, increment=1,
                   start_is_register=False, end_is_register=False,
                   increment_is_register=False):
        """ Insert command to start a loop

        :param counter_register_id: The id of the register to use as the loop\
            counter, between 0 and 15
        :type counter_register_id: int
        :param start:
            * If start_is_register is False, the number at which to\
              start the loop counter, >= 0
            * If start_is_register is True, the id of the register\
              containing the number at which to start the loop counter,\
              between 0 and 15
        :type start: int
        :param end:
            * If end_is_register is False, the number which the loop\
              counter must reach to stop the loop i.e. the loop will\
              run while the contents of counter_register < end, >= 0
            * If end_is_register is True, the id of the register\
              containing the number at which to stop the loop,\
              between 0 and 15
        :type end: int
        :param increment:
            * If increment_is_register is False, the amount by which to\
              increment the loop counter on each run of the loop, >= 0
            * If increment_is_register is True, the id of the register\
              containing the amount by which to increlement the loop\
              counter on each run of the loop, betwen 0 and 15
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
            If the binary specification file writer has not been initialized
        :raise data_specification.exceptions.DataWriteException:\
            If a write to external storage fails
        :raise data_specification.exceptions.DataSpecificationParameterOutOfBoundsException:\
            * If counter_register_id is not a valid register id
            * If start_is_register is True and increment is not a valid\
              register_id
            * If end_is_register is True and increment is not a valid\
              register_id
            * If increment_is_register is True, and increment is not a
              valid register_id
            * If start_is_register is False and start is not in the\
              allowed range
            * If end_is_register is False and end is not in the\
              allowed range
            * If increment_is_register is False and increment is not\
              in the allowed range
        """
        raise exceptions.UnimplementedDSGCommand("start_loop")

    def break_loop(self):
        """ Insert command to break out of a loop before it has completed

        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException:\
            If the binary specification file writer has not been initialized
        :raise data_specification.exceptions.DataWriteException:\
            If a write to external storage fails
        :raise data_specification.exceptions.DataSpecificationInvalidCommandException:\
            If there is no loop in operation at this point
        """
        raise exceptions.UnimplementedDSGCommand("break_loop")

    def end_loop(self):
        """ Insert command to indicate that this is the end of the loop.\
        Commands between the start of the loop and this command will be\
        repeated.

        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException:\
            If the binary specification file writer has not been initialized
        :raise data_specification.exceptions.DataWriteException:\
            If a write to external storage fails
        :raise data_specification.exceptions.DataSpecificationInvalidCommandException:\
            If there is no loop in operation at this point
        """
        raise exceptions.UnimplementedDSGCommand("end_loop")

    def start_conditional(self, register_id, condition, value,
                          value_is_register=False):
        """ Insert command to start a conditional if...then...else construct.\
        If the condition evaluates to true, the statement is executed up to\
        the next else statement, or the end of the conditional, whichever\
        comes first.

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
            If the binary specification file writer has not been initialized
        :raise data_specification.exceptions.DataWriteException:\
            If a write to external storage fails
        :raise data_specification.exceptions.DataSpecificationParameterOutOfBoundsException:\
            * If the register_id is not a valid register id
            * if value_is_register is True and value is not a valid\
              register id
        :raise data_specification.exceptions.DataSpecificationUnknownTypeException:\
            If the condition is not a valid condition
        """
        raise exceptions.UnimplementedDSGCommand("start_conditional")

    def else_conditional(self):
        """ Insert command for the else of an if...then...else construct.\
        If the condition of the conditional evaluates to false, the\
        statements up between the conditional and the insertion of this\
        "else" are skipped, and the statements from this point until the\
        end of the conditional are executed.

        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException:\
            If the binary specification file writer has not been initialized
        :raise data_specification.exceptions.DataWriteException:\
            If a write to external storage fails
        :raise data_specification.exceptions.DataSpecificationInvalidCommandException:\
            If there is no conditional in operation at this point
        """
        raise exceptions.UnimplementedDSGCommand("else_conditional")

    def end_conditional(self):
        """ Insert command to mark the end of an if...then...else construct

        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException:\
            If the binary specification file writer has not been initialized
        :raise data_specification.exceptions.DataWriteException:\
            If a write to external storage fails
        :raise data_specification.exceptions.DataSpecificationInvalidCommandException:\
            If there is no conditional in operation at this point
        """
        raise exceptions.UnimplementedDSGCommand("end_conditional")

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
            If the binary specification file writer has not been initialized
        :raise data_specification.exceptions.DataWriteException:\
            If a write to external storage fails
        :raise data_specification.exceptions.DataSpecificationParameterOutOfBoundsException:\
            * If register_id is not a valid register_id
            * If data_is_register is True, and data is not a valid\
              register id
            * If data_is_register is False, data_type is an integer\
              type and data has a fractional part
            * If data_is_register if False, and data would overflow the\
              data type
        :raise data_specification.exceptions.DataSpecificationUnknownTypeException:\
            If the data type is not known
        """
        raise exceptions.UnimplementedDSGCommand("set_register_value")

    def save_write_pointer(self, register_id):
        """ Insert command to save the write pointer to a register

        :param register_id: The id of the register to assign, between 0 and 15
        :type register_id: int
        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException:\
            If the binary specification file writer has not been initialized
        :raise data_specification.exceptions.DataWriteException:\
            If a write to external storage fails
        :raise data_specification.exceptions.DataSpecificationParameterOutOfBoundsException:\
            If the register_id is not a valid register id
        :raise data_specification.exceptions.DataSpecificationNoRegionSelectedException:\
            If no region has been selected
        """
        raise exceptions.UnimplementedDSGCommand("save_write_pointer")

    def set_write_pointer(self, address, address_is_register=False,
                          relative_to_current=False):
        """ Insert command to set the position of the write pointer within the
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
            If the binary specification file writer has not been initialized
        :raise data_specification.exceptions.DataWriteException:\
            If a write to external storage fails
        :raise data_specification.exceptions.DataSpecificationParameterOutOfBoundsException:\
            If the address_is_register is True and address is not a valid\
            register id
        :raise data_specification.exceptions.DataSpecificationRegionOutOfBoundsException:\
            If the move of the pointer would put it outside of the\
            current region
        :raise data_specification.exceptions.DataSpecificationNoRegionSelectedException:\
            If no region has been selected
        """
        raise exceptions.UnimplementedDSGCommand("set_write_pointer")

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
        :param return_register_id: The id of a register where the write pointer\
            will be written to once it has been updated, between\
            0 and 15or None if no such writing is to be done
        :type return_register_id: int
        :return: The current write pointer within the current region, in bytes\
            from the start of the region
        :rtype: int
        :raise data_specification.exceptions.DataUndefinedWriterException:\
            If the binary specification file writer has not been initialized
        :raise data_specification.exceptions.DataWriteException:\
            If a write to external storage fails
        :raise data_specification.exceptions.DataSpecificationParameterOutOfBoundsException:\
            * If log_block_size_is_register is False, and\
              log_block_size is not within the allowed range
            * If log_block_size_is_register is True and log_block_size\
              is not a valid register id
        :raise data_specification.exceptions.DataSpecificationRegionOutOfBoundsException:\
            If the move of the pointer would put it outside of the\
            current region
        :raise data_specification.exceptions.DataSpecificationNoRegionSelectedException:\
            If no region has been selected
        """
        raise exceptions.UnimplementedDSGCommand("align_write_pointer")

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
            initialized
        :raise data_specification.exceptions.DataWriteException:\
            If a write to external storage fails
        :raise data_specification.exceptions.DataSpecificationParameterOutOfBoundsException:\
            * If operand_1_is_register is True and operand_1 is not a\
              valid register id
            * If operand_2_is_register is True and operand_2 is not a\
              valid register id
        :raise data_specification.exceptions.DataSpecificationUnknownTypeException:\
            If operation is not a known operation
        """
        raise exceptions.UnimplementedDSGCommand("call_arthmetic_operation")

    def call_logic_operation(self, register_id, operand_1, operation,
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
            If the binary specification file writer has not been initialized
        :raise data_specification.exceptions.DataWriteException:\
            If a write to external storage fails
        :raise data_specification.exceptions.DataSpecificationParameterOutOfBoundsException:\
            * If operand_1_is_register is True and operand_1 is not a\
              valid register id
            * If operand_2_is_register is True and operand_2 is not a\
              valid register id
        :raise data_specification.exceptions.DataSpecificationUnknownTypeException:\
            If operation is not a known operation
        """
        raise exceptions.UnimplementedDSGCommand("call_logic_operation")

    def copy_structure(self, source_structure_id, destination_structure_id=None,
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
            * If None, indicates that the copy should be to a new\
              structure id
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
            If the binary specification file writer has not been initialized
        :raise data_specification.exceptions.DataWriteException:\
            If a write to external storage fails
        :raise data_specification.exceptions.DataSpecificationParameterOutOfBoundsException:\
            * If source_id_is_register is True and source_structure_id\
              is not a valid register id
            * If destination_id_is_register is True and\
              destination_structure_id is not a valid register id
            * If source_id_is_register is False and source_structure_id\
              is not a valid structure id
            * If destination_id_is_register is False and\
              destination_structure_id is not a valid structure id
        :raise data_specification.exceptions.DataSpecificationNoMoreException:\
            If destination_structure_id is None and there are no more\
            structure ids
        :raise data_specification.exceptions.DataSpecificationNotAllocatedException:\
            * If destination_structure_id is not None and no structure\
              with id destination_structure_id has been allocated
            * If no structure with id source_structure_id has been\
              allocated
        """
        raise exceptions.UnimplementedDSGCommand("copy_structure")

    def copy_structure_parameter(self, source_structure_id,
                                 source_parameter_index,
                                 destination_structure_id,
                                 destination_parameter_index):
        """ Insert command to copy the value of a parameter from one structure
        to another
        
        :param source_structure_id: The id of the source structure,\
            between 0 and 15
        :type source_structure_id: int
        :param source_parameter_index: The index of the parameter in the source\
            structure
        :type source_parameter_index: int
        :param destination_structure_id: The id of the destination structure,
            between 0 and 15
        :type destination_structure_id: int
        :param destination_parameter_index: The index of the parameter in the\
            destination structure
        :type destination_parameter_index: int
        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException:\
            If the binary specification file writer has not been initialized
        :raise data_specification.exceptions.DataWriteException:\
            If a write to external storage fails
        :raise data_specification.exceptions.DataSpecificationParameterOutOfBoundsException:\
            * If source_structure_id is not a valid structure id
            * If destination_structure_id is not a valid structure id
            * If source_parameter_index is not a valid parameter index\
              in the source structure
            * If destination_parameter_index is not a valid parameter\
              index in the destination structure
        :raise data_specification.exceptions.DataSpecificationInvalidTypeException:\
            If the source and destination data types do not match
        :raise data_specification.exceptions.DataSpecificationNotAllocatedException:\
            * If no structure with id destination_structure_id has been\
              allocated
            * If no structure with id source_structure_id has been
              allocated
        """
        raise exceptions.UnimplementedDSGCommand("copy_structure_parameter")

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
            If the binary specification file writer has not been initialized
        :raise data_specification.exceptions.DataWriteException:\
            If a write to external storage fails
        :raise data_specification.exceptions.DataSpecificationParameterOutOfBoundsException:\
            * If value_is_register is True and value is not a valid\
              register id
            * If value_is_register is False, the data_type is an
              integer type and value has a fractional part
            * If value_is_register is False and the value would
              overflow the data type
        :raise data_specification.exceptions.DataSpecificationUnknownTypeException:\
            * If data_type is not a vaild data type
        """
        raise exceptions.UnimplementedDSGCommand("print_value")

    def print_text(self, text):
        """ Insert command to print some text (for debugging)
        
        :param text: The text to write
        :type text: str
        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException:\
            If the binary specification file writer has not been initialized
        :raise data_specification.exceptions.DataWriteException:\
            If a write to external storage fails
        """
        raise exceptions.UnimplementedDSGCommand("print_text")

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
            initialized
        :raise data_specification.exceptions.DataWriteException:\
            If a write to external storage fails
        :raise data_specification.exceptions.DataSpecificationParameterOutOfBoundsException:\
            * If structure_id_is_register is True and structure_id is\
              not a valid register id
            * If structure_id_is_register is False and structure_id is\
              not a valid structure id
        :raise data_specification.exceptions.DataSpecificationNotAllocatedException:\
            If structure_id_is_register is False and structure_id is\
            is the id of a structure that has not been allocated
        """
        raise exceptions.UnimplementedDSGCommand("print_struct")

    def end_specification(self, close_writer=True):
        """ Insert a command to indicate that the specification has finished\
        and finish writing
        
        :param close_writer: Indicates whether to close the underlying writer(s)
        :type close_writer: bool
        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException:\
            If the binary specification file writer has not been initialized
        :raise data_specification.exceptions.DataWriteException:\
            If a write to external storage fails
        """
        self.comment("\nEnd of specification:")

        cmd_word = (constants.LEN1 << 28) | \
                   (Commands.END_SPEC.value << 20)
        encoded_cmd_word = bytearray(struct.pack("<I", cmd_word))
        cmd_word_list = encoded_cmd_word
        cmd_string = "END_SPEC"
        self.write_command_to_files(cmd_word_list, cmd_string)

        if close_writer:
            self.spec_writer.close()
            if self.report_writer is not None:
                self.report_writer.close()

    def write_command_to_files(self, cmd_word_list, cmd_string, indent=False,
                               outdent=False, no_instruction_number=False):
        """
        Writes the binary command to the binary output file and, if the
        user has requested a text output for debug purposes, also write the
        text version to the text file.
        Setting the optional parameter 'indent' to True causes subsequent
        commands to be indented by two spaces relative to this one.
        Similarly, setting 'outdent' to True, reverses this spacing.

        :param cmd_word_list: list of binary words to be added to the binary\
            data specification file
        :type cmd_word_list: bytearray
        :param cmd_string: string describing the command to be added to the\
            report for the data specification file
        :type cmd_string: str
        :param indent: if the following lines need to be indented
        :type indent: bool
        :param outdent: if the following lines need to be outdented
        :type outdent: bool
        :param no_instruction_number: if each report line should include also\
            the address of the command in the file
        :param no_instruction_number: bool
        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataUndefinedWriterException:\
            If the binary specification file writer has not been initialized
        :raise data_specification.exceptions.DataWriteException:\
            If a write to external storage fails
        """

        if self.spec_writer is None:
            raise exceptions.DataUndefinedWriterException(
                "The spec file writer has not been initialized")
        elif len(cmd_word_list) > 0:
            self.spec_writer.write(cmd_word_list)

        if self.report_writer is not None:
            if outdent is True:
                self.txt_indent -= 1
                if self.txt_indent < 0:
                    self.txt_indent = 0
            if no_instruction_number is True:
                formatted_cmd_string = "%s%s\n" % (
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
