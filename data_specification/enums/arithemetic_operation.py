# Copyright (c) 2014-2023 The University of Manchester
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from enum import Enum


class ArithmeticOperation(Enum):
    """ Arithmetic Operations
    """

    #: Addition operation
    ADD = (0, "+", "Perform addition")
    #: Subtraction operation
    SUBTRACT = (1, "-", "Perform subtraction")
    #: Multiplication operation
    MULTIPLY = (2, "*", "Perform multiplication")

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
