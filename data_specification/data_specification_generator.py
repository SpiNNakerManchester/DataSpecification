from enum import Enum


class DataType(Enum):
    """ Supported data types
    """
    UINT8 = (0, "8-bit unsigned integer")
    UINT16 = (1, "16-bit unsigned integer")
    UINT32 = (2, "32-bit unsigned integer")
    UINT64 = (3, "64-bit unsigned integer")
    INT8 = (4, "8-bit signed integer")
    INT16 = (5, "16-bit signed integer")
    INT32 = (6, "32-bit signed integer")
    INT64 = (7, "64-bit signed integer")
    U88 = (8, "8.8 unsigned fixed point number")
    U1616 = (9, "16.16 unsigned fixed point number")
    U3232 = (10, "32.32 unsigned fixed point number")
    S87 = (11, "8.7 signed fixed point number")
    S1615 = (12, "16.15 signed fixed point number")
    S3231 = (13, "32.31 signed fixed point number") 
    U08 = (16, "0.8 unsigned fixed point number")
    U016 = (17, "0.16 unsigned fixed point number")
    U032 = (18, "0.32 unsigned fixed point number")
    U064 = (19, "0.64 unsigned fixed point number")
    S07 = (20, "0.7 signed fixed point number")
    S015 = (21, "0.15 signed fixed point number")
    S031 = (22, "0.32 signed fixed point number")
    S063 = (23, "0.63 signed fixed point number")
    
    def __init__(self, value, doc=""):
        self._value_ = value
        self.__doc__ = doc
   
     
class RandomNumberGenerator(Enum):
    """ Random number generator types
    """
    
    MERSENNE_TWISTER = (0, "The well-known Mercenne Twister PRNG")
    
    def __init__(self, value, doc=""):
        self._value_ = value
        self.__doc__ = doc


class Condition(Enum):
    """ Comparison Operations
    """
    
    EQUAL = (0, "Compare the operands for equality")
    NOT_EQUAL = (1, "Compare the operands for inequality")
    LESS_THAN_OR_EQUAL = (2, "True if the first operand is <= the second")
    LESS_THAN = (3, "True if the first operand is <  the second")
    GREATER_THAN_OR_EQUAL = (4, "True if the first operand is >= the second")
    GREATER_THAN = (5, "True if the first operand is >  the second")
    
    def __init__(self, value, doc=""):
        self._value_ = value
        self.__doc__ = doc


class ArithmeticOperation(Enum):
    """ Arithmetic Operations
    """
    
    ADD = (0, "Perform addition")
    SUBTRACT = (1, "Perform subtraction")
    MULTIPLY = (2, "Perform multiplication")
    
    def __init__(self, value, doc=""):
        self._value_ = value
        self.__doc__ = doc
    

class LogicOperation(Enum):
    """ Logic Operations
    """
    LEFT_SHIFT = (0, "Shift left")
    RIGHT_SHIFT = (1, "Shift right")
    OR = (2, "Logical OR")
    AND = (3, "Logical AND")
    XOR = (4, "Logical XOR")
    NOT = (5, "Logical NOT")
            
    def __init__(self, value, doc=""):
        self._value_ = value
        self.__doc__ = doc


