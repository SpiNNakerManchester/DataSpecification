import struct

from data_specification.data_specification_executor_functions \
    import DataSpecificationExecutorFunctions as Dsef
from data_specification import exceptions, constants
from data_specification.enums import commands


class DataSpecificationExecutor(object):
    """ Used to execute a data specification language file to produce a memory\
        image
    """
    MAGIC_NUMBER = 0xAD130AD6
    VERSION = 1
    
    def __init__(self, spec_reader, mem_writer, space_available):
        """
        :param spec_reader: The object to read the specification language file\
                    from
        :type spec_reader:\
                    :py:class:`data_specification.abstract_data_reader.AbstractDataReader`
        :param mem_writer: The object to write the memory image to
        :type mem_writer:\
                    :py:class:`data_specification.abstract_data_writer.AbstractDataWriter`
        :param space_available: memory available (in bytes) for the data
        :type space_available: int
        :raise data_specification.exceptions.DataReadException:\
                    If a read from external storage fails
        :raise data_specification.exceptions.DataWriteException:\
                    If a write to external storage fails
        """
        self.spec_reader = spec_reader
        self.mem_writer = mem_writer
        self.space_available = space_available
        self.space_used = 0
        self.dsef = Dsef(
            self.spec_reader, self.mem_writer, self.space_available)
    
    def execute(self):
        """ Executes the specification
        
        :return: The number of bytes used by the image
        :rtype: int
        :raise data_specification.exceptions.DataReadException:\
                    If a read from external storage fails
        :raise data_specification.exceptions.DataWriteException:\
                    If a write to external storage fails
        :raise data_specification.exceptions.DataSpecificationException:\
                    If there is an error when executing the specification
        :raise data_specification.exceptions.DataSpecificationTablePointerOutOfMemory:
                    If the table pointer generated as data header exceeds the \
                    size of the available memory
        """
        instruction_spec = self.spec_reader.read(4)
        while len(instruction_spec) != 0:
            #process the received command
            cmd = struct.unpack("<I", str(instruction_spec))[0]

            opcode = (cmd >> 20) & 0xFF

            try:
                # noinspection PyArgumentList
                return_value = commands.Commands(opcode).exec_function(
                    self.dsef, cmd)
            except ValueError:
                raise exceptions.DataSpecificationException(
                    "Invalid command 0x{0:X} while reading file {1:s}".format(
                        cmd, self.spec_reader.filename))

            if return_value == constants.END_SPEC_EXECUTOR:
                break
            instruction_spec = self.spec_reader.read(4)

        # write the data file header
        self.write_header()

        # write the table pointer
        self.write_pointer_table()

        # write the data from dsef.mem_regions previously computed
        for i in xrange(constants.MAX_MEM_REGIONS):
            memory_area = self.dsef.mem_regions[i]
            if memory_area is not None:
                self.mem_writer.write(memory_area)

        return self.space_used

    def write_header(self):
        magic_number_encoded = bytearray(
            struct.pack("<I", constants.APPDATA_MAGIC_NUM))
        self.mem_writer.write(magic_number_encoded)
        version_encoded = bytearray(
            struct.pack("<I", constants.DSE_VERSION))
        self.mem_writer.write(version_encoded)

        # number of bytes in the header (2 words = 8 bytes)
        self.space_used = 8

    def write_pointer_table(self):
        pointer_table = [0] * constants.MAX_MEM_REGIONS
        pointer_table_size = constants.MAX_MEM_REGIONS * 4
        self.space_used += pointer_table_size

        index = 0
        pointer_table[index] = self.space_used

        for i in xrange(constants.MAX_MEM_REGIONS):
            memory_area = self.dsef.mem_regions[i]
            if memory_area is not None:
                region_size = len(memory_area)
                self.space_used += region_size
                if index < constants.MAX_MEM_REGIONS - 1:
                    index += 1
                    pointer_table[index] =\
                        pointer_table[index - 1] + region_size
            else:
                pointer_table[index] = 0
                index += 1

        if self.space_used > self.space_available:
            raise exceptions.DataSpecificationTablePointerOutOfMemory(
                self.space_available, self.space_used)

        for i in pointer_table:
            encoded_pointer = struct.pack("<I", i)
            self.mem_writer.write(encoded_pointer)
