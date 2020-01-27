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

from enum import Enum


class LogicOperation(Enum):
    """ Logic Operations
    """
    #: Shift left (with zero extension)
    LEFT_SHIFT = (0, "LSL", "Shift left")
    #: Shift right (with zero extension)
    RIGHT_SHIFT = (1, "LSR", "Shift right")
    #: Logical OR
    OR = (2, "OR", "Logical OR")
    #: Logical AND
    AND = (3, "AND", "Logical AND")
    #: Logical XOR
    XOR = (4, "XOR", "Logical XOR")
    #: Logical NOT (single argument)
    NOT = (5, "NOT", "Logical NOT")

    def __new__(cls, value, operator, doc=""):
        # pylint: disable=protected-access
        obj = object.__new__(cls)
        obj._value_ = value
        obj.operator = operator
        obj.__doc__ = doc
        return obj

    def __init__(self, value, operator, doc=""):
        self._value_ = value
        self.operator = operator
        self.__doc__ = doc
