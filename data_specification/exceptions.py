class DataWriteException(Exception):
    """ An exception that indicates that there was an error writing\
        to the underlying medium
    """

    def __init__(self, message):
        """
        :param message: A message to indicate what when wrong
        :type message: str
        """
        print message


class DataUndefinedWriterException(Exception):
    """an exception that indicates that the file data writer has not been\
       initialised
    """

    def __init__(self, message):
        """
        :param message: A message to indicate what when wrong
        :type message: str
        """
        print message


class DataReadException(Exception):
    """ An exception that indicates that there was an error reading\
        from the underlying medium
    """

    def __init__(self, message):
        """
        :param message: A message to indicate what when wrong
        :type message: str
        """
        print message


class DataSpecificationException(Exception):
    """ A general purpose exception indicating that something went\
        wrong when interacting with a Data Specification
    """

    def __init__(self, message):
        print message


class DataSpecificationRegionInUseException(DataSpecificationException):
    """ An exception that indicates that a region has already been\
        allocated
    """

    def __init__(self, region):
        """
        :param region: The region that was already allocated
        :type message: int
        """
        print "Region {0:d} was already allocated".format(region)


class DataSpecificationRegionUnfilledException(DataSpecificationException):
    """ An exception that indicates that a memory region is being used\
        that was originally requested to be unfilled
    """

    def __init__(self, region, command):
        """
        :param region: The region that was requested as unfilled
        :type region: int
        :param command: The command being executed
        :type command: str
        """
        print "Region {0:d} was requested unfilled, but command {1:s} " \
              "requests its use".format(region, command)


class DataSpecificationNoRegionSelectedException(DataSpecificationException):
    """ An exception that indicates that a memory region has not been selected
    """

    def __init__(self, command):
        """
        :param command: The command being executed
        :type command: str
        """
        print "Command {0:s} tries to operate on an unspecified memory " \
              "region".format(command)


class DataSpecificationRegionExhaustedException(DataSpecificationException):
    """ An exception that indicates that a region has run out of memory\
        whilst some data is being written
    """

    def __init__(self, region, region_size, allocated_size, command):
        """
        :param region: The region that was being written to
        :type region: int
        :param region_size: The originally requested size of the region that\
                    has run out of space, in bytes
        :type region_size: int
        :param allocated_size: The amount of the originally requested space\
                    that has already been allocated, in bytes
        :type allocated_size: int
        :param command: The command being executed
        :type command: str
        """
        print "Region {0:d} with size {1:d} ran out of allocated memory " \
              "(space already occupied {2:d}) during command {3:s}".format(
                  region, region_size, allocated_size, command)


class DataSpecificationRegionOutOfBoundsException(DataSpecificationException):
    """ An exception that indicates that an offset into a region is out\
        of bounds for that region
    """

    def __init__(self, region, region_size, requested_offset, command):
        """
        :param region: The region that was being offset into 
        :type region: int
        :param region_size: The originally requested size of the region in\
                    question, in bytes 
        :type region_size: int
        :param requested_offset: The offset being requested, in bytes
        :type requested_offset: int
        :param command: The command being executed
        :type command: str
        """
        print "Requesting offset {0:d} into region {1:d} with size {2:d} " \
              "during command {3:s}".format(
                  requested_offset, region, region_size, command)


class DataSpecificationParameterOutOfBoundsException(
    DataSpecificationException):
    """ An exception that indicates that a parameter value was outside of the\
        allowed bounds
    """

    def __init__(self, parameter, value, range_min, range_max, command):
        """
        :param paramter: The parameter that is out of bounds
        :type parameter: str
        :param value: The value specified
        :type type: float
        :param range_min: The minimum allowed value
        :type range_min: float
        :param range_max: The maximum allowed value
        :type range_max: float
        :param command: The command being executed
        :type command: str
        """
        print "Requesting value {0:d} for parameter {1:s} whose allowed range " \
              "is from {2:d} to {3:d} during command {4:s}".format(
                  value, parameter, range_min, range_max, command)


