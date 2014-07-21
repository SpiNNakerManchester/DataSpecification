from enum import Enum


class Condition(Enum):
    """ Comparison Operations
    """

    EQUAL = (0, "Compare the operands for equality")
    NOT_EQUAL = (1, "Compare the operands for inequality")
    LESS_THAN_OR_EQUAL = (2, "True if the first operand is <= the second")
    LESS_THAN = (3, "True if the first operand is <  the second")
    GREATER_THAN_OR_EQUAL = (4, "True if the first operand is >= the second")
    GREATER_THAN = (5, "True if the first operand is >  the second")

    def __new__(cls, value, doc=""):
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, value, doc=""):
        self._value_ = value
        self.__doc__ = doc
