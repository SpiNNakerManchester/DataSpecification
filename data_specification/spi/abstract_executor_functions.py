# Copyright (c) 2017 The University of Manchester
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from spinn_utilities.abstract_base import AbstractBase
from data_specification.exceptions import UnimplementedDSECommandError


class AbstractExecutorFunctions(object, metaclass=AbstractBase):
    """
    This class defines a function related to each of the commands of the
    data specification file. Subclasses need to provide implementations
    that work for the operations they wish to support.
    """
    # pylint: disable=unused-argument

    __slots__ = []

    def execute_break(self, cmd):  # pragma: no cover
        """
        This command raises an exception to stop the execution of the
        data spec executor (DSE).

        Implements :py:obj:`~.BREAK`

        :param int cmd: the command which triggered the function call
        :raise DataSpecificationSyntaxError:
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("BREAK")

    def execute_nop(self, cmd):
        """
        This command executes no operation.

        Implements :py:obj:`~.NOP`

        :param int cmd: the command which triggered the function call
        :raise DataSpecificationSyntaxError:
            If there is an error in the command syntax
        """

    def execute_reserve(self, cmd):  # pragma: no cover
        """
        This command reserves a region and assigns some memory space to it.

        Implements :py:obj:`~.RESERVE`

        :param int cmd: the command which triggered the function call
        :raise DataSpecificationSyntaxError:
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("RESERVE")

    def execute_reference(self, cmd):  # pragma: no cover
        """
        This command reserves a region and sets it to reference another.

        Implements :py:obj:`~.REFERENCE`

        :param int cmd: the command which triggered the function call
        :raise DataSpecificationSyntaxError:
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("REFERENCE")

    def execute_free(self, cmd):  # pragma: no cover
        """
        This command frees some memory.

        Implements :py:obj:`~data_specification.enums.commands.FREE`

        :param int cmd: the command which triggered the function call
        :raise DataSpecificationSyntaxError:
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("FREE")

    def execute_declare_rng(self, cmd):  # pragma: no cover
        """
        This command declares a random number generator.

        Implements :py:obj:`~.DECLARE_RNG`

        :param int cmd: the command which triggered the function call
        :raise DataSpecificationSyntaxError:
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("DECLARE_RNG")

    def execute_random_dist(self, cmd):  # pragma: no cover
        """
        This command defines a random distribution.

        Implements :py:obj:`~.DECLARE_RANDOM_DIST`

        :param int cmd: the command which triggered the function call
        :raise DataSpecificationSyntaxError:
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("DECLARE_RANDOM_DIST")

    def execute_get_random_rumber(self, cmd):  # pragma: no cover
        """
        This command obtains a random number from a distribution.

        Implements :py:obj:`~.GET_RANDOM_NUMBER`

        :param int cmd: the command which triggered the function call
        :raise DataSpecificationSyntaxError:
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("GET_RANDOM_NUMBER")

    def execute_start_struct(self, cmd):  # pragma: no cover
        """
        This command starts to define a structure.

        Implements :py:obj:`~.START_STRUCT`

        :param int cmd: the command which triggered the function call
        :raise DataSpecificationSyntaxError:
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("START_STRUCT")

    def execute_struct_elem(self, cmd):  # pragma: no cover
        """
        This command adds an element to a structure.

        Implements :py:obj:`~.STRUCT_ELEM`

        :param int cmd: the command which triggered the function call
        :raise DataSpecificationSyntaxError:
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("STRUCT_ELEM")

    def execute_end_struct(self, cmd):  # pragma: no cover
        """
        This command completes the definition of a structure.

        Implements :py:obj:`~.END_STRUCT`

        :param int cmd: the command which triggered the function call
        :raise DataSpecificationSyntaxError:
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("END_STRUCT")

    def execute_start_constructor(self, cmd):  # pragma: no cover
        """
        This command starts the definition of a function.

        Implements :py:obj:`~.START_CONSTRUCTOR`

        :param int cmd: the command which triggered the function call
        :raise DataSpecificationSyntaxError:
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("START_CONSTRUCTOR")

    def execute_end_constructor(self, cmd):  # pragma: no cover
        """
        This command ends the definition of a function.

        Implements :py:obj:`~.END_CONSTRUCTOR`

        :param int cmd: the command which triggered the function call
        :raise DataSpecificationSyntaxError:
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("END_CONSTRUCTOR")

    def execute_construct(self, cmd):  # pragma: no cover
        """
        This command calls a function.

        Implements :py:obj:`~.CONSTRUCT`

        :param int cmd: the command which triggered the function call
        :raise DataSpecificationSyntaxError:
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("CONSTRUCT")

    def execute_read(self, cmd):  # pragma: no cover
        """
        This command reads a word from memory.

        Implements :py:obj:`~.READ`

        :param int cmd: the command which triggered the function call
        :raise DataSpecificationSyntaxError:
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("READ")

    def execute_write(self, cmd):  # pragma: no cover
        """
        This command writes the given value in the specified region a
        number of times as identified by either a value in the command
        or a register value.

        Implements :py:obj:`~.WRITE`

        :param int cmd: the command which triggered the function call
        :raise DataSpecificationSyntaxError:
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("WRITE")

    def execute_write_array(self, cmd):  # pragma: no cover
        """
        This command writes an array of values in the specified region.

        Implements :py:obj:`~.WRITE_ARRAY`

        :param int cmd: the command which triggered the function call
        :raise DataSpecificationSyntaxError:
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("WRITE_ARRAY")

    def execute_write_struct(self, cmd):  # pragma: no cover
        """
        This command writes a structure to memory.

        Implements :py:obj:`~.WRITE_STRUCT`

        :param int cmd: the command which triggered the function call
        :raise DataSpecificationSyntaxError:
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("WRITE_STRUCT")

    def execute_block_copy(self, cmd):  # pragma: no cover
        """
        This command copies a block of memory from one location to another.

        Implements :py:obj:`~.BLOCK_COPY`

        :param int cmd: the command which triggered the function call
        :raise DataSpecificationSyntaxError:
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("BLOCK_COPY")

    def execute_switch_focus(self, cmd):  # pragma: no cover
        """
        This command switches the focus to the desired, already allocated,
        memory region.

        Implements :py:obj:`~.SWITCH_FOCUS`

        :param int cmd: the command which triggered the function call
        :raise DataSpecificationSyntaxError:
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("SWITCH_FOCUS")

    def execute_loop(self, cmd):  # pragma: no cover
        """
        This command starts a loop.

        Implements :py:obj:`~.LOOP`

        :param int cmd: the command which triggered the function call
        :raise DataSpecificationSyntaxError:
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("LOOP")

    def execute_break_loop(self, cmd):  # pragma: no cover
        """
        This command stops a loop early.

        Implements :py:obj:`~.BREAK_LOOP`

        :param int cmd: the command which triggered the function call
        :raise DataSpecificationSyntaxError:
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("BREAK_LOOP")

    def execute_end_loop(self, cmd):  # pragma: no cover
        """
        This command finishes a loop.

        Implements :py:obj:`~.END_LOOP`

        :param int cmd: the command which triggered the function call
        :raise DataSpecificationSyntaxError:
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("END_LOOP")

    def execute_if(self, cmd):  # pragma: no cover
        """
        This command does a conditional branch.

        Implements :py:obj:`~.IF`

        :param int cmd: the command which triggered the function call
        :raise DataSpecificationSyntaxError:
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("IF")

    def execute_else(self, cmd):  # pragma: no cover
        """
        This command handles the other branch of a conditional.

        Implements :py:obj:`~.ELSE`

        :param int cmd: the command which triggered the function call
        :raise DataSpecificationSyntaxError:
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("ELSE")

    def execute_end_if(self, cmd):  # pragma: no cover
        """
        This command ends a conditional.

        Implements :py:obj:`~.END_IF`

        :param int cmd: the command which triggered the function call
        :raise DataSpecificationSyntaxError:
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("ENDIF")

    def execute_mv(self, cmd):  # pragma: no cover
        """
        This command moves an immediate value to a register or copies the
        value of a register to another register.

        Implements :py:obj:`~.MV`

        :param int cmd: the command which triggered the function call
        :raise DataSpecificationSyntaxError:
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("MV")

    def execute_get_wr_ptr(self, cmd):  # pragma: no cover
        """
        This command gets the current write pointer.

        Implements :py:obj:`~.GET_WR_PTR`

        :param int cmd: the command which triggered the function call
        :raise DataSpecificationSyntaxError:
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("GET_WR_PTR")

    def execute_set_wr_ptr(self, cmd):  # pragma: no cover
        """
        This command sets the current write pointer.

        Implements :py:obj:`~.SET_WR_PTR`

        :param int cmd: the command which triggered the function call
        :raise DataSpecificationSyntaxError:
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("SET_WR_PTR")

    def execute_reset_wr_ptr(self, cmd):  # pragma: no cover
        """
        This command resets the current write pointer to the beginning
        of the memory region.

        :param int cmd: the command which triggered the function call
        :raise DataSpecificationSyntaxError:
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("RESET_RW_PTR")

    def execute_align_wr_ptr(self, cmd):  # pragma: no cover
        """
        This command moves the write pointer to be at the start of the
        next word if it isn't already at the start of a word.

        Implements :py:obj:`~.ALIGN_WR_PTR`

        :param int cmd: the command which triggered the function call
        :raise DataSpecificationSyntaxError:
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("ALIGN_WR_PTR")

    def execute_arith_op(self, cmd):  # pragma: no cover
        """
        This command performs an arithmetic operation.

        Implements :py:obj:`~.ARITH_OP`

        :param int cmd: the command which triggered the function call
        :raise DataSpecificationSyntaxError:
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("ARITH_OP")

    def execute_logic_op(self, cmd):  # pragma: no cover
        """
        This command performs a logical operation.

        Implements :py:obj:`~.LOGIC_OP`

        :param int cmd: the command which triggered the function call
        :raise DataSpecificationSyntaxError:
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("LOGIC_OP")

    def execute_reformat(self, cmd):  # pragma: no cover
        """
        This command is never generated!

        Implements :py:obj:`~.REFORMAT`

        :param int cmd: the command which triggered the function call
        :raise DataSpecificationSyntaxError:
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("REFORMAT")

    def execute_copy_struct(self, cmd):  # pragma: no cover
        """
        This command copies a structure from one slot to another.

        Implements :py:obj:`~.COPY_STRUCT`

        :param int cmd: the command which triggered the function call
        :raise DataSpecificationSyntaxError:
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("COPY_STRUCT")

    def execute_copy_param(self, cmd):  # pragma: no cover
        """
        This command copies a field of a structure to another field of
        a possibly-different structure.

        Implements :py:obj:`~.COPY_PARAM`

        :param int cmd: the command which triggered the function call
        :raise DataSpecificationSyntaxError:
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("COPY_PARAM")

    def execute_write_param(self, cmd):  # pragma: no cover
        """
        This command handles a single element of a structure.

        Implements :py:obj:`~.WRITE_PARAM`

        :param int cmd: the command which triggered the function call
        :raise DataSpecificationSyntaxError:
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("WRITE_PARAM")

    def execute_write_param_component(self, cmd):  # pragma: no cover
        """
        This command is never generated!

        Implements :py:obj:`~.WRITE_PARAM_COMPONENT`

        :param int cmd: the command which triggered the function call
        :raise DataSpecificationSyntaxError:
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("WRITE_PARAM_COMPONENT")

    def execute_print_val(self, cmd):  # pragma: no cover
        """
        This command prints a value to the log.

        Implements :py:obj:`~.PRINT_VAL`

        :param int cmd: the command which triggered the function call
        :raise DataSpecificationSyntaxError:
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("PRINT_VAL")

    def execute_print_txt(self, cmd):  # pragma: no cover
        """
        This command prints a short string to the log.

        Implements :py:obj:`~.PRINT_TXT`

        :param int cmd: the command which triggered the function call
        :raise DataSpecificationSyntaxError:
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("PRINT_TXT")

    def execute_print_struct(self, cmd):  # pragma: no cover
        """
        This command prints a structure to the log.

        Implements :py:obj:`~.PRINT_STRUCT`

        :param int cmd: the command which triggered the function call
        :raise DataSpecificationSyntaxError:
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("PRINT_STRUCT")

    def execute_read_param(self, cmd):  # pragma: no cover
        """
        This command extracts an element from a structure.

        Implements :py:obj:`~.READ_PARAM`

        :param int cmd: the command which triggered the function call
        :raise DataSpecificationSyntaxError:
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("READ_PARAM")

    def execute_end_spec(self, cmd):  # pragma: no cover
        """
        This command marks the end of the specification program.

        Implements :py:obj:`~.END_SPEC`

        :param int cmd: the command which triggered the function call
        :return: A special marker to signal the end.
        :raise DataSpecificationSyntaxError:
            If there is an error in the command syntax
        :raise UnimplementedDSECommandError:
            If the command is not implemented.
        """
        raise UnimplementedDSECommandError("END_SPEC")
