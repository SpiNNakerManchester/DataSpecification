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

from spinn_utilities.abstract_base import AbstractBase
from data_specification.exceptions import UnimplementedDSECommandError


class AbstractExecutorFunctions(object, metaclass=AbstractBase):
    """ This class defines a function related to each of the commands of the\
        data specification file. Subclasses need to provide implementations\
        that work for the operations they wish to support.
    """
    # pylint: disable=unused-argument

    __slots__ = []

    def execute_break(self, cmd):  # pragma: no cover
        """ This command raises an exception to stop the execution of the \
            data spec executor (DSE).

        :param int cmd: the command which triggered the function call
        :return: No value returned
        :raise DataSpecificationSyntaxError:\
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:\
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("BREAK")

    def execute_nop(self, cmd):
        """ This command executes no operation.

        :param int cmd: the command which triggered the function call
        :return: No value returned
        :rtype: None
        :raise DataSpecificationSyntaxError:\
            If there is an error in the command syntax
        """

    def execute_reserve(self, cmd):  # pragma: no cover
        """ This command reserves a region and assigns some memory space \
            to it.

        :param int cmd: the command which triggered the function call
        :return: No value returned
        :raise DataSpecificationSyntaxError:\
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:\
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("RESERVE")

    def execute_free(self, cmd):  # pragma: no cover
        """ This command frees some memory.

        :param int cmd: the command which triggered the function call
        :return: No value returned
        :raise DataSpecificationSyntaxError:\
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:\
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("FREE")

    def execute_declare_rng(self, cmd):  # pragma: no cover
        """ This command declares a random number generator.

        :param int cmd: the command which triggered the function call
        :return: No value returned
        :raise DataSpecificationSyntaxError:\
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:\
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("DECLARE_RNG")

    def execute_random_dist(self, cmd):  # pragma: no cover
        """ This command defines a random disribution.

        :param int cmd: the command which triggered the function call
        :return: No value returned
        :raise DataSpecificationSyntaxError:\
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:\
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("DECLARE_RANDOM_DIST")

    def execute_get_random_rumber(self, cmd):  # pragma: no cover
        """ This command obtains a random number from a distribution.

        :param int cmd: the command which triggered the function call
        :return: No value returned
        :raise DataSpecificationSyntaxError:\
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:\
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("GET_RANDOM_NUMBER")

    def execute_start_struct(self, cmd):  # pragma: no cover
        """ This command starts to define a structure.

        :param int cmd: the command which triggered the function call
        :return: No value returned
        :raise DataSpecificationSyntaxError:\
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:\
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("START_STRUCT")

    def execute_struct_elem(self, cmd):  # pragma: no cover
        """ This command adds an element to a structure.

        :param int cmd: the command which triggered the function call
        :return: No value returned
        :raise DataSpecificationSyntaxError:\
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:\
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("STRUCT_ELEM")

    def execute_end_struct(self, cmd):  # pragma: no cover
        """ This command completes the definition of a structure.

        :param int cmd: the command which triggered the function call
        :return: No value returned
        :raise DataSpecificationSyntaxError:\
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:\
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("END_STRUCT")

    def execute_start_constructor(self, cmd):  # pragma: no cover
        """ This command starts the definition of a function.

        :param int cmd: the command which triggered the function call
        :return: No value returned
        :raise DataSpecificationSyntaxError:\
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:\
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("START_CONSTRUCTOR")

    def execute_end_constructor(self, cmd):  # pragma: no cover
        """ This command ends the definition of a function.

        :param int cmd: the command which triggered the function call
        :return: No value returned
        :raise DataSpecificationSyntaxError:\
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:\
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("END_CONSTRUCTOR")

    def execute_construct(self, cmd):  # pragma: no cover
        """ This command calls a function.

        :param int cmd: the command which triggered the function call
        :return: No value returned
        :raise DataSpecificationSyntaxError:\
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:\
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("CONSTRUCT")

    def execute_read(self, cmd):  # pragma: no cover
        """ This command reads a word from memory.

        :param int cmd: the command which triggered the function call
        :return: No value returned
        :raise DataSpecificationSyntaxError:\
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:\
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("READ")

    def execute_write(self, cmd):  # pragma: no cover
        """ This command writes the given value in the specified region a\
            number of times as identified by either a value in the command \
            or a register value.

        :param int cmd: the command which triggered the function call
        :return: No value returned
        :raise DataSpecificationSyntaxError:\
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:\
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("WRITE")

    def execute_write_array(self, cmd):  # pragma: no cover
        """ This command writes an array of values in the specified region.

        :param int cmd: the command which triggered the function call
        :return: No value returned
        :raise DataSpecificationSyntaxError:\
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:\
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("WRITE_ARRAY")

    def execute_write_struct(self, cmd):  # pragma: no cover
        """ This command writes a structure to memory.

        :param int cmd: the command which triggered the function call
        :return: No value returned
        :raise DataSpecificationSyntaxError:\
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:\
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("WRITE_STRUCT")

    def execute_block_copy(self, cmd):  # pragma: no cover
        """ This command copies a block of memory from one location to \
            another.

        :param int cmd: the command which triggered the function call
        :return: No value returned
        :raise DataSpecificationSyntaxError:\
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:\
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("BLOCK_COPY")

    def execute_switch_focus(self, cmd):  # pragma: no cover
        """ This command switches the focus to the desired, already allocated,\
            memory region.

        :param int cmd: the command which triggered the function call
        :return: No value returned
        :raise DataSpecificationSyntaxError:\
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:\
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("SWITCH_FOCUS")

    def execute_loop(self, cmd):  # pragma: no cover
        """ This command starts a loop.

        :param int cmd: the command which triggered the function call
        :return: No value returned
        :raise DataSpecificationSyntaxError:\
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:\
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("LOOP")

    def execute_break_loop(self, cmd):  # pragma: no cover
        """ This command stops a loop early.

        :param int cmd: the command which triggered the function call
        :return: No value returned
        :raise DataSpecificationSyntaxError:\
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:\
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("BREAK_LOOP")

    def execute_end_loop(self, cmd):  # pragma: no cover
        """ This command finishes a loop.

        :param int cmd: the command which triggered the function call
        :return: No value returned
        :raise DataSpecificationSyntaxError:\
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:\
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("END_LOOP")

    def execute_if(self, cmd):  # pragma: no cover
        """ This command does a conditional branch.

        :param int cmd: the command which triggered the function call
        :return: No value returned
        :raise DataSpecificationSyntaxError:\
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:\
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("IF")

    def execute_else(self, cmd):  # pragma: no cover
        """ This command handles the other branch of a conditional.

        :param int cmd: the command which triggered the function call
        :return: No value returned
        :raise DataSpecificationSyntaxError:\
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:\
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("ELSE")

    def execute_end_if(self, cmd):  # pragma: no cover
        """ This command ends a conditional.

        :param int cmd: the command which triggered the function call
        :return: No value returned
        :raise DataSpecificationSyntaxError:\
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:\
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("ENDIF")

    def execute_mv(self, cmd):  # pragma: no cover
        """ This command moves an immediate value to a register or copies the \
            value of a register to another register.

        :param int cmd: the command which triggered the function call
        :return: No value returned
        :raise DataSpecificationSyntaxError:\
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:\
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("MV")

    def execute_get_wr_ptr(self, cmd):  # pragma: no cover
        """ This command gets the current write pointer.

        :param int cmd: the command which triggered the function call
        :return: No value returned
        :raise DataSpecificationSyntaxError:\
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:\
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("GET_WR_PTR")

    def execute_set_wr_ptr(self, cmd):  # pragma: no cover
        """ This command sets the current write pointer.

        :param int cmd: the command which triggered the function call
        :return: No value returned
        :raise DataSpecificationSyntaxError:\
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:\
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("SET_WR_PTR")

    def execute_reset_wr_ptr(self, cmd):  # pragma: no cover
        """ This command resets the current write pointer to the beginning \
            of the memory region.

        :param int cmd: the command which triggered the function call
        :return: No value returned
        :raise DataSpecificationSyntaxError:\
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:\
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("RESET_RW_PTR")

    def execute_align_wr_ptr(self, cmd):  # pragma: no cover
        """ This command moves the write pointer to be at the start of the \
            next word if it isn't already at the start of a word.

        :param int cmd: the command which triggered the function call
        :return: No value returned
        :raise DataSpecificationSyntaxError:\
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:\
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("ALIGN_WR_PTR")

    def execute_arith_op(self, cmd):  # pragma: no cover
        """ This command performs an arithmetic operation.

        :param int cmd: the command which triggered the function call
        :return: No value returned
        :raise DataSpecificationSyntaxError:\
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:\
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("ARITH_OP")

    def execute_logic_op(self, cmd):  # pragma: no cover
        """ This command performs a logical operation.

        :param int cmd: the command which triggered the function call
        :return: No value returned
        :raise DataSpecificationSyntaxError:\
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:\
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("LOGIC_OP")

    def execute_reformat(self, cmd):  # pragma: no cover
        """ This command is never generated!

        :param int cmd: the command which triggered the function call
        :return: No value returned
        :raise DataSpecificationSyntaxError:\
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:\
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("REFORMAT")

    def execute_copy_struct(self, cmd):  # pragma: no cover
        """ This command copies a structure from one slot to another.

        :param int cmd: the command which triggered the function call
        :return: No value returned
        :raise DataSpecificationSyntaxError:\
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:\
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("COPY_STRUCT")

    def execute_copy_param(self, cmd):  # pragma: no cover
        """ This command copies a field of a structure to another field of \
            a possibly-different structure.

        :param int cmd: the command which triggered the function call
        :return: No value returned
        :raise DataSpecificationSyntaxError:\
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:\
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("COPY_PARAM")

    def execute_write_param(self, cmd):  # pragma: no cover
        """ This command handles a single element of a structure.

        :param int cmd: the command which triggered the function call
        :return: No value returned
        :raise DataSpecificationSyntaxError:\
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:\
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("WRITE_PARAM")

    def execute_write_param_component(self, cmd):  # pragma: no cover
        """ This command is never generated!

        :param int cmd: the command which triggered the function call
        :return: No value returned
        :raise DataSpecificationSyntaxError:\
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:\
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("WRITE_PARAM_COMPONENT")

    def execute_print_val(self, cmd):  # pragma: no cover
        """ This command prints a value to the log.

        :param int cmd: the command which triggered the function call
        :return: No value returned
        :raise DataSpecificationSyntaxError:\
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:\
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("PRINT_VAL")

    def execute_print_txt(self, cmd):  # pragma: no cover
        """ This command prints a short string to the log.

        :param int cmd: the command which triggered the function call
        :return: No value returned
        :raise DataSpecificationSyntaxError:\
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:\
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("PRINT_TXT")

    def execute_print_struct(self, cmd):  # pragma: no cover
        """ This command prints a structure to the log.

        :param int cmd: the command which triggered the function call
        :return: No value returned
        :raise DataSpecificationSyntaxError:\
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:\
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("PRINT_STRUCT")

    def execute_read_param(self, cmd):  # pragma: no cover
        """ This command extracts an element from a structure.

        :param int cmd: the command which triggered the function call
        :return: No value returned
        :raise DataSpecificationSyntaxError:\
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:\
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("READ_PARAM")

    def execute_end_spec(self, cmd):  # pragma: no cover
        """ This command marks the end of the specification program.

        :param int cmd: the command which triggered the function call
        :return: A special marker to signal the end.
        :raise DataSpecificationSyntaxError:\
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:\
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("END_SPEC")
