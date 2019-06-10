class MemoryRegion(object):
    """ Memory region storage object
    """

    __slots__ = [

        # flag that states if the region is filled or not
        "_unfilled",

        # the amount of memory allocated to this DSG
        "_allocated_size",

        # the region address map????
        "_region_data",

        # the position in the memory where the writing is currently occurring
        "_write_pointer",

        # the max point where if written over, it will cause an error
        "_max_write_pointer"
    ]

    def __init__(self, unfilled, size):
        """
        :param unfilled: if the region needs to be filled when written
        :rtype: None
        :raise None: this method does not raise any known exception
        """
        self._unfilled = unfilled
        self._allocated_size = size
        self._region_data = bytearray(size)
        self._write_pointer = 0
        self._max_write_pointer = 0

    @property
    def allocated_size(self):
        """ The size of the region

        :return: the size of the region
        :rtype: int
        :raise None: this method does not raise any known exception
        """
        return self._allocated_size

    @property
    def remaining_space(self):
        """ The space between the current write pointer and the end of the/
            region

        :return: the number of bytes in the region that can be written
        :rtype: int
        :raise None: this method does not raise any known exception
        """
        return self._allocated_size - self._write_pointer

    @property
    def unfilled(self):
        """ Whether the region is marked as not fillable

        :return: True if the region will not contain any data at write time
        :rtype: bool
        :raise None: this method does not raise any known exception
        """
        return self._unfilled

    @property
    def region_data(self):
        """ The container which holds the data written in this region

        :return: the region data container
        :rtype: bytearray
        :raise None: this method does not raise any known exception
        """
        return self._region_data

    @property
    def write_pointer(self):
        return self._write_pointer

    @write_pointer.setter
    def write_pointer(self, write_pointer):
        self._write_pointer = write_pointer
        self._max_write_pointer = max((
            self._write_pointer, self._max_write_pointer))

    @property
    def max_write_pointer(self):
        return self._max_write_pointer

    def increment_write_pointer(self, n_bytes):
        self._write_pointer += n_bytes
        self._max_write_pointer = max((
            self._write_pointer, self._max_write_pointer))
