# Copyright (c) 2017-2019 The University of Manchester
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


class DataSpecificationException(Exception):
    """ A general purpose exception indicating that something went\
        wrong when interacting with a Data Specification
    """


class DataUndefinedWriterException(Exception):
    """ An exception that indicates that the file data writer has not been\
        initialised
    """


class RegionInUseException(DataSpecificationException):
    """ An exception that indicates that a region has already been\
        allocated
    """

    def __init__(self, region, label=None):
        """
        :param int region: The region that was already allocated
        :param label: What label is known for the region
        :type label: str or None
        """
        if label is None:
            msg = "Region {0:d} was already allocated".format(region)
        else:
            msg = "Region {0:d} ({1:s}) was already allocated".format(
                region, label)
        super().__init__(msg)


class StructureInUseException(DataSpecificationException):
    """ An exception that indicates that a structure has already been\
        defined
    """

    def __init__(self, structure):
        """
        :param int structure: The structure that was already allocated
        """
        super().__init__("Structure {0} was already allocated".format(
            structure))


class RegionUnfilledException(DataSpecificationException):
    """ An exception that indicates that a memory region is being used\
        that was originally requested to be unfilled
    """

    def __init__(self, region, command):
        """
        :param int region: The region that was requested as unfilled
        :param str command: The command being executed
        """
        super().__init__(
            "Region {0} was requested unfilled, but command {1} "
            "requests its use".format(region, command))


class NoRegionSelectedException(DataSpecificationException):
    """ An exception that indicates that a memory region has not been selected
    """

    def __init__(self, command):
        """
        :param str command: The command being executed
        """
        super().__init__(
            "Command {0} tries to operate on an unspecified memory region"
            .format(command))


class RegionExhaustedException(DataSpecificationException):
    """ An exception that indicates that a region has run out of memory\
        whilst some data is being written
    """

    def __init__(self, region, region_size, allocated_size, command):
        """
        :param int region: The region that was being written to
        :param int region_size: The originally requested size of the region
            that has run out of space, in bytes
        :param int allocated_size: The amount of the originally requested
            space that has already been allocated, in bytes
        :param str command: The command being executed
        """
        super().__init__(
            "Region {0} with size {1} ran out of allocated memory "
            "(space already occupied {2}) during command {3:s}".format(
                region, region_size, allocated_size, command))


class RegionOutOfBoundsException(DataSpecificationException):
    """ An exception that indicates that an offset into a region is out\
        of bounds for that region
    """

    def __init__(self, region, region_size, requested_offset, command):
        """
        :param int region: The region that was being offset into
        :param int region_size:
            The originally requested size of the region in question, in bytes
        :param int requested_offset: The offset being requested, in bytes
        :param str command: The command being executed
        """
        super().__init__(
            "Requesting offset {0} into region {1} with size {2} "
            "during command {3}".format(
                requested_offset, region, region_size, command))


class ParameterOutOfBoundsException(DataSpecificationException):
    """ An exception that indicates that a parameter value was outside of the\
        allowed bounds
    """

    def __init__(self, parameter, value, range_min, range_max, command):
        """
        :param str parameter: The parameter that is out of bounds
        :param value: The value specified
        :type value: float or int
        :param range_min: The minimum allowed value
        :type range_min: float or int
        :param range_max: The maximum allowed value
        :type range_max: float or int
        :param str command: The command being executed
        """
        # pylint: disable=too-many-arguments
        super().__init__(
            "Requesting value {} for parameter {} whose allowed range is "
            "from {} to {} during command {}".format(
                value, parameter, range_min, range_max, command))


class NotAllocatedException(DataSpecificationException):
    """ An exception that indicates that an item is being used\
        that has not been allocated
    """

    def __init__(self, item_type, item_id, command):
        """
        :param str item_type: The type of the item being used
        :param int item_id: The ID of the item being used
        :param str command: The command being executed
        """
        super().__init__(
            "Using unallocated item with type {0} and ID {1} during "
            "command {2}".format(item_type, item_id, command))


class NoMoreException(DataSpecificationException):
    """ An exception that indicates that there is no more space for the\
        requested item
    """

    def __init__(self, space_available, space_required, region):
        """
        :param int space_available: The space available in the region
        :param int space_required: The space requested by the write command
        """
        super().__init__(
            "Space unavailable to write all the elements requested by the "
            "write operation. Space available: {0}; space requested: "
            "{1} for region {2}.".format(
                space_available, space_required, region))


class FunctionInUseException(DataSpecificationException):
    """ An exception that indicates that a function is already defined
    """

    def __init__(self, function_id):
        """
        :param int function_id: The ID of the function
        """
        super().__init__("Function {0} is already defined".format(function_id))


class RNGInUseException(DataSpecificationException):
    """ An exception that indicates that a random number generator is\
        already defined
    """

    def __init__(self, rng_id):
        """
        :param int rng_id: The ID of the rng
        """
        super().__init__(
            "Random number generator {0} is already defined".format(rng_id))


class RandomNumberDistributionInUseException(DataSpecificationException):
    """ An exception that indicates that a random number distribution is\
        already defined
    """

    def __init__(self, rng_id):
        """
        :param int rng_id: The ID of the random number distribution
        """
        super().__init__(
            "Random number distribution {0} is already defined".format(
                rng_id))


class WrongParameterNumberException(DataSpecificationException):
    """ An exception that indicates that a function has been called with a\
        wrong number of parameters.
    """

    def __init__(self, function_id, no_of_parameters_required, parameters):
        """
        :param int function_id: The ID of the function
        :param list parameters: The parameters used in the function call
        :param int no_of_parameters_required:
            The number of parameters required by the function
        """
        super().__init__(
            "Function {0} that requires {1} parameters has been called "
            "with the following parameters: {2}".format(
                function_id, no_of_parameters_required, parameters))


