from enum import Enum


class LogicOperation(Enum):
    """ Logic Operations
    """
    LEFT_SHIFT = (0, "Shift left")
    RIGHT_SHIFT = (1, "Shift right")
    OR = (2, "Logical OR")
    AND = (3, "Logical AND")
    XOR = (4, "Logical XOR")
    NOT = (5, "Logical NOT")

    def __new__(cls, value, doc=""):
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, value, doc=""):
        self._value_ = value
        self.__doc__ = doc