class DataSpecificationNotAllocatedException(DataSpecificationException):
    """ An exception that indicates that an item is being used\
        that has not been allocated
    """

    def __init__(self, item_type, item_id, command):
        """
        :param item_type: The type of the item being used
        :type item_type: str
        :param item_id: The id of the item being used
        :type item_id: int
        :param command: The command being executed
        :type command: str
        """
        print "Using unallocated item with type {0:s} and id {1:d} during " \
              "command {2:s}".format(item_type, item_id, command)


class DataSpecificationNoMoreException(DataSpecificationException):
    """ An exception that indicates that there is no more space for the\
        requested item
    """

    def __init__(self, space_available, space_required):
        """
        :param space_available: The space available in the region
        :type space_available: int
        :param space_required: The space requested by the write command
        :type space_required: int
        """
        print "Space unavailable to write all the elements requested by the " \
              "write operation. Space available: {0:d}; space requested: " \
              "{1:d}".format(space_available, space_required)


class DataSpecificationUnknownTypeException(DataSpecificationException):
    """ An exception that indicates that the value of the requested type\
        is unknown
    """

    def __init__(self, type_name, requested_value, command):
        """
        :param type_name: The name of the requested type
        :type type_name: str
        :param requested_value: The requested value
        :type requested_value: float
        :param command: The command being executed
        :type command: str
        """
        print "Unknown value {0:f} of the requested type {1:s} during " \
              "command {2:s}".format(type_name, requested_value, command)


class DataSpecificationInvalidSizeException(DataSpecificationException):
    """ An exception that indicates that the size of the requested type is\
        invalid
    """

    def __init__(self, type_name, type_size, command):
        """
        :param type_name: The name of the requested type
        :type type_name: str
        :param type_size: The size of the requested variable
        :type type_size: int
        :param command: The command being executed
        :type command: str
        """
        print "Invalid size {0:d} of the requested type {1:s} during " \
              "command {%s}".format(type_size, type_name, command)

class DataSpecificationInvalidCommandException(DataSpecificationException):
    """ An exception that indicates that the command being requested cannot be
        executed at this point in the specification
    """

    def __init__(self, command):
        """
        :param command: The command being executed
        :type command: str
        """
        print "The requested command {0:s} cannot be executed at this point " \
              "in the specification".format(command)


class DataSpecificationInvalidTypeException(DataSpecificationException):
    """ An exception that indicates that the value of the type given does not\
        match that expected
    """

    def __init__(self, type_name, requested_value, expected_value, command):
        """
        :param type_name: The name of the requested type
        :type type_name: str
        :param requested_value: The requested value
        :type requested_value: int
        :param expected_value: The expected value
        :type expected_value: int
        :param command: The command being executed
        :type command: str
        """
        print "The value assigned {0:d} does not match the value expected " \
              "{1:d} for type {2:s} during command {3:s}".format(
                  requested_value, expected_value, type_name, command)


class ExecuteBreakInstruction(DataSpecificationException):
    """ An exception which occurs when a BREAK instruction is found in the data\
    specification
    """

    def __init__(self, address, filename):
        print "Executing BREAK instruction at address {0:d} of file " \
              "{1:s}".format(address, filename)


class DataSpecificationSyntaxError(DataSpecificationException):
    """ An exception which occurs when a command read from the data\
    specification file shows an inconsistency in the binary content
    """

    def __init__(self, message):
        print message


class DataSpecificationTablePointerOutOfMemory(DataSpecificationException):
    """ An exception which occurs when building the table pointer as header of\
    the data generated by the spec executor. This message is printed in case\
    the memory available is not enough to contain the pointer table for each of\
    the allocated regions
    """

    def __init__(self, memory_available, memory_required):
        print "The memory available {0:d} is not sufficient for the allocated" \
              " regions plus the header table pointer {1:d}".format(
            memory_available, memory_required)


class DataSpecificationRegionNotAllocated(DataSpecificationException):
    """ An exception which occurs when trying to write to an unallocated region\
    of memory
    """

    def __init__(self, region, command):
        print "Region {0:d} has not been allocated during execution of " \
              "command {1:s}".format(region, command)
