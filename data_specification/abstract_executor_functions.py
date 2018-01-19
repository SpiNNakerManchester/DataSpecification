from .exceptions import UnimplementedDSECommandError


class AbstractExecutorFunctions(object):
    """This class defines a function related to each of the commands of the\
        data specification file. Subclasses need to provide implementations\
        that work for the operations they wish to support.
    """
    # pylint: disable=unused-argument

    __slots__ = []

    def execute_break(self, cmd):
        raise UnimplementedDSECommandError("BREAK")

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
        raise UnimplementedDSECommandError("RESERVE")

    def execute_free(self, cmd):
        raise UnimplementedDSECommandError("FREE")

    def execute_declare_rng(self, cmd):
        raise UnimplementedDSECommandError("DECLARE_RNG")

    def execute_random_dist(self, cmd):
        raise UnimplementedDSECommandError("DECLARE_RANDOM_DIST")

    def execute_get_random_rumber(self, cmd):
        raise UnimplementedDSECommandError("GET_RANDOM_NUMBER")

    def execute_start_struct(self, cmd):
        raise UnimplementedDSECommandError("START_STRUCT")

    def execute_struct_elem(self, cmd):
        raise UnimplementedDSECommandError("STRUCT_ELEM")

    def execute_end_struct(self, cmd):
        raise UnimplementedDSECommandError("END_STRUCT")

    def execute_start_constructor(self, cmd):
        raise UnimplementedDSECommandError("START_CONSTRUCTOR")

    def execute_end_constructor(self, cmd):
        raise UnimplementedDSECommandError("END_CONSTRUCTOR")

    def execute_construct(self, cmd):
        raise UnimplementedDSECommandError("CONSTRUCT")

    def execute_read(self, cmd):
        raise UnimplementedDSECommandError("READ")

    def execute_write(self, cmd):
        raise UnimplementedDSECommandError("WRITE")

    def execute_write_array(self, cmd):
        raise UnimplementedDSECommandError("WRITE_ARRAY")

    def execute_write_struct(self, cmd):
        raise UnimplementedDSECommandError("WRITE_STRUCT")

    def execute_block_copy(self, cmd):
        raise UnimplementedDSECommandError("BLOCK_COPY")

    def execute_switch_focus(self, cmd):
        raise UnimplementedDSECommandError("SWITCH_FOCUS")

    def execute_loop(self, cmd):
        raise UnimplementedDSECommandError("LOOP")

    def execute_break_loop(self, cmd):
        raise UnimplementedDSECommandError("BREAK_LOOP")

    def execute_end_loop(self, cmd):
        raise UnimplementedDSECommandError("END_LOOP")

    def execute_if(self, cmd):
        raise UnimplementedDSECommandError("IF")

    def execute_else(self, cmd):
        raise UnimplementedDSECommandError("ELSE")

    def execute_end_if(self, cmd):
        raise UnimplementedDSECommandError("ENDIF")

    def execute_mv(self, cmd):
        raise UnimplementedDSECommandError("MV")

    def execute_get_wr_ptr(self, cmd):
        raise UnimplementedDSECommandError("GET_WR_PTR")

    def execute_set_wr_ptr(self, cmd):
        raise UnimplementedDSECommandError("SET_WR_PTR")

    def execute_reset_wr_ptr(self, cmd):
        raise UnimplementedDSECommandError("RESET_RW_PTR")

    def execute_align_wr_ptr(self, cmd):
        raise UnimplementedDSECommandError("ALIGN_WR_PTR")

    def execute_arith_op(self, cmd):
        raise UnimplementedDSECommandError("ARITH_OP")

    def execute_logic_op(self, cmd):
        raise UnimplementedDSECommandError("LOGIC_OP")

    def execute_reformat(self, cmd):
        raise UnimplementedDSECommandError("REFORMAT")

    def execute_copy_struct(self, cmd):
        raise UnimplementedDSECommandError("COPY_STRUCT")

    def execute_copy_param(self, cmd):
        raise UnimplementedDSECommandError("COPY_PARAM")

    def execute_write_param(self, cmd):
        raise UnimplementedDSECommandError("WRITE_PARAM")

    def execute_write_param_component(self, cmd):
        raise UnimplementedDSECommandError("WRITE_PARAM_COMPONENT")

    def execute_print_val(self, cmd):
        raise UnimplementedDSECommandError("PRINT_VAL")

    def execute_print_txt(self, cmd):
        raise UnimplementedDSECommandError("PRINT_TXT")

    def execute_print_struct(self, cmd):
        raise UnimplementedDSECommandError("PRINT_STRUCT")

    def execute_read_param(self, cmd):
        raise UnimplementedDSECommandError("READ_PARAM")

    def execute_end_spec(self, cmd):
        raise UnimplementedDSECommandError("END_SPEC")
