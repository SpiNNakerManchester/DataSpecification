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

import decimal
import struct
from enum import Enum
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
        The ninth value is the numpy convert param needed for decoding from\
            bytes.
        The tenth value is the number of bytes this data type takes up for\
            decoding into numpy. 
        The eleventh value is the text description of the type.
    """
    # pylint: disable=no-member
    UINT8 = (0,
             1,
             decimal.Decimal("0"),
             decimal.Decimal("255"),
             decimal.Decimal("1"),
             "B",
             False,
             int,
             np.uint8,
             'u',
             1,
             "8-bit unsigned integer")
    UINT16 = (1,
              2,
              decimal.Decimal("0"),
              decimal.Decimal("65535"),
              decimal.Decimal("1"),
              "H",
              False,
              int,
              np.uint16,
              'u',
              2,
              "16-bit unsigned integer")
    UINT32 = (2,
              4,
              decimal.Decimal("0"),
              decimal.Decimal("4294967295"),
              decimal.Decimal("1"),
              "I",
              False,
              int,
              np.uint32,
              'u',
              4,
              "32-bit unsigned integer")
    UINT64 = (3,
              8,
              decimal.Decimal("0"),
              decimal.Decimal("18446744073709551615"),
              decimal.Decimal("1"),
              "Q",
              False,
              int,
              np.uint64,
              'u',
              8,
              "64-bit unsigned integer")
    INT8 = (4,
            1,
            decimal.Decimal("-128"),
            decimal.Decimal("127"),
            decimal.Decimal("1"),
            "b",
            False,
            int,
            np.int8,
            'i',
            1,
            "8-bit signed integer")
    INT16 = (5,
             2,
             decimal.Decimal("-32768"),
             decimal.Decimal("32767"),
             decimal.Decimal("1"),
             "h",
             False,
             int,
             np.int16,
             'i',
             2,
             "16-bit signed integer")
    INT32 = (6,
             4,
             decimal.Decimal("-2147483648"),
             decimal.Decimal("2147483647"),
             decimal.Decimal("1"),
             "i",
             False,
             int,
             np.int32,
             'i',
             4,
             "32-bit signed integer")
    INT64 = (7,
             8,
             decimal.Decimal("-9223372036854775808"),
             decimal.Decimal("9223372036854775807"),
             decimal.Decimal("1"),
             "q",
             False,
             int,
             np.int64,
             "i",
             8,
             "64-bit signed integer")
    U88 = (8,
           2,
           decimal.Decimal("0"),
           decimal.Decimal("255.99609375"),
           decimal.Decimal("256"),
           "H",
           True,
           None,
           None,
           None,
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
             None,
             None,
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
             None,
             None,
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
           None,
           None,
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
             None,
             None,
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
             None,
             None,
             None,
             "32.31 signed fixed point number")  # rounding problem for max
    FLOAT_32 = (14,
                4,
                decimal.Decimal("-3.4028234e38"),
                decimal.Decimal("3.4028234e38"),
                decimal.Decimal("1"),
                "f",
                False,
                float,
                np.float32,
                "f",
                4,
                "32-bit floating point number")
    FLOAT_64 = (15,
                8,
                decimal.Decimal("-1.7976931348623157e+308"),
                decimal.Decimal("1.7976931348623157e+308"),
                decimal.Decimal("1"),
                "d",
                False,
                float,
                np.float64,
                "f",
                8,
                "64-bit floating point number")
    U08 = (16,
           1,
           decimal.Decimal("0"),
           decimal.Decimal("0.99609375"),
           decimal.Decimal("256"),
           "B",
           True,
           None,
           None,
           None,
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
            None,
            None,
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
            None,
            None,
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
            None,
            None,
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
           None,
           None,
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
            None,
            None,
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
            None,
            None,
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
            None,
            None,
            None,
            "0.63 signed fixed point number")  # rounding problem for max

    def __new__(cls, value, size, min_val, max_val, scale, struct_encoding,
                apply_scale, force_cast, numpy_typename, numpy_decoding,
                nump_decoding_size, doc=""):
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
        obj.numpy_decoding = numpy_decoding
        obj.numpy_decoding_size = nump_decoding_size
        obj._apply_scale = apply_scale
        obj._force_cast = force_cast
        if size == 1:
            struct_encoding += "xxx"
        elif size == 2:
            struct_encoding += "xx"
        obj._struct = struct.Struct("<" + struct_encoding)
        return obj

    def __init__(self, value, size, min_val, max_val, scale, struct_encoding,
                 apply_scale, force_cast, numpy_typename, numpy_decoding,
                 nump_decoding_size, doc=""):
        # pylint: disable=too-many-arguments
        self._value_ = value
        self.__doc__ = doc
        self.size = size
        self.min = min_val
        self.max = max_val
        self.scale = scale
        self.struct_encoding = struct_encoding
        self.numpy_typename = numpy_typename
        self.numpy_decoding = numpy_decoding
        self.numpy_decoding_size = nump_decoding_size
        self._apply_scale = apply_scale
        self._force_cast = force_cast
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
        elif self._force_cast is not None:
            value = self._force_cast(value)
        return self._struct.pack(value)

    def decode_array(self, values):
        """ Decodes the SpiNNaker byte array into iterable of this type.
        :param values: the bytes to decode into this given data type
        :rtype: numpy array
        """
        return np.asarray(values, dtype="uint8").view(dtype="<{}{}".format(
            self.numpy_decoding, self.numpy_decoding_size))
