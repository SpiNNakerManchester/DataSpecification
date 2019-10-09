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

from .exceptions import UnimplementedDSECommandError


class AbstractExecutorFunctions(object):
    """ This class defines a function related to each of the commands of the\
        data specification file. Subclasses need to provide implementations\
        that work for the operations they wish to support.
    """
    # pylint: disable=unused-argument

    __slots__ = []

    def execute_break(self, cmd):  # pragma: no cover
        raise UnimplementedDSECommandError("BREAK")

    def execute_nop(self, cmd):
        """ This command executes no operation.

        :param cmd: the command which triggered the function call
        :type cmd: int
        :return: No value returned
        :rtype: None
        """

    def execute_reserve(self, cmd):  # pragma: no cover
        raise UnimplementedDSECommandError("RESERVE")

    def execute_free(self, cmd):  # pragma: no cover
        raise UnimplementedDSECommandError("FREE")

    def execute_declare_rng(self, cmd):  # pragma: no cover
        raise UnimplementedDSECommandError("DECLARE_RNG")

    def execute_random_dist(self, cmd):  # pragma: no cover
        raise UnimplementedDSECommandError("DECLARE_RANDOM_DIST")

    def execute_get_random_rumber(self, cmd):  # pragma: no cover
        raise UnimplementedDSECommandError("GET_RANDOM_NUMBER")

    def execute_start_struct(self, cmd):  # pragma: no cover
        raise UnimplementedDSECommandError("START_STRUCT")

    def execute_struct_elem(self, cmd):  # pragma: no cover
        raise UnimplementedDSECommandError("STRUCT_ELEM")

    def execute_end_struct(self, cmd):  # pragma: no cover
        raise UnimplementedDSECommandError("END_STRUCT")

    def execute_start_constructor(self, cmd):  # pragma: no cover
        raise UnimplementedDSECommandError("START_CONSTRUCTOR")

    def execute_end_constructor(self, cmd):  # pragma: no cover
        raise UnimplementedDSECommandError("END_CONSTRUCTOR")

    def execute_construct(self, cmd):  # pragma: no cover
        raise UnimplementedDSECommandError("CONSTRUCT")

    def execute_read(self, cmd):  # pragma: no cover
        raise UnimplementedDSECommandError("READ")

    def execute_write(self, cmd):  # pragma: no cover
        raise UnimplementedDSECommandError("WRITE")

    def execute_write_array(self, cmd):  # pragma: no cover
        raise UnimplementedDSECommandError("WRITE_ARRAY")

    def execute_write_struct(self, cmd):  # pragma: no cover
        raise UnimplementedDSECommandError("WRITE_STRUCT")

    def execute_block_copy(self, cmd):  # pragma: no cover
        raise UnimplementedDSECommandError("BLOCK_COPY")

    def execute_switch_focus(self, cmd):  # pragma: no cover
        raise UnimplementedDSECommandError("SWITCH_FOCUS")

    def execute_loop(self, cmd):  # pragma: no cover
        raise UnimplementedDSECommandError("LOOP")

    def execute_break_loop(self, cmd):  # pragma: no cover
        raise UnimplementedDSECommandError("BREAK_LOOP")

    def execute_end_loop(self, cmd):  # pragma: no cover
        raise UnimplementedDSECommandError("END_LOOP")

    def execute_if(self, cmd):  # pragma: no cover
        raise UnimplementedDSECommandError("IF")

    def execute_else(self, cmd):  # pragma: no cover
        raise UnimplementedDSECommandError("ELSE")

    def execute_end_if(self, cmd):  # pragma: no cover
        raise UnimplementedDSECommandError("ENDIF")

    def execute_mv(self, cmd):  # pragma: no cover
        raise UnimplementedDSECommandError("MV")

    def execute_get_wr_ptr(self, cmd):  # pragma: no cover
        raise UnimplementedDSECommandError("GET_WR_PTR")

    def execute_set_wr_ptr(self, cmd):  # pragma: no cover
        raise UnimplementedDSECommandError("SET_WR_PTR")

    def execute_reset_wr_ptr(self, cmd):  # pragma: no cover
        raise UnimplementedDSECommandError("RESET_RW_PTR")

    def execute_align_wr_ptr(self, cmd):  # pragma: no cover
        raise UnimplementedDSECommandError("ALIGN_WR_PTR")

    def execute_arith_op(self, cmd):  # pragma: no cover
        raise UnimplementedDSECommandError("ARITH_OP")

    def execute_logic_op(self, cmd):  # pragma: no cover
        raise UnimplementedDSECommandError("LOGIC_OP")

    def execute_reformat(self, cmd):  # pragma: no cover
        raise UnimplementedDSECommandError("REFORMAT")

    def execute_copy_struct(self, cmd):  # pragma: no cover
        raise UnimplementedDSECommandError("COPY_STRUCT")

    def execute_copy_param(self, cmd):  # pragma: no cover
        raise UnimplementedDSECommandError("COPY_PARAM")

    def execute_write_param(self, cmd):  # pragma: no cover
        raise UnimplementedDSECommandError("WRITE_PARAM")

    def execute_write_param_component(self, cmd):  # pragma: no cover
        raise UnimplementedDSECommandError("WRITE_PARAM_COMPONENT")

    def execute_print_val(self, cmd):  # pragma: no cover
        raise UnimplementedDSECommandError("PRINT_VAL")

    def execute_print_txt(self, cmd):  # pragma: no cover
        raise UnimplementedDSECommandError("PRINT_TXT")

    def execute_print_struct(self, cmd):  # pragma: no cover
        raise UnimplementedDSECommandError("PRINT_STRUCT")

    def execute_read_param(self, cmd):  # pragma: no cover
        raise UnimplementedDSECommandError("READ_PARAM")

    def execute_end_spec(self, cmd):  # pragma: no cover
        raise UnimplementedDSECommandError("END_SPEC")
