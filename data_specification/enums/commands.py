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

    #: Reserves a block of memory ready for filling.
    RESERVE = (
        0x02, DataSpecificationExecutorFunctions.execute_reserve,
        "Reserves a block of memory ready for filling")
    REFERENCE = (
        0x04, DataSpecificationExecutorFunctions.execute_reference,
        "References a region completely from another core on the same chip")
    #: Performs a simple write or block write operation.
    WRITE = (
        0x42, DataSpecificationExecutorFunctions.execute_write,
        "Performs a simple write or block write operation")
    #: Performs a write from an array.
    WRITE_ARRAY = (
        0x43, DataSpecificationExecutorFunctions.execute_write_array,
        "Performs a write from an array")
    #: Swap between different reserved memory regions to work on several at
    #: the same time.
    SWITCH_FOCUS = (
        0x50, DataSpecificationExecutorFunctions.execute_switch_focus,
        "Swap between different reserved memory regions to work on several at"
        " the same time")
    #: Move the write pointer to a new location, either relative to the
    #: start of this reserved memory area or relative to the current
    #: write pointer.
    SET_WR_PTR = (
        0x64, DataSpecificationExecutorFunctions.execute_set_wr_ptr,
        "Move the write pointer to a new location, either relative to the"
        " start of this reserved memory area or relative to the current"
        " write pointer")
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
