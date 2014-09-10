
class MemoryRegion(object):
    """ memory region storage object

    """

    def __init__(self, memory_pointer, unfilled, size):
        """constrctor for the memory region

        :param memory_pointer: the write pointer position
        :param unfilled: if the region needs to be filled when written
        :return: None
        :rtype: None
        :raise None: this method does not raise any known exception
        """
        self._mem_pointer = memory_pointer
        self._unfilled = unfilled
        self._allocated_size = size
        self._region_data = bytearray(size)

    @property
    def memory_pointer(self):
        """ property method to retrieve memory write pointer

        :return: the memory pointer of the region
        :rtype: int
        :raise None: this method does not raise any known exception
        """
        return self._mem_pointer

    @property
    def allocated_size(self):
        """ property method for the size of the region

        :return: the size of the region
        :rtype: int
        :raise None: this method does not raise any knwon exception
        """
        return self._allocated_size

    @property
    def unfilled(self):
        """ property method to retrieve if the region is filled

        :return: the the
        :rtype: None
        :raise None: this method does not raise any known exception
        """
        return self._unfilled

    @property
    def region_data(self):
        """the container which holds the data written in this region

        :return: the region data container
        :rtype: bytearray
        :raise None: this method does not raise any known exception
        """
        return self._region_data



