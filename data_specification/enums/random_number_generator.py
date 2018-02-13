from enum import Enum


class RandomNumberGenerator(Enum):
    """ Random number generator types
    """

    MERSENNE_TWISTER = (0, "The well-known Mersenne Twister PRNG")

    def __new__(cls, value, doc=""):
        # pylint: disable=protected-access
        obj = object.__new__(cls)
        obj._value_ = value
        obj.__doc__ = doc
        return obj

    def __init__(self, value, doc=""):
        self._value_ = value
        self.__doc__ = doc
