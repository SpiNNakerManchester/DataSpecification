import logging
import numpy
import struct

from .data_specification_executor_functions \
    import DataSpecificationExecutorFunctions as Dsef
from .constants import APPDATA_MAGIC_NUM, DSE_VERSION, END_SPEC_EXECUTOR, \
    MAX_MEM_REGIONS, APP_PTR_TABLE_BYTE_SIZE, APP_PTR_TABLE_HEADER_BYTE_SIZE
from .enums import Commands
from .exceptions import DataSpecificationException

logger = logging.getLogger(__name__)


class DataSpecificationExecutor(object):
    """ Used to execute a data specification language file to produce a memory\
        image
    """

    __slots__ = [
        # The object to read the specification language file
        "spec_reader",

        # The executer functions
        "dsef"

    ]

    def __init__(self, spec_reader, memory_space):
        """
        :param spec_reader: The object to read the specification language file\
                    from
        :type spec_reader:\
                    :py:class:`data_specification.abstract_data_reader.\
                    AbstractDataReader`
        :param memory_space: memory available on the destination architecture
        :type memory_space: int
        :raise spinn_storage_handlers.exceptions.DataReadException:\
                    If a read from external storage fails
        :raise spinn_storage_handlers.exceptions.DataWriteException:\
                    If a write to external storage fails
        """
        self.spec_reader = spec_reader
        self.dsef = Dsef(self.spec_reader, memory_space)

    def execute(self):
        """ Executes the specification

        :return: The number of bytes used by the image and \
                the number of bytes written by the image
        :rtype: int
        :raise spinn_storage_handlers.exceptions.DataReadException:\
                    If a read from external storage fails
        :raise spinn_storage_handlers.exceptions.DataWriteException:\
                    If a write to external storage fails
        :raise data_specification.exceptions.DataSpecificationException:\
                    If there is an error when executing the specification
        :raise data_specification.exceptions.\
                    DataSpecificationTablePointerOutOfMemory:\
                    If the table pointer generated as data header exceeds the \
                    size of the available memory
        """
        index = 0
        instruction_spec = self.spec_reader.read(4)
        while len(instruction_spec) != 0:
            # process the received command
            cmd = struct.unpack("<I", str(instruction_spec))[0]

            opcode = (cmd >> 20) & 0xFF

            try:
                # noinspection PyArgumentList
                return_value = Commands(opcode).exec_function(self.dsef, cmd)
            except (ValueError, TypeError):
                logger.debug("problem decoding opcode %d at index %d",
                             cmd, index, exc_info=True)
                raise DataSpecificationException(
                    "Invalid command 0x{0:X} while reading file {1:s}".format(
                        cmd, self.spec_reader.filename))

            if return_value == END_SPEC_EXECUTOR:
                break
            instruction_spec = self.spec_reader.read(4)
            index += 4

    def get_region(self, region_id):
        """ Get a region with a given id

        :param region_id: The id of the region to get
        :type region_id: int
        :return: The region, or None if the region was not allocated
        """
        return self.dsef.mem_regions[region_id]

    def get_header(self):
        """ Get the header of the data as a numpy array
        """
        return numpy.array([APPDATA_MAGIC_NUM, DSE_VERSION], dtype="<u4")

    def get_pointer_table(self, start_address):
        """ Get the pointer table as a numpy array

        :param start_address: The base address of the data to be written
        """
        pointer_table = numpy.zeros(MAX_MEM_REGIONS, dtype="<u4")
        pointer_table_size = MAX_MEM_REGIONS * 4
        next_free_offset = pointer_table_size + APP_PTR_TABLE_HEADER_BYTE_SIZE

        for i in xrange(MAX_MEM_REGIONS):
            memory_region = self.dsef.mem_regions[i]
            if memory_region is not None:
                pointer_table[i] = next_free_offset + start_address
                next_free_offset += memory_region.allocated_size
            else:
                pointer_table[i] = 0

        return pointer_table

    def get_constructed_data_size(self):
        """ Return the size of the data that will be written to memory

        :return: size of the data that will be written to memory
        :rtype: unsigned int
        """
        size = APP_PTR_TABLE_BYTE_SIZE
        for i in xrange(MAX_MEM_REGIONS):
            memory_region = self.dsef.mem_regions[i]
            if memory_region is not None:
                size += memory_region.allocated_size
        return size
