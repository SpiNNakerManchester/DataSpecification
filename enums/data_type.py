from enum import Enum


class DataType(Enum):
    """ Supported data types
    """
    UINT8 = (0, "8-bit unsigned integer")
    UINT16 = (1, "16-bit unsigned integer")
    UINT32 = (2, "32-bit unsigned integer")
    UINT64 = (3, "64-bit unsigned integer")
    INT8 = (4, "8-bit signed integer")
    INT16 = (5, "16-bit signed integer")
    INT32 = (6, "32-bit signed integer")
    INT64 = (7, "64-bit signed integer")
    U88 = (8, "8.8 unsigned fixed point number")
    U1616 = (9, "16.16 unsigned fixed point number")
    U3232 = (10, "32.32 unsigned fixed point number")
    S87 = (11, "8.7 signed fixed point number")
    S1615 = (12, "16.15 signed fixed point number")
    S3231 = (13, "32.31 signed fixed point number")
    U08 = (16, "0.8 unsigned fixed point number")
    U016 = (17, "0.16 unsigned fixed point number")
    U032 = (18, "0.32 unsigned fixed point number")
    U064 = (19, "0.64 unsigned fixed point number")
    S07 = (20, "0.7 signed fixed point number")
    S015 = (21, "0.15 signed fixed point number")
    S031 = (22, "0.32 signed fixed point number")
    S063 = (23, "0.63 signed fixed point number")

    def __new__(cls, value, doc=""):
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, value, doc=""):
        self._value_ = value
        self.__doc__ = doc
