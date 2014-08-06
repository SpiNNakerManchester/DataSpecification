from data_specification import constants, exceptions, memory_region_collection
import struct


class DataSpecificationExecutorFunctions:
    """
    This class includes the function related to each of the commands
    of the data specification file.
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
        """
        self.spec_reader = spec_reader
        self.mem_writer = mem_writer
        self.space_available = space_available

        self.space_allocated = 0
        self.current_region = None

        self.registers = [0] * constants.MAX_REGISTERS
        self.mem_regions = memory_region_collection.MemoryRegionCollection(
            constants.MAX_MEM_REGIONS)
        self.struct_slots = [0] * constants.MAX_STRUCT_SLOTS
        self.wr_ptr = [None] * constants.MAX_MEM_REGIONS

    def __unpack_cmd__(self, cmd):
        self._cmd_size = (cmd >> 28) & 0x3
        self.opcode = (cmd >> 20) & 0xFF
        self.use_dest_reg = (cmd >> 18) & 0x1 == 0x1
        self.use_src1_reg = (cmd >> 17) & 0x1 == 0x1
        self.use_src2_reg = (cmd >> 16) & 0x1 == 0x1
        self.dest_reg = (cmd >> 12) & 0xF
        self.src1_reg = (cmd >> 8) & 0xF
        self.src2_reg = (cmd >> 4) & 0xF
        self.data_len = (cmd >> 12) & 0x3

    def execute_break(self, cmd):
        raise exceptions.ExecuteBreakInstruction(
            self.spec_reader.tell(), self.spec_reader.filename)

    def execute_nop(self, cmd):
        pass

    def execute_reserve(self, cmd):
        """

        :param cmd:
        :return:
        :raise data_specification.exceptions.DataSpecificationException:\
            If there is an error when executing the specification
        """
        self.__unpack_cmd__(cmd)
        region = cmd & 0x1F  # cmd[4:0]

        if self._cmd_size != constants.LEN2:
            raise exceptions.DataSpecificationSyntaxError(
                "Command {0:s} requires one word as argument (total 2 words), "
                "but the current encoding ({1:X}) is specified to be {2:d} "
                "words long".format(
                    "RESERVE", cmd, self._cmd_size))

        unfilled = (cmd >> 7) & 0x1 == 0x1

        if not self.mem_regions.is_empty(region):
            raise exceptions.DataSpecificationRegionInUseException(region)

        size_encoded = self.spec_reader.read(4)
        size = struct.unpack("<I", size_encoded)[0]
        if size & 0x3 != 0:
            size = (size + 4) - (size & 0x3)

        if (size <= 0) or size > (self.space_available - self.space_allocated):
            raise exceptions.DataSpecificationParameterOutOfBoundsException(
                "region size", size, 1,
                (self.space_available-self.space_allocated),
                "RESERVE"
            )

        self.mem_regions[region] = bytearray(size)
        if unfilled:
            self.mem_regions.set_unfilled(region)
        else:
            self.mem_regions.set_filled(region)

        self.wr_ptr[region] = 0
        self.space_allocated += size

    def execute_free(self, cmd):
        pass

    def execute_declare_rng(self, cmd):
        pass

    def execute_random_dist(self, cmd):
        pass

    def execute_get_random_rumber(self, cmd):
        pass

    def execute_start_struct(self, cmd):
        pass

    def execute_struct_elem(self, cmd):
        pass

    def execute_end_struct(self, cmd):
        pass

    def execute_start_constructor(self, cmd):
        pass

    def execute_end_constructor(self, cmd):
        pass

    def execute_construct(self, cmd):
        pass

    def execute_write(self, cmd):
        self.__unpack_cmd__(cmd)

        if self.use_src2_reg:
            n_repeats = self.registers[self.src2_reg]
        else:
            n_repeats = cmd & 0xFF

        data_len = 0
        if self.data_len == 0:
            data_len = 1
        elif self.data_len == 1:
            data_len = 2
        elif self.data_len == 2:
            data_len = 4
        elif self.data_len == 3:
            data_len = 8

        if self.use_src1_reg:
            value = self.registers[self.src1_reg]
        else:
            if self._cmd_size == constants.LEN2 and data_len != 8:
                read_data = self.spec_reader.read(4)
                value = struct.unpack("<I", read_data)[0]
            elif self._cmd_size == constants.LEN3 and data_len == 8:
                read_data = self.spec_reader.read(8)
                value = struct.unpack("<Q", read_data)[0]
            else:
                raise exceptions.DataSpecificationSyntaxError(
                    "Command {0:s} requires a value as an argument, but the "
                    "current encoding ({1:X}) is specified to be {2:d} words "
                    "long and the data length command argument is specified to "
                    "be {3:d} bytes long".format(
                        "WRITE", cmd, self._cmd_size,
                        data_len))

        # Perform the writes
        self._write_to_mem(
            value, data_len, n_repeats, "WRITE")

    def execute_write_array(self, cmd):
        pass

    def execute_write_struct(self, cmd):
        pass

    def execute_block_copy(self, cmd):
        pass

    def execute_switch_focus(self, cmd):
        self.__unpack_cmd__(cmd)

        if not self.use_src1_reg:
            region = (cmd >> 8) & 0xF
        else:
            region = self.registers[self.src1_reg]

        if self.mem_regions.is_empty(region):
            raise exceptions.DataSpecificationRegionUnfilledException(
                region, "SWITCH_FOCUS")
        else:
            self.current_region = region

    def execute_loop(self, cmd):
        pass

    def execute_break_loop(self, cmd):
        pass

    def execute_end_loop(self, cmd):
        pass

    def execute_if(self, cmd):
        pass

    def execute_else(self, cmd):
        pass

    def execute_end_if(self, cmd):
        pass

    def execute_mv(self, cmd):
        pass

    def execute_get_wr_ptr(self, cmd):
        pass

    def execute_set_wr_ptr(self, cmd):
        pass

    def execute_align_wr_ptr(self, cmd):
        pass

    def execute_arith_op(self, cmd):
        pass

    def execute_logic_op(self, cmd):
        pass

    def execute_reformat(self, cmd):
        pass

    def execute_copy_struct(self, cmd):
        pass

    def execute_copy_param(self, cmd):
        pass

    def execute_write_param(self, cmd):
        pass

    def execute_write_param_component(self, cmd):
        pass

    def execute_print_val(self, cmd):
        pass

    def execute_print_txt(self, cmd):
        pass

    def execute_print_struct(self, cmd):
        pass

    def execute_end_spec(self, cmd):
        pass

    def _write_to_mem(self, value, n_bytes, repeat, command):
        """Write to a memory array.

        If a memory slot is not assigned the current memory slot is used.
        Likewise, if neither the aligned or offset pointers are provided the
        next free space in memory is used.

        The resultant pointers are returned and may need writing back to the
        memory slot.
        """

        if self.current_region is None:
            raise exceptions.DataSpecificationNoRegionSelectedException(
                command)

        if self.mem_regions[self.current_region] is None:
            raise exceptions.DataSpecificationRegionNotAllocated(
                self.current_region, command)

        space_allocated = len(self.mem_regions[self.current_region])
        space_used = self.wr_ptr[self.current_region]
        space_available = space_allocated - space_used
        space_required = n_bytes * repeat

        if space_available < space_required:
            raise exceptions.DataSpecificationNoMoreException(
                space_available, space_required)

        if n_bytes == 1:
            encoded_value = struct.pack("<B", value)
        elif n_bytes == 2:
            encoded_value = struct.pack("<H", value)
        elif n_bytes == 4:
            encoded_value = struct.pack("<I", value)
        elif n_bytes == 8:
            encoded_value = struct.pack("<Q", value)
        else:
            raise exceptions.DataSpecificationUnknownTypeLengthException(
                n_bytes, command)

        encoded_array = encoded_value * repeat
        current_write_ptr = self.wr_ptr[self.current_region]
        self.mem_regions[self.current_region][current_write_ptr:current_write_ptr + len(encoded_array)] = encoded_array
        self.wr_ptr += len(encoded_array)