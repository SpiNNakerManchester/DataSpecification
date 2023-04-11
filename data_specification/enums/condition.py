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


class Condition(Enum):
    """
    Comparison Operations.
    """

    #: Compare the operands for equality
    EQUAL = (
        0, "==",
        "Compare the operands for equality")
    #: Compare the operands for inequality
    NOT_EQUAL = (
        1, "!=",
        "Compare the operands for inequality")
    #: True if the first operand is <= the second
    LESS_THAN_OR_EQUAL = (
        2, "<=",
        "True if the first operand is <= the second")
    #: True if the first operand is <  the second
    LESS_THAN = (
        3, "<",
        "True if the first operand is <  the second")
    #: True if the first operand is >= the second
    GREATER_THAN_OR_EQUAL = (
        4, ">=",
        "True if the first operand is >= the second")
    #: True if the first operand is >  the second
    GREATER_THAN = (
        5, ">",
        "True if the first operand is >  the second")

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
