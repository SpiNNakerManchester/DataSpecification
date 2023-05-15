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
