from enum import Enum
import decimal
import struct
import numpy as np


class DataType(Enum):
    """ Supported data types
        The first value is an identifier for the enum class;
        The second value is the size in bytes of the type;
        The third value is the minimum possible value for the type;
        The fourth value is the maximum possible value for the type;
        The fifth value is the scale of the input value to convert it in\
            integer;
        The sixth value is the pattern to use following the struct package\
            encodings to convert the data in binary format;
        The seventh value is whether to apply the scaling when converting to\
            SpiNNaker's binary format.
        The eighth value is the corresponding numpy type (or None to inhibit\
            direct conversion via numpy, scaled conversion still supported);
        The ninth value is the text description of the type.
    """
    # pylint: disable=no-member
    UINT8 = (0,
             1,
             decimal.Decimal("0"),
             decimal.Decimal("255"),
             decimal.Decimal("1"),
             "B",
             False,
             np.uint8,
             "8-bit unsigned integer")
    UINT16 = (1,
              2,
              decimal.Decimal("0"),
              decimal.Decimal("65535"),
              decimal.Decimal("1"),
              "H",
              False,
              np.uint16,
              "16-bit unsigned integer")
    UINT32 = (2,
              4,
              decimal.Decimal("0"),
              decimal.Decimal("4294967295"),
              decimal.Decimal("1"),
              "I",
              False,
              np.uint32,
              "32-bit unsigned integer")
    UINT64 = (3,
              8,
              decimal.Decimal("0"),
              decimal.Decimal("18446744073709551615"),
              decimal.Decimal("1"),
              "Q",
              False,
              np.uint64,
              "64-bit unsigned integer")
    INT8 = (4,
            1,
            decimal.Decimal("-128"),
            decimal.Decimal("127"),
            decimal.Decimal("1"),
            "b",
            False,
            np.int8,
            "8-bit signed integer")
    INT16 = (5,
             2,
             decimal.Decimal("-32768"),
             decimal.Decimal("32767"),
             decimal.Decimal("1"),
             "h",
             False,
             np.int16,
             "16-bit signed integer")
    INT32 = (6,
             4,
             decimal.Decimal("-2147483648"),
             decimal.Decimal("2147483647"),
             decimal.Decimal("1"),
             "i",
             False,
             np.int32,
             "32-bit signed integer")
    INT64 = (7,
             8,
             decimal.Decimal("-9223372036854775808"),
             decimal.Decimal("9223372036854775807"),
             decimal.Decimal("1"),
             "q",
             False,
             np.int64,
             "64-bit signed integer")
    U88 = (8,
           2,
           decimal.Decimal("0"),
           decimal.Decimal("255.99609375"),
           decimal.Decimal("256"),
           "H",
           True,
           None,
           "8.8 unsigned fixed point number")
    U1616 = (9,
             4,
             decimal.Decimal("0"),
             decimal.Decimal("65535.9999847"),
             decimal.Decimal("65536"),
             "I",
             True,
             None,
             "16.16 unsigned fixed point number")
    U3232 = (10,
             8,
             decimal.Decimal("0"),
             decimal.Decimal("4294967295.99999999976716935634613037109375"),
             decimal.Decimal("4294967296"),
             "Q",
             True,
             None,
             "32.32 unsigned fixed point number")  # rounding problem for max
    S87 = (11,
           2,
           decimal.Decimal("-256"),
           decimal.Decimal("255.9921875"),
           decimal.Decimal("128"),
           "h",
           True,
           None,
           "8.7 signed fixed point number")
    S1615 = (12,
             4,
             decimal.Decimal("-65536"),
             decimal.Decimal("65535.999969482421875"),
             decimal.Decimal("32768"),
             "i",
             True,
             None,
             "16.15 signed fixed point number")
    S3231 = (13,
             8,
             decimal.Decimal("-4294967296"),
             decimal.Decimal("4294967295.9999999995343387126922607421875"),
             decimal.Decimal("2147483648"),
             "q",
             True,
             None,
             "32.31 signed fixed point number")  # rounding problem for max
    FLOAT_32 = (14,
                4,
                decimal.Decimal("-3.4028234e38"),
                decimal.Decimal("3.4028234e38"),
                decimal.Decimal("1"),
                "f",
                False,
                np.float32,
                "32-bit floating point number")
    FLOAT_64 = (15,
                8,
                decimal.Decimal("-1.7976931348623157e+308"),
                decimal.Decimal("1.7976931348623157e+308"),
                decimal.Decimal("1"),
                "d",
                False,
                np.float64,
                "64-bit floating point number")
    U08 = (16,
           1,
           decimal.Decimal("0"),
           decimal.Decimal("0.99609375"),
           decimal.Decimal("256"),
           "B",
           True,
           None,
           "0.8 unsigned fixed point number")
    U016 = (17,
            2,
            decimal.Decimal("0"),
            decimal.Decimal("0.999984741211"),
            decimal.Decimal("65536"),
            "H",
            True,
            None,
            "0.16 unsigned fixed point number")
    U032 = (18,
            4,
            decimal.Decimal("0"),
            decimal.Decimal("0.99999999976716935634613037109375"),
            decimal.Decimal("4294967296"),
            "I",
            True,
            None,
            "0.32 unsigned fixed point number")
    U064 = (19,
            8,
            decimal.Decimal("0"),
            decimal.Decimal(
                "0.9999999999999999999457898913757247782996273599565029"),
            decimal.Decimal("18446744073709551616"),
            "Q",
            True,
            None,
            "0.64 unsigned fixed point number")  # rounding problem for max
    S07 = (20,
           1,
           decimal.Decimal("-1"),
           decimal.Decimal("0.9921875"),
           decimal.Decimal("128"),
           "b",
           True,
           None,
           "0.7 signed fixed point number")
    S015 = (21,
            2,
            decimal.Decimal("-1"),
            decimal.Decimal("0.999969482421875"),
            decimal.Decimal("32768"),
            "h",
            True,
            None,
            "0.15 signed fixed point number")
    S031 = (22,
            4,
            decimal.Decimal("-1"),
            decimal.Decimal("0.99999999976716935634613037109375"),
            decimal.Decimal("2147483648"),
            "i",
            True,
            None,
            "0.32 signed fixed point number")
    S063 = (23,
            8,
            decimal.Decimal("-1"),
            decimal.Decimal(
                "0.9999999999999999998915797827514495565992547199130058"),
            decimal.Decimal("9223372036854775808"),
            "q",
            True,
            None,
            "0.63 signed fixed point number")  # rounding problem for max

    def __new__(cls, value, size, min_val, max_val, scale, struct_encoding,
                apply_scale, numpy_typename, doc=""):
        # pylint: disable=protected-access, too-many-arguments
        obj = object.__new__(cls)
        obj._value_ = value
        obj.__doc__ = doc
        obj.size = size
        obj.min = min_val
        obj.max = max_val
        obj.scale = scale
        obj.struct_encoding = struct_encoding
        obj.numpy_typename = numpy_typename
        obj._apply_scale = apply_scale
        if size == 1:
            struct_encoding += "xxx"
        elif size == 2:
            struct_encoding += "xx"
        obj._struct = struct.Struct("<" + struct_encoding)
        return obj

    def __init__(self, value, size, min_val, max_val, scale, struct_encoding,
                 apply_scale, numpy_typename, doc=""):
        # pylint: disable=too-many-arguments
        self._value_ = value
        self.__doc__ = doc
        self.size = size
        self.min = min_val
        self.max = max_val
        self.scale = scale
        self.struct_encoding = struct_encoding
        self.numpy_typename = numpy_typename
        self._apply_scale = apply_scale
        if size == 1:
            struct_encoding += "xxx"
        elif size == 2:
            struct_encoding += "xx"
        self._struct = struct.Struct("<" + struct_encoding)

    def encode(self, value):
        """ Encode the Python value for SpiNNaker according to this type.
        """
        if self._apply_scale:
            value = int(decimal.Decimal(str(value)) * self.scale)
        return self._struct.pack(value)
