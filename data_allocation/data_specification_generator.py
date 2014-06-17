def _enum(*sequential, **named):
    enums = dict(filter(lambda x: x[0] is not None, 
            zip(sequential, range(len(sequential)))), **named)
    return type('Enum', (), enums)


class DataSpecificationGenerator(object):
    """ Used to generate a data specification language file that can be\
        executed to produce a memory image
    """
    
    DATA_TYPE = _enum("uint8", "uint16", "uint32", "uint64", 
                       "int8", "int16", "int32", "int64", 
                       "u88", "u1616", "u3232", 
                       "s87", "s1615", "s3231", 
                       "struct", "random", 
                       "u08", "u016", "u032", "u064", 
                       "s07", "s015", "s031", "s063")
    """  Enumeration of possible data types:
        
            ====== ===============================================
            Type   Description
            ====== ===============================================
            uint8  8-bit unsigned integer
            uint16 16-bit unsigned integer
            uint32 32-bit unsigned integer
            unit64 64-bit unsigned integer
            int8   8-bit signed integer
            int16  16-bit signed integer
            int32  32-bit signed integer
            int64  64-bit signed integer
            u88    8.8 unsigned fixed point number
            u1616  16.16 unsigned fixed point number
            u3232  32.32 unsigned fixed point number
            s87    8.7 signed fixed point number
            s1615  16.15 signed fixed point number
            s3231  32.31 signed fixed point number
            struct Reference to a pre-defined structure
            random Reference to a pre-defined random distribution
            u08    0.8 unsigned fixed point number
            u016   0.16 unsigned fixed point number
            u032   0.32 unsigned fixed point number
            u064   0.64 unsigned fixed point number
            s07    0.7 signed fixed point number
            s015   0.15 signed fixed point number
            s031   0.31 signed fixed point number
            s063   0.63 signed fixed point number
            ====== ===============================================
    """
    
    
    RANDOM_NUMBER_GENERATOR_TYPE = _enum("MERSENNE_TWISTER")
    """ Enumeration of possible random number generator types:
            
            ================ ===============================================
            Type             Description
            ================ ===============================================
            MERSENNE_TWISTER The well-known Mercenne Twister PRNG
            ================ ===============================================
    """
    
    
    CONDITION = _enum("EQUAL", "NOT_EQUAL", "LESS_THAN_OR_EQUAL", "LESS_THAN",
            "GREATER_THAN_OR_EQUAL", "GREATER_THAN")
    """ Enumeration of possible random conditionals:
            
            ===================== ==============================================
            Type                  Description
            ===================== ==============================================
            EQUAL                 Compares the operands for equality
            NOT_EQUAL             Compares the operands for inequality
            LESS_THAN_OR_EQUAL    True if the first operand is <= the second
            LESS_THAN             True if the first operand is <  the second
            GREATER_THAN_OR_EQUAL True if the first operand is >= the second
            GREATER_THAN          True if the first operand is >  the second
            ===================== ==============================================
    """
    
    
    def __init__(self, spec_writer, app_id, magic=None, write_text=False):
        """
        :param spec_writer: The object to write the specification to
        :type spec_writer: data_allocation.abstract_data_specification_writer
                                          .AbstractDataSpecificationWriter
        :param app_id: The id of the application
        :type app_id: int
        :param magic: Magic number to write to the header,
                      or None to use default
        :type magic: int
        :param write_text: Determines if a text version of the specification
                           is to be written
        :type write_text: bool
        :raise None: No exceptions are raised
        """
        pass
    
    
    def comment(self, comment):
        """ Write a comment to the text version of the specification.\
            Note that this is ignored by the binary file
        
        :param comment: The comment to write
        :type comment: str
        :return: Nothing is returned
        :raise data_allocation.exceptions.DataSpecificationWriteException:\
                    If a write to external storage fails
        """
        pass
    
    
    def execute_break(self):
        """ Insert command to stop execution with an exception (for debugging)
        
        :return: Nothing is returned
        :rtype: None
        :raise data_allocation.exceptions.DataSpecificationWriteException:\
                    If a write to external storage fails
        """
        pass
        
    
    def execute_no_operation(self):
        """ Insert command to execute nothing
        
        :return: Nothing is returned
        :rtype: None
        :raise data_allocation.exceptions.DataSpecificationWriteException:\
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
        :raise data_allocation.exceptions.DataSpecificationWriteException:\
                    If a write to external storage fails
        :raise data_allocation.exceptions.DataSpecificationRegionInUseException:\
                    If the region was already reserved
        :raise data_allocation.exceptions.DataSpecificationParameterOutOfBoundsException:\
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
        :raise data_allocation.exceptions.DataSpecificationWriteException:\
                    If a write to external storage fails
        :raise data_allocation.exceptions.DataSpecificationNotAllocatedException:\
                    If the region was not reserved
        :raise data_allocation.exceptions.DataSpecificationParameterOutOfBoundsException:\
                    If the region requested was out of the allowed range
        """
        pass
    
    
    def declare_random_number_generator(self, rng_type, seed):
        """ Insert command to declare a random number generator
        
        :param rng_type: The type of the random number generator 
        :type rng_type: RANDOM_NUMBER_GENERATOR_TYPE
        :param seed: The seed of the random number generator >= 0
        :type seed: int
        :return: The id of the created random number generator, between 0 and 15
        :rtype: int
        :raise data_allocation.exceptions.DataSpecificationWriteException:\
                    If a write to external storage fails
        :raise data_allocation.exceptions.DataSpecificationNoMoreException:\
                    If there is no more space for a new generator
        :raise data_allocation.exceptions.DataSpecificationUnknownTypeException:\
                    If the rng_type is not one of the allowed values
        :raise data_allocation.exceptions.DataSpecificationParameterOutOfBoundsException:\
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
        :raise data_allocation.exceptions.DataSpecificationWriteException:\
                    If a write to external storage fails
        :raise data_allocation.exceptions.DataSpecificationNoMoreException:\
                    If there is no more space for a new random distribution
        :raise data_allocation.exceptions.DataSpecificationNotAllocatedException:\
                    If the requested rng_id has not been allocated
        :raise data_allocation.exceptions.DataSpecificationParameterOutOfBoundsException:\
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
        :raise data_allocation.exceptions.DataSpecificationWriteException:\
                    If a write to external storage fails
        :raise data_allocation.exceptions.DataSpecificationNotAllocatedException:\
                    If the random distribution id was not previously declared
        :raise data_allocation.exceptions.DataSpecificationParameterOutOfBoundsException:\
                    If the distribution_id or register_id specified was out of\
                    range
        """
        pass
    
    
    def define_struture(self, elements):
        """ Insert commands to define a data structure
        
        :param elements: A list of tuples of (label, data_type, value) where:
        
                    * label is the label of the element (for debugging)
                    * data_type is the data type of the element
                    * value is the value of the element,\
                      or None if no value is to be assigned
        :type elements: list of (str, DATA_TYPE, int)
        :return: The id of the new structure, between 0 and 15
        :rtype: int
        :raise data_allocation.exceptions.DataSpecificationWriteException:\
                    If a write to external storage fails
        :raise data_allocation.exceptions.DataSpecificationNoMoreException:\
                    If there are no more spaces for new structures
        :raise data_allocation.exceptions.DataSpecificationParameterOutOfBoundsException:\
                    If there are too many items in the list of elements, or\
                    the size of one of the tuples is incorrect
        :raise data_allocation.exceptions.DataSpecificationUnknownTypeException:\
                    If one of the data types in the structure is unknown
        """
        pass
    
    
    def set_structure_value(self, structure_id, value_index, value):
        """ Insert command to set a value in a structure
        
        :param structure_id: The id of the structure between 0 and 15
        :type structure_id: int
        :param value_index: The index of the value to assign in the structure
        :type value_index: int
        :param value: The value to assign at the selected position as a float
        :type value: float
        :return: Nothing is returned
        :rtype: None
        :raise data_allocation.exceptions.DataSpecificationWriteException:\
                    If a write to external storage fails
        :raise data_allocation.exceptions.DataSpecificationParameterOutOfBoundsException:\
                    * If the structure_id is not in the allowed range
                    * If the value_index is larger than that declared in the\
                      original structure
                    * If the value has a fractional part and the data type of\
                      the structure value is int
                    * If the value would overflow the position in the structure
        :raise data_allocation.exceptions.DataSpecificationNotAllocatedException:\
                    If the structure requested has not been declared
        """
        pass
    
    
    def write_value(self, data, repeats=1, data_type=DATA_TYPE.uint32):
        """ Insert commands to write a value one or more times.
        
        :param data: The data to write as a float, or if data_type is struct or
                     random, the id of the structure or random number generator
                     respectively
        :type data: float
        :param repeats: The number of times to repeat the data between 1 and 255
        :type repeats: int
        :param data_type: The type of the data to be written
        :type data_type: DATA_TYPE
        :return: Nothing is returned
        :rtype: None
        :raise data_allocation.exceptions.DataSpecificationWriteException:\
                    If a write to external storage fails
        :raise data_allocation.exceptions.DataSpecificationParameterOutOfBoundsException:\
                    * If the number of repeats is less than 1 or more than 255
                    * If the value has a fractional part and the data type of\
                      the structure value is int, struct or random
                    * If the data_type is struct or random and the value is\
                      not a valid identifier for a struct or a random
                    * If the value would overflow the data type
        :raise data_allocation.exceptions.DataSpecificationUnknownTypeException:\
                    If the data type is not known
        :raise data_allocation.exceptions.DataSpecificationNotAllocatedException:\
                    If data_type is struct or random, and the specified id was\
                    not allocated
        :raise data_allocation.exceptions.DataSpecificationNoRegionSelectedException:\
                    If no region has been selected to write to
        :raise data_allocation.exceptions.DataSpecificationRegionExhaustedException:\
                    If the selected region has no more space
        """
        pass
    
    
    def write_reg_value(self, register_id, repeats=1, 
            data_type=DATA_TYPE.uint32):
        """ Insert command to write a value from a register one or more times
        
        :param register_id: The id of the register from which the value will/
                    be written, between 0 and 15
        :type register_id: int
        :param repeats: The number of times to repeat the data between 1 and 255
        :type repeats: int
        :param data_type: The type of the data to be written
        :type data_type: DATA_TYPE
        :return: Nothing is returned
        :rtype: None
        :raise data_allocation.exceptions.DataSpecificationWriteException:\
                    If a write to external storage fails
        :raise data_allocation.exceptions.DataSpecificationParameterOutOfBoundsException:\
                    * If the number of repeats is less than 1 or more than 255
                    * If the data_type is struct or random and the value in the\
                      register is not a valid identifier for a struct or a \
                      random
                    * If the value in the register would overflow the data type
        :raise data_allocation.exceptions.DataSpecificationUnknownTypeException:\
                    If the data type is not known
        :raise data_allocation.exceptions.DataSpecificationNotAllocatedException:\
                    If data_type is struct or random, and the value in the\
                    register was not allocated
        :raise data_allocation.exceptions.DataSpecificationNoRegionSelectedException:\
                    If no region has been selected to write to
        :raise data_allocation.exceptions.DataSpecificationRegionExhaustedException:\
                    If the selected region has no more space
        """
        pass
    
    
    def write_array(self, array, repeats=1, data_type=DATA_TYPE.uint32):
        """ Insert command to write an array of homogeneous data
        
        :param array: An iterable of values to write
        :type array: iterable
        :param repeats: The number of times to repeat the array between\
                    1 and 255
        :type repeats: int
        :param data_type: The type of each element of the array to be written
        :type data_type: DATA_TYPE
        :return: Nothing is returned
        :rtype: None
        :raise data_allocation.exceptions.DataSpecificationWriteException:\
                    If a write to external storage fails
        :raise data_allocation.exceptions.DataSpecificationParameterOutOfBoundsException:\
                    * If the number of repeats is less than 1 or more than 255
                    * If the data_type is struct or random and the value in the\
                      array is not a valid identifier for a struct or a \
                      random
                    * If the value in the array would overflow the data type
        :raise data_allocation.exceptions.DataSpecificationUnknownTypeException:\
                    If the data type is not known
        :raise data_allocation.exceptions.DataSpecificationNotAllocatedException:\
                    If data_type is struct or random, and the value in the\
                    array was not allocated
        :raise data_allocation.exceptions.DataSpecificationNoRegionSelectedException:\
                    If no region has been selected to write to
        :raise data_allocation.exceptions.DataSpecificationRegionExhaustedException:\
                    If the selected region has no more space
        """
        pass
    
    
    def switch_write_focus(self, region):
        """ Insert command to switch the region being written to
        
        :param region: The id of the region to switch to, between 0 and 15
        :type region: int
        :return: Nothing is returned
        :rtype: None
        :raise data_allocation.exceptions.DataSpecificationWriteException:\
                    If a write to external storage fails
        :raise data_allocation.exceptions.DataSpecificationParameterOutOfBoundsException:\
                    If the region identifier is not valid
        :raise data_allocation.exceptions.DataSpecificationNotAllocatedException:\
                    If the region has not been allocated
        :raise data_allocation.exceptions.DataSpecificationRegionUnfilledException:\
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
        :param start: The number at which to start the loop counter between 
        :type start: int
        :param end: The number which the loop counter reaches which stops the\
                    loop i.e. the loop will run while the counter_register < end
        :type end: int
        :param increment: The amount by which to increment the loop counter
                    on each run of the loop
        :type increment: int
        :param start_is_register: Indicates if start is a register id
        :type start_is_register: bool
        :param end_is_register: Indicates if end is a register id
        :type end_is_register: bool
        :param increment_is_register: Indicates if increment is a register id
        :type increment_is_register: bool
        :return: Nothing is returned
        :rtype: None
        :raise data_allocation.exceptions.DataSpecificationWriteException:\
                    If a write to external storage fails
        :raise data_allocation.exceptions.DataSpecificationParameterOutOfBoundsException:\
                    * If the register id is not in the allowed range
                    * If start, end or increment are not in the allowed range
                    * If start, end or increment are register ids and are not\
                      valid register ids
        """
        pass
    
    
    def break_loop(self):
        """ Insert command to break out of a loop before it has completed
        
        :return: Nothing is returned
        :rtype: None
        :raise data_allocation.exceptions.DataSpecificationWriteException:\
                    If a write to external storage fails
        :raise data_allocation.exceptions.DataSpecificationInvalidCommandException:\
                    If there is no loop in operation at this point
        """
        pass
    
    
    def end_loop(self):
        """ Insert command to indicate that this is the end of the loop.\
            Commands between the start of the loop and this command will be\ 
            repeated.
        
        :return: Nothing is returned
        :rtype: None
        :raise data_allocation.exceptions.DataSpecificationWriteException:\
                    If a write to external storage fails
        :raise data_allocation.exceptions.DataSpecificationInvalidCommandException:\
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
        :type condition: CONDITION
        :param value: The value to compare the value of the register with
        :type value: int
        :param value_is_register: Indicates if the value is a register id
        :type value_is_register: bool
        
        """
        pass
    