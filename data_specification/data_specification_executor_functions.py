from data_specification import constants


class DataSpecificationExecutorFunctions:
    """
    This class includes the function related to each of the commands
    of the data specification file.
    """

    def __init__(self, spec_reader, mem_writer):
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

        self.registers = [0] * constants.MAX_REGISTERS
        self.mem_slots = [0] * constants.MAX_MEM_REGIONS
        self.struct_slots = [0] * constants.MAX_STRUCT_SLOTS

    def __unpack_cmd(self, cmd):
        opcode = (cmd >> 20) & 0xFF
        use_dest_reg = (cmd >> 18) & 0x1 == 0x1
        use_src1_reg = (cmd >> 17) & 0x1 == 0x1
        use_src2_reg = (cmd >> 16) & 0x1 == 0x1
        dest_reg = (cmd >> 12) & 0xF
        src1_reg = (cmd >> 8) & 0xF
        src2_reg = (cmd >> 4) & 0xF
        return [opcode, use_dest_reg, use_src1_reg, use_src2_reg, dest_reg, src1_reg, src2_reg]

    def execute_break(self, cmd):
        pass

    def execute_nop(self, cmd):
        pass

    def execute_reserve(self, cmd):
        pass

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
        pass

    def execute_write_array(self, cmd):
        pass

    def execute_write_struct(self, cmd):
        pass

    def execute_block_copy(self, cmd):
        pass

    def execute_switch_focus(self, cmd):
        pass

    def execute_loop(self, cmd):
        pass

    def execute_brak_loop(self, cmd):
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
