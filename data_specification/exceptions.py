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


class DataSpecificationException(Exception):
    """
    A general purpose exception indicating that something went
    wrong when interacting with a Data Specification.
    """


class RegionInUseException(DataSpecificationException):
    """
    An exception that indicates that a region has already been allocated.
    """

    def __init__(self, region, label=None):
        """
        :param int region: The region that was already allocated
        :param label: What label is known for the region
        :type label: str or None
        """
        if label is None:
            msg = f"Region {region:d} was already allocated"
        else:
            msg = f"Region {region:d} ({label}) was already allocated"
        super().__init__(msg)


class RegionUnfilledException(DataSpecificationException):
    """
    An exception that indicates that a memory region is being used
    that was originally requested to be unfilled.
    """

    def __init__(self, region, command):
        """
        :param int region: The region that was requested as unfilled
        :param str command: The command being executed
        """
        super().__init__(
            f"Region {region} was requested unfilled, but command {command} "
            "requests its use")


class NoRegionSelectedException(DataSpecificationException):
    """
    An exception that indicates that a memory region has not been selected.
    """

    def __init__(self, command):
        """
        :param str command: The command being executed
        """
        super().__init__(
            f"Command {command} tries to operate on an unspecified "
            "memory region")


class RegionExhaustedException(DataSpecificationException):
    """
    An exception that indicates that a region has run out of memory
    whilst some data is being written.
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
            f"Region {region} with size {region_size} ran out of allocated "
            f"memory (space already occupied {allocated_size}) during "
            f"command {command}")


class RegionOutOfBoundsException(DataSpecificationException):
    """
    An exception that indicates that an offset into a region is out
    of bounds for that region.
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
            f"Requesting offset {requested_offset} into region {region} "
            f"with size {region_size} during command {command}")


class ParameterOutOfBoundsException(DataSpecificationException):
    """
    An exception that indicates that a parameter value was outside of the
    allowed bounds.
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
            f"Requesting value {value} for parameter {parameter} whose "
            f"allowed range is from {range_min} to {range_max} during "
            f"command {command}")


class NotAllocatedException(DataSpecificationException):
    """
    An exception that indicates that an item is being used
    that has not been allocated.
    """

    def __init__(self, item_type, item_id, command):
        """
        :param str item_type: The type of the item being used
        :param int item_id: The ID of the item being used
        :param str command: The command being executed
        """
        super().__init__(
            f"Using unallocated item with type {item_type} and ID {item_id} "
            f"during command {command}")


class NoMoreException(DataSpecificationException):
    """
    An exception that indicates that there is no more space for the
    requested item.
    """

    def __init__(self, space_available, space_required, region):
        """
        :param int space_available: The space available in the region
        :param int space_required: The space requested by the write command
        """
        super().__init__(
            "Space unavailable to write all the elements requested by the "
            f"write operation. Space available: {space_available}; space "
            f"requested: {space_required} for region {region}.")


class NestedFunctionException(DataSpecificationException):
    """
    An exception that indicates that a function is being defined within
    the context of another function definition.
    """

    def __init__(self):
        super().__init__("Nested function definition not supported")


class TypeMismatchException(DataSpecificationException):
    """
    An exception that indicates that a type mismatch has occurred.
    """

    def __init__(self, command):
        """
        :param str command: The command that generated the exception
        """
        super().__init__(
            f"A type mismatch has occurred during command {command}")


class UnknownTypeException(DataSpecificationException):
    """
    An exception that indicates that the value of the requested type
    is unknown.
    """

    def __init__(self, type_id, command):
        """
        :param int type_id: The ID of the requested type
        :param str command: The command being executed
        """
        super().__init__(
            f"Unknown ID value {type_id} for data type during "
            f"command {command}")


class UnknownTypeLengthException(DataSpecificationException):
    """
    An exception that indicates that the value of the requested type
    is unknown.
    """

    def __init__(self, data_length, command):
        """
        :param int data_length: the length of the requested type
        :param str command: The command being executed
        """
        super().__init__(
            f"Unknown data length {data_length} during command {command}")


class InvalidSizeException(DataSpecificationException):
    """
    An exception that indicates that the size of the requested type is invalid.
    """

    def __init__(self, type_name, type_size, command):
        """
        :param str type_name: The name of the requested type
        :param int type_size: The size of the requested variable
        :param str command: The command being executed
        """
        super().__init__(
            f"Invalid size {type_size} of the requested type {type_name} "
            f"during command {command}")


class DataSpecificationSyntaxError(DataSpecificationException):
    """
    An exception which occurs when a command read from the data
    specification file shows an inconsistency in the binary content.
    """


class TablePointerOutOfMemoryException(DataSpecificationException):
    """
    An exception which occurs when building the table pointer as header of the
    data generated by the spec executor. This message is printed in case the
    memory available is not enough to contain the pointer table for each of
    the allocated regions.
    """

    def __init__(self, memory_available, memory_required):
        """

        :param int memory_available: on-chip memory available
        :param int memory_required: on-chip memory required to complete the
            execution of the specification file
        """
        super().__init__(
            f"The memory available {memory_available} is not sufficient for "
            "the allocated regions plus the header table "
            f"pointer {memory_required}")


class RegionNotAllocatedException(DataSpecificationException):
    """
    An exception which occurs when trying to write to an unallocated
    region of memory.
    """

    def __init__(self, region, command):
        """
        :param int region: The ID of the region that was not allocated.
        :param str command: The name of the command that was being handled.
        """
        super().__init__(
            f"Region {region} has not been allocated during execution of "
            f"command {command}")


class UnimplementedDSECommandError(DataSpecificationException):
    """
    An exception which occurs when trying to execute an unimplemented
    command.
    """

    def __init__(self, command):
        """
        :param str command: Command attempted to be executed by the DSE
        """
        super().__init__(
            f"Command {command} in the data specification executor has "
            "not yet been implemented")


class UnimplementedDSGCommandError(DataSpecificationException):
    """
    An exception which occurs when trying to write an unimplemented command.
    """

    def __init__(self, command):
        """
        :param str command: Command attempted to be generated by the DSG
        """
        super().__init__(
            f"Command {command} in the data specification generator has "
            "not yet been implemented")
