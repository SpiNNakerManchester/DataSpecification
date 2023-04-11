# Copyright (c) 2014 The University of Manchester
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

from enum import Enum
from data_specification.data_specification_executor_functions import (
    DataSpecificationExecutorFunctions)


class Commands(Enum):
    """
    Set of opcodes for the spec executor.
    """

    #: Halts spec execution with an error.
    BREAK = (
        0x00, DataSpecificationExecutorFunctions.execute_break,
        "Halts spec execution with an error")
    #: No operation. Can be used as a filler.
    NOP = (
        0x01, DataSpecificationExecutorFunctions.execute_nop,
        "No operation. Can be used as a filler")
    #: Reserves a block of memory ready for filling.
    RESERVE = (
        0x02, DataSpecificationExecutorFunctions.execute_reserve,
        "Reserves a block of memory ready for filling")
    FREE = (
        0x03, DataSpecificationExecutorFunctions.execute_free,
        "Releases previously reserved memory")
    REFERENCE = (
        0x04, DataSpecificationExecutorFunctions.execute_reference,
        "References a region completely from another core on the same chip")
    DECLARE_RNG = (
        0x05, DataSpecificationExecutorFunctions.execute_declare_rng,
        "Declares a new random number generator")
    DECLARE_RANDOM_DIST = (
        0x06, DataSpecificationExecutorFunctions.execute_random_dist,
        "Declares a new random distribution")
    GET_RANDOM_NUMBER = (
        0x07, DataSpecificationExecutorFunctions.execute_get_random_rumber,
        "Returns a random number drawn from the given distribution")
    START_STRUCT = (
        0x10, DataSpecificationExecutorFunctions.execute_start_struct,
        "Begins declaration of new structure")
    STRUCT_ELEM = (
        0x11, DataSpecificationExecutorFunctions.execute_struct_elem,
        "Declare single element in a structure")
    END_STRUCT = (
        0x12, DataSpecificationExecutorFunctions.execute_end_struct,
        "Ends declaration of new structure")
    START_CONSTRUCTOR = (
        0x20, DataSpecificationExecutorFunctions.execute_start_constructor,
        "Begins definition of a function to write data structures to memory")
    END_CONSTRUCTOR = (
        0x25, DataSpecificationExecutorFunctions.execute_end_constructor,
        "Ends definition of the write function")
    CONSTRUCT = (
        0x40, DataSpecificationExecutorFunctions.execute_construct,
        "Invokes a constructor to build a data structure")
    READ = (
        0x41, DataSpecificationExecutorFunctions.execute_read,
        "Performs a simple read  operation")
    #: Performs a simple write or block write operation.
    WRITE = (
        0x42, DataSpecificationExecutorFunctions.execute_write,
        "Performs a simple write or block write operation")
    #: Performs a write from an array.
    WRITE_ARRAY = (
        0x43, DataSpecificationExecutorFunctions.execute_write_array,
        "Performs a write from an array")
    WRITE_STRUCT = (
        0x44, DataSpecificationExecutorFunctions.execute_write_struct,
        "Performs a write from a predefined structure")
    BLOCK_COPY = (
        0x45, DataSpecificationExecutorFunctions.execute_block_copy,
        "Copies a block of data from one area to another")
    #: Swap between different reserved memory regions to work on several at
    #: the same time.
    SWITCH_FOCUS = (
        0x50, DataSpecificationExecutorFunctions.execute_switch_focus,
        "Swap between different reserved memory regions to work on several at"
        " the same time")
    LOOP = (
        0x51, DataSpecificationExecutorFunctions.execute_loop,
        "Set-up a loop")
    BREAK_LOOP = (
        0x52, DataSpecificationExecutorFunctions.execute_break_loop,
        "Early exit from a loop")
    END_LOOP = (
        0x53, DataSpecificationExecutorFunctions.execute_end_loop,
        "End of a loop")
    IF = (
        0x55, DataSpecificationExecutorFunctions.execute_if,
        "Perform a condition and execute the following instructions only if"
        " the condition is true")
    ELSE = (
        0x56, DataSpecificationExecutorFunctions.execute_else,
        "Else clause for associated IF statement")
    END_IF = (
        0x57, DataSpecificationExecutorFunctions.execute_end_if,
        "Close block of instructions begun with the IF instruction")
    #: Place a value in a register, from an immediate or another register.
    MV = (
        0x60, DataSpecificationExecutorFunctions.execute_mv,
        "Place a value in a register, from an immediate or another register")
    GET_WR_PTR = (
        0x63, DataSpecificationExecutorFunctions.execute_get_wr_ptr,
        "Copy current write address to a register")
    #: Move the write pointer to a new location, either relative to the
    #: start of this reserved memory area or relative to the current
    #: write pointer.
    SET_WR_PTR = (
        0x64, DataSpecificationExecutorFunctions.execute_set_wr_ptr,
        "Move the write pointer to a new location, either relative to the"
        " start of this reserved memory area or relative to the current"
        " write pointer")
    ALIGN_WR_PTR = (
        0x65, DataSpecificationExecutorFunctions.execute_align_wr_ptr,
        "Moves the write pointer so that it points to the next block with a"
        " given address granularity")
    ARITH_OP = (
        0x67, DataSpecificationExecutorFunctions.execute_arith_op,
        "Perform arithmetic operation with operand 2 coming from a register")
    LOGIC_OP = (
        0x68, DataSpecificationExecutorFunctions.execute_logic_op,
        "Perform logical operation with operand 2 coming from a register")
    REFORMAT = (
        0x6A, DataSpecificationExecutorFunctions.execute_reformat,
        "Reformats a value in an internal register")
    COPY_STRUCT = (
        0x70, DataSpecificationExecutorFunctions.execute_copy_struct,
        "Create an identical copy of a structure")
    COPY_PARAM = (
        0x71, DataSpecificationExecutorFunctions.execute_copy_param,
        "Copy a parameter from one structure to another")
    WRITE_PARAM = (
        0x72, DataSpecificationExecutorFunctions.execute_write_param,
        "Modify a single parameter in a structure using an immediate value or"
        " register held-value")
    READ_PARAM = (
        0x73, DataSpecificationExecutorFunctions.execute_read_param,
        "Load the value of a structure parameter in a register")
    WRITE_PARAM_COMPONENT = (
        0x74, DataSpecificationExecutorFunctions.execute_write_param_component,
        "Modify a single parameter in a structure")
    PRINT_VAL = (
        0x80, DataSpecificationExecutorFunctions.execute_print_val,
        "Output the value of a register to the screen")
    PRINT_TXT = (
        0X81, DataSpecificationExecutorFunctions.execute_print_txt,
        "Print a text string to the screen")
    PRINT_STRUCT = (
        0X82, DataSpecificationExecutorFunctions.execute_print_struct,
        "Print the current state of one structure to the screen")
    END_SPEC = (
        0XFF, DataSpecificationExecutorFunctions.execute_end_spec,
        "Cleanly ends the parsing of the data specs")

    def __new__(cls, value, exec_function, doc=""):
        # pylint: disable=protected-access
        obj = object.__new__(cls)
        obj._value_ = value
        obj.exec_function = exec_function
        obj.__doc__ = doc
        return obj

    def __init__(self, value, exec_function, doc=""):
        self._value_ = value
        self.exec_function = exec_function
        self.__doc__ = doc