class DuplicateParameterException(DataSpecificationException):
    """ And exception that indicates that a command has been called with a\
        duplicate parameter, which shouldn't be allowed.
    """

    def __init__(self, command, parameters):
        """
        :param int command: The command called with duplicate parameters
        :param list parameters: The parameters used to call the function
        """
        super().__init__(
            "The command {0} has been called with duplicate parameters: "
            "{1}".format(command, repr(parameters)))


class NestedFunctionException(DataSpecificationException):
    """ An exception that indicates that a function is being defined within\
        the context of another function definition
    """

    def __init__(self):
        super().__init__("Nested function definition not supported")


class TypeMismatchException(DataSpecificationException):
    """ An exception that indicates that a type mismatch has occurred
    """

    def __init__(self, command):
        """
        :param str command: The command that generated the exception
        """
        super().__init__(
            "A type mismatch has occurred during command {0}".format(
                command))


class UnknownTypeException(DataSpecificationException):
    """ An exception that indicates that the value of the requested type\
        is unknown
    """

    def __init__(self, type_id, command):
        """
        :param int type_id: The ID of the requested type
        :param str command: The command being executed
        """
        super().__init__(
            "Unknown ID value {0} for data type during command {1}".format(
                type_id, command))


class UnknownTypeLengthException(DataSpecificationException):
    """ An exception that indicates that the value of the requested type\
        is unknown
    """

    def __init__(self, data_length, command):
        """
        :param int data_length: the length of the requested type
        :param str command: The command being executed
        """
        super().__init__("Unknown data length {0} during command {1}".format(
            data_length, command))


class InvalidSizeException(DataSpecificationException):
    """ An exception that indicates that the size of the requested type is\
        invalid
    """

    def __init__(self, type_name, type_size, command):
        """
        :param str type_name: The name of the requested type
        :param int type_size: The size of the requested variable
        :param str command: The command being executed
        """
        super().__init__(
            "Invalid size {0} of the requested type {1} during "
            "command {2}".format(type_size, type_name, command))


class InvalidCommandException(DataSpecificationException):
    """ An exception that indicates that the command being requested cannot\
        be executed at this point in the specification.
    """

    def __init__(self, command):
        """
        :param str command: The command being executed
        """
        super().__init__(
            "The requested command {0} cannot be executed at this point "
            "in the specification".format(command))


class UnknownConditionException(DataSpecificationException):
    """ And exception which is triggered in case the condition in an IF test\
        does not exist in the list of possible conditions
    """

    def __init__(self, condition_id, command):
        """
        :param int condition_id: ID of the condition being requested
        :param str command: The command being executed
        """
        super().__init__(
            "The requested condition with ID {0} does not belong to the "
            "list of possible tests during command {1}".format(
                condition_id, command))


class InvalidOperationException(DataSpecificationException):
    """ An exception that indicates that the operation of the type given type\
        is not available.
    """

    def __init__(self, operation_type, requested_operation_id, command):
        """
        :param str operation_type:
            The type of operation requested (i.e. arithmetic or logic)
        :param int requested_operation_id: The ID of the requested operation
        :param str command: The command being executed
        """
        super().__init__(
            "The {0} operation requested with ID {1} does not match "
            "the possible operations available during command {2}".format(
                operation_type, requested_operation_id, command))


class ExecuteBreakInstruction(DataSpecificationException):
    """ An exception which occurs when a BREAK instruction is found in the\
        data specification.
    """

    def __init__(self, address, filename):
        """
        :param int address: address of the data specification being executed
            at the time of breakpoint
        :param str filename: file being parsed
        """
        super().__init__(
            "Executing BREAK instruction at address {0} of file {1}"
            .format(address, filename))


class DataSpecificationSyntaxError(DataSpecificationException):
    """ An exception which occurs when a command read from the data\
        specification file shows an inconsistency in the binary content.
    """


class TablePointerOutOfMemoryException(DataSpecificationException):
    """ An exception which occurs when building the table pointer as header of\
        the data generated by the spec executor. This message is printed in\
        case the memory available is not enough to contain the pointer table\
        for each of the allocated regions.
    """

    def __init__(self, memory_available, memory_required):
        """

        :param int memory_available: on-chip memory available
        :param int memory_required: on-chip memory required to complete the
            execution of the specification file
        """
        super().__init__(
            "The memory available {0} is not sufficient for the allocated"
            " regions plus the header table pointer {1}".format(
                memory_available, memory_required))


class RegionNotAllocatedException(DataSpecificationException):
    """ An exception which occurs when trying to write to an unallocated\
        region of memory
    """

    def __init__(self, region, command):
        """
        :param int region: The ID of the region that was not allocated.
        :param str command: The name of the command that was being handled.
        """
        super().__init__(
            "Region {0} has not been allocated during execution of "
            "command {1}".format(region, command))


class UnimplementedDSECommandError(DataSpecificationException):
    """ An exception which occurs when trying to execute an unimplemented\
        command
    """

    def __init__(self, command):
        """
        :param str command: Command attempted to be executed by the DSE
        """
        super().__init__(
            "Command {0} in the data specification executor has not yet "
            "been implemented".format(command))


class UnimplementedDSGCommandError(DataSpecificationException):
    """ An exception which occurs when trying to write an unimplemented\
        command
    """

    def __init__(self, command):
        """
        :param str command: Command attempted to be generated by the DSG
        """
        super().__init__(
            "Command {0} in the data specification generator has not yet "
            "been implemented".format(command))