class DataSpecificationGenerator(object):
    """ Used to generate a data specification language file that can be\
        executed to produce a memory image
    """
    
    def __init__(self, spec_writer, magic=None, write_text=False):
        """
        :param spec_writer: The object to write the specification to
        :type spec_writer: Implementation of\
                :py:class:`data_specification.abstract_data_writer.AbstractDataWriter`
        :param magic: Magic number to write to the header or None to use default
        :type magic: int
        :param write_text: Determines if a text version of the specification\
                    is to be written
        :type write_text: bool
        :raise data_specification.exceptions.DataWriteException:\
                    If a write to external storage fails
        """
        pass
    
    def comment(self, comment):
        """ Write a comment to the text version of the specification.\
            Note that this is ignored by the binary file
        
        :param comment: The comment to write
        :type comment: str
        :return: Nothing is returned
        :raise data_specification.exceptions.DataWriteException:\
                    If a write to external storage fails
        """
        pass
    
    def execute_break(self):
        """ Insert command to stop execution with an exception (for debugging)
        
        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataWriteException:\
                    If a write to external storage fails
        """
        pass
        
    def execute_no_operation(self):
        """ Insert command to execute nothing
        
        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataWriteException:\
                    If a write to external storage fails
        """
        pass
    
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
        :raise data_specification.exceptions.DataWriteException:\
                    If a write to external storage fails
        :raise data_specification.exceptions.DataSpecificationRegionInUseException:\
                    If the region was already reserved
        :raise data_specification.exceptions.DataSpecificationParameterOutOfBoundsException:\
                    If the region requested was out of the allowed range, or
                    that the size was too big to fit in SDRAM
        """
        pass
    
    def free_memory_region(self, region):
        """ Insert command to free a previously reserved memory region
        
        :param region: The number of the region to free, from 0 to 15
        :type region: int
        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataWriteException:\
                    If a write to external storage fails
        :raise data_specification.exceptions.DataSpecificationNotAllocatedException:\
                    If the region was not reserved
        :raise data_specification.exceptions.DataSpecificationParameterOutOfBoundsException:\
                    If the region requested was out of the allowed range
        """
        pass
    
    def declare_random_number_generator(self, rng_type, seed):
        """ Insert command to declare a random number generator
        
        :param rng_type: The type of the random number generator 
        :type rng_type: :py:class:`RandomNumberGenerator`
        :param seed: The seed of the random number generator >= 0
        :type seed: int
        :return: The id of the created random number generator, between 0 and 15
        :rtype: int
        :raise data_specification.exceptions.DataWriteException:\
                    If a write to external storage fails
        :raise data_specification.exceptions.DataSpecificationNoMoreException:\
                    If there is no more space for a new generator
        :raise data_specification.exceptions.DataSpecificationUnknownTypeException:\
                    If the rng_type is not one of the allowed values
        :raise data_specification.exceptions.DataSpecificationParameterOutOfBoundsException:\
                    If the seed is too big or too small
        """
        pass
    
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
        :raise data_specification.exceptions.DataWriteException:\
                    If a write to external storage fails
        :raise data_specification.exceptions.DataSpecificationNoMoreException:\
                    If there is no more space for a new random distribution
        :raise data_specification.exceptions.DataSpecificationNotAllocatedException:\
                    If the requested rng_id has not been allocated
        :raise data_specification.exceptions.DataSpecificationParameterOutOfBoundsException:\
                    If rng_id, min_value or max_value is out of range
        """
        pass
    
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
        :raise data_specification.exceptions.DataWriteException:\
                    If a write to external storage fails
        :raise data_specification.exceptions.DataSpecificationNotAllocatedException:\
                    If the random distribution id was not previously declared
        :raise data_specification.exceptions.DataSpecificationParameterOutOfBoundsException:\
                    If the distribution_id or register_id specified was out of\
                    range
        """
        pass
    
    def define_struture(self, parameters):
        """ Insert commands to define a data structure
        
        :param parameters: A list of between 1 and 255 tuples of\
                    (label, data_type, value) where:
                    * label is the label of the element (for debugging)
                    * data_type is the data type of the element
                    * value is the value of the element,\
                      or None if no value is to be assigned
        :type parameters: list of (str, :py:class:`DataType`, float)
        :return: The id of the new structure, between 0 and 15
        :rtype: int
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
        pass
    
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
                    structure, between 0 and the number of parameters declared\
                    in the structure
        :type parameter_index: int
        :param value: 
                    * If value_is_register is False, the value to assign at the\
                      selected position as a float
                    * If value_is_register is True, the id of the register\
                      containing the value to assign to the position, between\
                      0 and 15
        :type value: float
        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataWriteException:\
                    If a write to external storage fails
        :raise data_specification.exceptions.DataSpecificationParameterOutOfBoundsException:\
                    * If structure_id is not in the allowed range
                    * If parameter_index is larger than the number of\
                      parameters declared in the original structure
                    * If value_is_register is False, and the data type of\
                      the structure value is an integer, and the value has a\
                      fractional part
                    * If value_is_register is False, and value would overflow\
                      the position in the structure
                    * If value_is_register is True, and value is not a valid\
                      register id
        :raise data_specification.exceptions.DataSpecificationNotAllocatedException:\
                    If the structure requested has not been declared
        """
        pass
    
    def write_structure(
            self, structure_id, repeats=1, repeats_is_register=False):
        """ Insert command to write a structure to the current write pointer,
            causing the current write pointer to move on by the number of
            bytes needed to represent the structure
        
        :param structure_id: 
                    * If called within a function, the id of the structure to\
                      write, between 0 and 15 
                    * If called outside of a function, the id of the structure\
                      argument, between 0 and 5 
        :type structure_id: int
        :param repeats:
                    * If repeats_is_register is True, the id of the register
                      containing the number of repeats, between 0 and 15
                    * If repeats_is_register is False, the number of repeats to\
                      write, between 0 and 255
        :type repeats: int
        :param repeats_is_register: Identifies if repeats identifies a\
                     register
        :type repeats_is_register: bool
        :return: The position of the write pointer within the current region,\
                    in bytes from the start of the region
        :rtype: int
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
        pass
    
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
        :raise data_specification.exceptions.DataWriteException:\
                    If a write to external storage fails
        :raise data_specification.exceptions.DataSpecificationNoMoreException:\
                    If there are no more spaces for new functions
        :raise data_specification.exceptions.DataSpecificationParameterOutOfBoundsException:\
                    If there are too many items in the list of arguments
        :raise data_specification.exceptions.DataSpecificationInvalidCommandException:\
                    If there is already a function being defined at this point
        """
        pass
    
    def end_function(self):
        """ Insert command to mark the end of a function definition
        
        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataWriteException:\
                    If a write to external storage fails
        :raise data_specification.exceptions.DataSpecificationInvalidCommandException:\
                    If there is no function being defined at this point
        """
        pass
    
    def call_function(self, function_id, structure_ids):
        """ Insert command to call a function
        
        :param function_id: The id of a previously defined function, between 0
                    and 31
        :type function_id: int
        :param structure_ids: A list of structure_ids that will be passed into\
                    the function, each between 0 and 15
        :type structure_ids: list of int
        :return: Nothing is returned
        :rtype: None
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
        pass
    
    def write_value(self, data, data_is_register=False, repeats=1, 
            repeats_is_register=False, data_type=DataType.UINT32):
        """ Insert command to write a value one or more times to the current
            write pointer, causing the write pointer to move on by the number
            of bytes required to represent the data type
        
        :param data:
                    * If data_is_register is True, the id of the register
                      containing the data, between 0 and 15
                    * If data_is_register is False, the data to write as a float
        :type data: float
        :param data_is_register: Identifies if data is a register id
        :type data_is_register: bool
        :param repeats:
                    * If repeats_is_register is True, the id of the register
                      containing the number of times to repeat the data,
                      between 0 and 15
                    * If repeats_is_register is False, the number of times to\
                      repeat the data, between 1 and 255
        :type repeats: int
        :param repeats_is_register: Identifies if repeats is a register id
        :type repeats_is_register: bool
        :param data_type:
                    * If data_is_register is True, the type of the data held
                      in the register
                    * If data_is_register is False, the type to convert data to
        :type data_type: :py:class:`DataType`
        :return: The position of the write pointer within the current region,
                    in bytes from the start of the region
        :rtype: int
        :raise data_specification.exceptions.DataWriteException:\
                    If a write to external storage fails
        :raise data_specification.exceptions.DataSpecificationParameterOutOfBoundsException:\
                    * If repeats_is_register is False, and repeats is out\
                      of range
                      If repeats_is_register is True, and repeats is not a\
                      valid register id
                    * If data_is_register is False, and data_type is an integer\
                      type, and data has a fractional part
                    * If data_is_register is False and data would overflow the\
                      data type
                    * If data_is_register is True and data is not a valid\
                      register id
        :raise data_specification.exceptions.DataSpecificationUnknownTypeException:\
                    If the data type is not known
        :raise data_specification.exceptions.DataSpecificationNoRegionSelectedException:\
                    If no region has been selected to write to
        :raise data_specification.exceptions.DataSpecificationRegionExhaustedException:\
                    If the selected region has no more space
        """
        pass
    
    def write_array(self, array):
        """ Insert command to write an array of words, causing the write pointer
            to move on by (4 * the array size), in bytes
        
        :param array: An array of words to be written
        :type array: array
        :return: The position of the write pointer within the current region,\
                    in bytes from the start of the region
        :rtype: int
        :raise data_specification.exceptions.DataWriteException:\
                    If a write to external storage fails
        :raise data_specification.exceptions.DataSpecificationNoRegionSelectedException:\
                    If no region has been selected to write to
        :raise data_specification.exceptions.DataSpecificationRegionExhaustedException:\
                    If the selected region has no more space
        """
        pass
    
    def switch_write_focus(self, region):
        """ Insert command to switch the region being written to
        
        :param region: The id of the region to switch to, between 0 and 15
        :type region: int
        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataWriteException:\
                    If a write to external storage fails
        :raise data_specification.exceptions.DataSpecificationParameterOutOfBoundsException:\
                    If the region identifier is not valid
        :raise data_specification.exceptions.DataSpecificationNotAllocatedException:\
                    If the region has not been allocated
        :raise data_specification.exceptions.DataSpecificationRegionUnfilledException:\
                    If the selected region should not be filled
        """
        pass
    
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
        pass
    
    def break_loop(self):
        """ Insert command to break out of a loop before it has completed
        
        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataWriteException:\
                    If a write to external storage fails
        :raise data_specification.exceptions.DataSpecificationInvalidCommandException:\
                    If there is no loop in operation at this point
        """
        pass
    
    def end_loop(self):
        """ Insert command to indicate that this is the end of the loop.\
            Commands between the start of the loop and this command will be\ 
            repeated.
        
        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataWriteException:\
                    If a write to external storage fails
        :raise data_specification.exceptions.DataSpecificationInvalidCommandException:\
                    If there is no loop in operation at this point
        """
        pass
    
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
        :raise data_specification.exceptions.DataWriteException:\
                    If a write to external storage fails
        :raise data_specification.exceptions.DataSpecificationParameterOutOfBoundsException:\
                    * If the register_id is not a valid register id
                    * if value_is_register is True and value is not a valid\
                      register id
        :raise data_specification.exceptions.DataSpecificationUnknownTypeException:\
                    If the condition is not a valid condition
        """
        pass
    
    def else_conditional(self):
        """ Insert command for the else of an if...then...else construct.\
            If the condition of the conditional evaluates to false, the\
            statements up between the conditional and the insertion of this\
            "else" are skipped, and the statements from this point until the\
            end of the conditional are executed.
        
        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataWriteException:\
                    If a write to external storage fails
        :raise data_specification.exceptions.DataSpecificationInvalidCommandException:\
                    If there is no conditional in operation at this point
        """
        pass
    
    def end_conditional(self):
        """ Insert command to mark the end of an if...then...else construct
        
        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataWriteException:\
                    If a write to external storage fails
        :raise data_specification.exceptions.DataSpecificationInvalidCommandException:\
                    If there is no conditional in operation at this point
        """
        pass
    
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
        pass
    
    def save_write_pointer(self, register_id):
        """ Insert command to save the write pointer to a register
        
        :param register_id: The id of the register to assign, between 0 and 15
        :type register_id: int
        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataWriteException:\
                    If a write to external storage fails
        :raise data_specification.exceptions.DataSpecificationParameterOutOfBoundsException:\
                    If the register_id is not a valid register id
        :raise data_specification.exceptions.DataSpecificationNoRegionSelectedException:\
                    If no region has been selected
        """
        pass
    
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
        :raise data_specification.exceptions.DataWriteException:\
                    If a write to external storage fails
        :raise data_specification.exceptions.DataSpecificationParameterOutOfBoundsException:\
                    If the address_is_register is True and address is not\
                    a valid register id
        :raise data_specification.exceptions.DataSpecificationRegionOutOfBoundsException:\
                    If the move of the pointer would put it outside of the\
                    current region
        :raise data_specification.exceptions.DataSpecificationNoRegionSelectedException:\
                    If no region has been selected
        """
        
    def align_write_pointer(self, log_block_size, 
            log_block_size_is_register=False, return_register_id=None):
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
        pass
    
    def call_arithmetic_operation(self, register_id, operand_1, operation, 
            operand_2, signed, operand_1_is_register=False, 
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
        pass
    
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
        pass
    
    def copy_structure(self, source_structure_id, destination_structure_id=None,
            source_id_is_register=False, destination_id_is_register=False):
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
        :raise data_specification.exceptions.DataWriteException:\
                    If a write to external storage fails
        :raise data_specification.exceptions.DataSpecificationParameterOutOfBoundsException:\
                    * If source_id_is_register is True and source_structure_id\
                      is not a valid register id
                    * If destination_id_is_register is True and\
                      destination_structure_id is not a valid register id
                    * If source_id_is_register is False and source_struture_id\
                      is not a valid struture id
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
        pass
    
    def copy_structure_parameter(self, source_structure_id, 
            source_parameter_index, destination_structure_id, 
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
        :raise data_specification.exceptions.DataWriteException:\
                    If a write to external storage fails
        :raise data_specification.exceptions.DataSpecificationParameterOutOfBoundsException:\
                    * If source_struture_id is not a valid struture id
                    * If ddestination_structure_id is not a valid structure id
                    * If source_parameter_index is not a valid parameter index\
                      in the source structure
                    * If destination_parameter_index is not a valid parmater\
                      index in the destination structure
        :raise data_specification.exceptions.DataSpecificationInvalidTypeException:\
                    If the source and destination data types do not match
        :raise data_specification.exceptions.DataSpecificationNotAllocatedException:\
                    * If no structure with id destination_structure_id has been\
                      allocated
                    * If no structure with id source_structure_id has been
                      allocated  
        """
        pass
    
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
        pass
    
    def print_text(self, text):
        """ Insert command to print some text (for debugging)
        
        :param text: The text to write
        :type text: str
        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataWriteException:\
                    If a write to external storage fails
        """
        pass
    
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
        pass
    
    def end_specification(self, close_writer=True):
        """ Insert a command to indicate that the specification has finished\
            and finish writing
        
        :param close_writer: Indicates whether to close the underlying writer
        :type close_writer: bool
        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataWriteException:\
                    If a write to external storage fails
        """
        pass
