from data_specification.data_specification_executor_functions \
    import DataSpecificationExecutorFunctions as dsef
from data_specification import exceptions, constants
from enums import commands
import struct


class DataSpecificationExecutor(object):
    """ Used to execute a data specification language file to produce a memory\
        image
    """
    
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
        self.dsef = dsef(self.spec_reader, self.mem_writer, self.space_available)
    
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
        """
        for instruction_spec in iter(lambda: self.spec_reader.read(4), ''):
            #process the received command
            cmd = struct.unpack(">I", instruction_spec)[0]

            opcode = (cmd >> 20) & 0xFF

            try:
                return_value = commands.Commands(opcode).exec_function(dsef, cmd)
            except ValueError:
                raise exceptions.DataSpecificationException(
                    "Invalid command 0x{0:X} while reading file {2:s}".format(
                        cmd, self.spec_reader.filename))

            if return_value == constants.END_SPEC_EXECUTOR:
                break
        #write here the files from dsef.mem_regions

        used_regions = self.dsef.mem_regions.count_used_regions()
        tbl_pointers = [0] * used_regions
        tbl_pointers_size = used_regions * 4
        self.space_used += tbl_pointers_size

        id = 0
        tbl_pointers[id] = tbl_pointers_size

        for i in self.dsef.mem_regions.regions():
            if i is not None:
                region_size = len(i)
                self.space_used += region_size
                if id != used_regions:
                    id += 1
                    tbl_pointers[id] = tbl_pointers[id - 1] + region_size

        if self.space_used + tbl_pointers_size > self.space_available:
            raise exceptions.DataSpecificationTablePointerOutOfMemory(
                self.space_available, (self.space_used + tbl_pointers_size))

        for i in tbl_pointers:
            encoded_pointer = struct.pack("<I", i)
            self.mem_writer(encoded_pointer)

        for i in self.dsef.mem_regions.regions():
            self.mem_writer(i)

        return self.space_used