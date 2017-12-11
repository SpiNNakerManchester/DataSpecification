from .exceptions import UnimplementedDSECommand


class AbstractExecutorFunctions(object):
    """This class defines a function related to each of the commands of the\
        data specification file. Subclasses need to provide implementations\
        that work for the operations they wish to support.
    """
    # pylint: disable=unused-argument

    __slots__ = []

    def execute_break(self, cmd):
        raise UnimplementedDSECommand("BREAK")

    def execute_nop(self, cmd):
        """
        This command executes no operation

        :param cmd: the command which triggered the function call
        :type cmd: int
        :return: No value returned
        :rtype: None
        """
        pass

    def execute_reserve(self, cmd):
        raise UnimplementedDSECommand("RESERVE")

    def execute_free(self, cmd):
        raise UnimplementedDSECommand("FREE")

    def execute_declare_rng(self, cmd):
        raise UnimplementedDSECommand("DECLARE_RNG")

    def execute_random_dist(self, cmd):
        raise UnimplementedDSECommand("DECLARE_RANDOM_DIST")

    def execute_get_random_rumber(self, cmd):
        raise UnimplementedDSECommand("GET_RANDOM_NUMBER")

    def execute_start_struct(self, cmd):
        raise UnimplementedDSECommand("START_STRUCT")

    def execute_struct_elem(self, cmd):
        raise UnimplementedDSECommand("STRUCT_ELEM")

    def execute_end_struct(self, cmd):
        raise UnimplementedDSECommand("END_STRUCT")

    def execute_start_constructor(self, cmd):
        raise UnimplementedDSECommand("START_CONSTRUCTOR")

    def execute_end_constructor(self, cmd):
        raise UnimplementedDSECommand("END_CONSTRUCTOR")

    def execute_construct(self, cmd):
        raise UnimplementedDSECommand("CONSTRUCT")

    def execute_read(self, cmd):
        raise UnimplementedDSECommand("READ")

    def execute_write(self, cmd):
        raise UnimplementedDSECommand("WRITE")

    def execute_write_array(self, cmd):
        raise UnimplementedDSECommand("WRITE_ARRAY")

    def execute_write_struct(self, cmd):
        raise UnimplementedDSECommand("WRITE_STRUCT")

    def execute_block_copy(self, cmd):
        raise UnimplementedDSECommand("BLOCK_COPY")

    def execute_switch_focus(self, cmd):
        raise UnimplementedDSECommand("SWITCH_FOCUS")

    def execute_loop(self, cmd):
        raise UnimplementedDSECommand("LOOP")

    def execute_break_loop(self, cmd):
        raise UnimplementedDSECommand("BREAK_LOOP")

    def execute_end_loop(self, cmd):
        raise UnimplementedDSECommand("END_LOOP")

    def execute_if(self, cmd):
        raise UnimplementedDSECommand("IF")

    def execute_else(self, cmd):
        raise UnimplementedDSECommand("ELSE")

    def execute_end_if(self, cmd):
        raise UnimplementedDSECommand("ENDIF")

    def execute_mv(self, cmd):
        raise UnimplementedDSECommand("MV")

    def execute_get_wr_ptr(self, cmd):
        raise UnimplementedDSECommand("GET_WR_PTR")

    def execute_set_wr_ptr(self, cmd):
        raise UnimplementedDSECommand("SET_WR_PTR")

    def execute_reset_wr_ptr(self, cmd):
        raise UnimplementedDSECommand("RESET_RW_PTR")

    def execute_align_wr_ptr(self, cmd):
        raise UnimplementedDSECommand("ALIGN_WR_PTR")

    def execute_arith_op(self, cmd):
        raise UnimplementedDSECommand("ARITH_OP")

    def execute_logic_op(self, cmd):
        raise UnimplementedDSECommand("LOGIC_OP")

    def execute_reformat(self, cmd):
        raise UnimplementedDSECommand("REFORMAT")

    def execute_copy_struct(self, cmd):
        raise UnimplementedDSECommand("COPY_STRUCT")

    def execute_copy_param(self, cmd):
        raise UnimplementedDSECommand("COPY_PARAM")

    def execute_write_param(self, cmd):
        raise UnimplementedDSECommand("WRITE_PARAM")

    def execute_write_param_component(self, cmd):
        raise UnimplementedDSECommand("WRITE_PARAM_COMPONENT")

    def execute_print_val(self, cmd):
        raise UnimplementedDSECommand("PRINT_VAL")

    def execute_print_txt(self, cmd):
        raise UnimplementedDSECommand("PRINT_TXT")

    def execute_print_struct(self, cmd):
        raise UnimplementedDSECommand("PRINT_STRUCT")

    def execute_read_param(self, cmd):
        raise UnimplementedDSECommand("READ_PARAM")

    def execute_end_spec(self, cmd):
        raise UnimplementedDSECommand("END_SPEC")
