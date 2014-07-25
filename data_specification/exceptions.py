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
        print "Region {%d} was already allocated".format(region)


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
        print "Region {%d} was requested unfilled, but command {} requests its use".format(
            region, command)


class DataSpecificationNoRegionSelectedException(DataSpecificationException):
    """ An exception that indicates that a memory region has not been selected
    """

    def __init__(self, command):
        """
        :param command: The command being executed
        :type command: str
        """
        print "Command {} tries to operate on an unspecified memory region".format(
            command)


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
        print "Region {%d} with size {%d} ran out of allocated memory (space already occupied {%d}) during command {}".format(
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
        print "Requesting offset {%d} into region {%d} with size {%d} during command {}".format(
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
        print "Requesting value {%d} for parameter {} whose allowed range is from {%d} to {%d} during command {%s}".format(
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
        print "Using unallocated item with type {} and id {%d} during command {%s}".format(
            item_type, item_id, command)


class DataSpecificationNoMoreException(DataSpecificationException):
    """ An exception that indicates that there is no more space for the\
        requested item
    """

    def __init__(self, item_type, items_allocated):
        """
        :param item_type: The type of item being requested
        :type item_type: str
        :param items_allocated: The number of items that have been allocated
        :type item_type: int
        """
        print "Unavailable space for requested item type {%s}. Items already allocated: {%d}".format(
            item_type, items_allocated)


class DataSpecificationUnknownTypeException(DataSpecificationException):
    """ An exception that indicates that the value of the requested type\
        is unknown
    """

    def __init__(self, type_name, requested_value, command):
        """
        :param type_name: The name of the requested type
        :type type_name: str
        :param requested_value: The requested value
        :type requested_value: int
        :param command: The command being executed
        :type command: str
        """
        print "Unknown value {%d} of the requested type {%s} during command {%s}".format(
            type_name, requested_value, command)


class DataSpecificationInvalidCommandException(DataSpecificationException):
    """ An exception that indicates that the command being requested cannot be
        executed at this point in the specification
    """

    def __init__(self, command):
        """
        :param command: The command being executed
        :type command: str
        """
        print "The requested command {%s} cannot be executed at this point in the specification".format(
            command)


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
        print "The value assigned {%d} does not match the value expected {%d} for type {%s} during command {%s}".format(
            requested_value, expected_value, type_name, command)
