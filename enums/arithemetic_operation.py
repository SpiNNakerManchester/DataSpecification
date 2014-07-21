from enum import Enum


class ArithmeticOperation(Enum):
    """ Arithmetic Operations
    """

    ADD = (0, "Perform addition")
    SUBTRACT = (1, "Perform subtraction")
    MULTIPLY = (2, "Perform multiplication")

    def __new__(cls, value, doc=""):
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, value, doc=""):
        self._value_ = value
        self.__doc__ = doc
