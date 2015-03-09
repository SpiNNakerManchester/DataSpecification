import struct

from data_specification.data_specification_executor_functions \
    import DataSpecificationExecutorFunctions as Dsef
from data_specification import exceptions, constants
from data_specification.enums import commands


class DataSpecificationExecutor(object):
    """ Used to execute a data specification language file to produce a memory\
        image
    """
    
    def __init__(self, spec_reader, mem_writer, space_available,
                 report_writer=None):
        """
        :param spec_reader: The object to read the specification language file\
                    from
        :type spec_reader:\
                    :py:class:`data_specification.abstract_data_reader.\
                    AbstractDataReader`
        :param mem_writer: The object to write the memory image to
        :type mem_writer:\
                    :py:class:`data_specification.abstract_data_writer.
                    AbstractDataWriter`
        :param space_available: memory available (in bytes) for the data
        :type space_available: int
        :param report_writer: The object to write the report of the data \
                    specification executor
        :type report_writer:\
                    :py:class:`data_specification.abstract_data_writer.
                    AbstractDataWriter`
        :raise data_specification.exceptions.DataReadException:\
                    If a read from external storage fails
        :raise data_specification.exceptions.DataWriteException:\
                    If a write to external storage fails
        """
        self.spec_reader = spec_reader
        self.mem_writer = mem_writer
        self.report_writer = report_writer
        self.space_available = space_available
        self.space_used = 0
        self.space_written = 0
        self.dsef = Dsef(
            self.spec_reader, self.mem_writer, self.space_available)
    
    def execute(self):
        """ Executes the specification
        
        :return: The number of bytes used by the image and \
                the number of bytes written by the image
        :rtype: int
        :raise data_specification.exceptions.DataReadException:\
                    If a read from external storage fails
        :raise data_specification.exceptions.DataWriteException:\
                    If a write to external storage fails
        :raise data_specification.exceptions.DataSpecificationException:\
                    If there is an error when executing the specification
        :raise data_specification.exceptions.\
                    DataSpecificationTablePointerOutOfMemory:\
                    If the table pointer generated as data header exceeds the \
                    size of the available memory
        """
        instruction_spec = self.spec_reader.read(4)
        while len(instruction_spec) != 0:
            # process the received command
            cmd = struct.unpack("<I", str(instruction_spec))[0]

            opcode = (cmd >> 20) & 0xFF

            try:
                # noinspection PyArgumentList
                return_value = \
                    commands.Commands(opcode).exec_function(self.dsef, cmd)
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

        # take into account what has just been written to file
        self.space_written = self.space_used

        # write the data from dsef.mem_regions previously computed
        for i in xrange(constants.MAX_MEM_REGIONS):
            memory_region = self.dsef.mem_regions[i]
            if memory_region is not None:
                if ((memory_region.unfilled and
                    self.dsef.mem_regions.needs_to_write_region(i)) or
                        not memory_region.unfilled):
                    self.mem_writer.write(memory_region.region_data)
                else:
                    self.space_written -= memory_region.allocated_size
        return self.space_used, self.space_written

    def write_header(self):
        """ writes the DSE header which resides at the top of any cores
        memory region when used with a DSE.

        :return: None
        :raise None: this method does not raise any known exceptions
        """
        if self.report_writer is not None:
            self.report_writer.write("header structure \n")
        magic_number_encoded = bytearray(
            struct.pack("<I", constants.APPDATA_MAGIC_NUM))

        if self.report_writer is not None:
            self.report_writer.write(
                "{} Magic number - file identifier: {} \n".format(
                    self.mem_writer.tell(), constants.APPDATA_MAGIC_NUM))
        self.mem_writer.write(magic_number_encoded)

        version_encoded = bytearray(
            struct.pack("<I", constants.DSE_VERSION))
        if self.report_writer is not None:
            self.report_writer.write(
                "{} File structure version: {} \n".format(
                    self.mem_writer.tell(), constants.DSE_VERSION))
        self.mem_writer.write(version_encoded)

        self.space_used = 0

    def write_pointer_table(self):
        """ writes the pointer table which defines at what memory address
        each memory region starts at as well as the size of each region

        :return: None
        :raise None: this method does not raise any known exceptions
        """
        if self.report_writer is not None:
            self.report_writer.write("Pointer table \n")
        pointer_table = [0] * constants.MAX_MEM_REGIONS
        pointer_table_size = constants.MAX_MEM_REGIONS * 4
        self.space_used += \
            pointer_table_size + constants.APP_PTR_TABLE_HEADER_BYTE_SIZE
        next_free_offset = \
            pointer_table_size + constants.APP_PTR_TABLE_HEADER_BYTE_SIZE

        for i in xrange(constants.MAX_MEM_REGIONS):
            memory_region = self.dsef.mem_regions[i]
            if memory_region is not None:
                pointer_table[i] = next_free_offset
                region_size = memory_region.allocated_size
            else:
                pointer_table[i] = 0
                region_size = 0
            self.space_used += region_size
            next_free_offset += region_size

        if self.space_used > self.space_available:
            raise exceptions.DataSpecificationTablePointerOutOfMemory(
                self.space_available, self.space_used)

        index = 0
        for i in pointer_table:
            if self.report_writer is not None:
                self.report_writer.write(
                    "{:8X} pointer {:d}: {:8X} \n".format(
                        self.mem_writer.tell(), index, i))
            encoded_pointer = struct.pack("<I", i)
            self.mem_writer.write(encoded_pointer)
            index += 1

        if self.report_writer is not None:
            self.report_writer.write("End of pointer table \n")