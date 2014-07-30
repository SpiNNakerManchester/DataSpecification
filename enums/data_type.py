from enum import Enum


class DataType(Enum):
    """ Supported data types
        The first value is an identifier for the enum class;
        The second value is the size in bytes of the type;
        The third value is the text description of the type.
    """
    UINT8 = (0, 1, 0, 255, "8-bit unsigned integer")
    UINT16 = (1, 2, 0, 65535, "16-bit unsigned integer")
    UINT32 = (2, 4, 0, 4294967295, "32-bit unsigned integer")
    UINT64 = (3, 8, 0, 18446744073709551615, "64-bit unsigned integer")
    INT8 = (4, 1, -128, 127, "8-bit signed integer")
    INT16 = (5, 2, -32768, 32767, "16-bit signed integer")
    INT32 = (6, 4, -2147483648, 2147483647, "32-bit signed integer")
    INT64 = (7, 8, -9223372036854775808, 9223372036854775807, "64-bit signed integer")
    U88 = (8, 2, 0, 255.99609375, "8.8 unsigned fixed point number")
    U1616 = (9, 4, 0, 65535.9999847, "16.16 unsigned fixed point number")
    U3232 = (10, 8, 0, 4294967295.99999999976716935634613037109375, "32.32 unsigned fixed point number") #rounding problem for max
    S87 = (11, 2, -256, 255.9921875, "8.7 signed fixed point number")
    S1615 = (12, 4, -32768, 32767.9999847, "16.15 signed fixed point number")
    S3231 = (13, 8, -4294967296, 4294967295.9999999995343387126922607421875, "32.31 signed fixed point number") #rounding problem for max
    U08 = (16, 1, 0, 0.99609375, "0.8 unsigned fixed point number")
    U016 = (17, 2, 0, 0.999984741211, "0.16 unsigned fixed point number")
    U032 = (18, 4, 0, 0.99999999976716935634613037109375, "0.32 unsigned fixed point number")
    U064 = (19, 8, 0, 0.9999999999999999999457898913757247782996273599565029, "0.64 unsigned fixed point number") #rounding problem for max
    S07 = (20, 1, -1, 0.9921875, "0.7 signed fixed point number")
    S015 = (21, 2, -1, 0.999969482421875, "0.15 signed fixed point number")
    S031 = (22, 4, -1, 0.99999999976716935634613037109375, "0.32 signed fixed point number")
    S063 = (23, 8, -1, 0.9999999999999999998915797827514495565992547199130058, "0.63 signed fixed point number") #rounding problem for max

    def __new__(cls, value, size, min_val, max_val, doc=""):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.__doc__ = doc
        obj.size = size
        obj.min = min_val
        obj.max = max_val
        return obj

    def __init__(self, value, size, min_val, max_val, doc=""):
        self._value_ = value
        self.__doc__ = doc
        self.size = size
        self.min = min_val
        self.max = max_val
