from abc import ABCMeta, abstractmethod


class AbstractDataReader(object):
    """ Abstract reader used to read data from somewhere
    """
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def read_bytes(self, n_bytes):
        """ Read some bytes of data from the underlying storage.  Will block\
            until some bytes are available, but might not return the full\
            n_bytes.  The size of the returned array indicates how many\
            bytes were read.
        
        :param n_bytes: The number of bytes to read
        :type n_bytes: int
        :return: An array of bytes
        :rtype: array of bytes
        :raise data_allocation.exceptions.DataReadException:\
            If an error occurs reading from the underlying storage
        """
        pass
    
    @abstractmethod
    def read_bytes_into(self, data, offset=0, length=None):
        """ Read some bytes of data from the underlying storage into a\
            pre-defined array.  Will block until some bytes are available,\
            but may not fill the array completely.
        
        :param data: The place where the data is to be stored
        :type data: array of bytes
        :return: The number of bytes stored in data
        :rtype: int
        :raise data_allocation.exceptions.DataReadException:\
            If an error occurs reading from the underlying storage
        """
        pass
    
    @abstractmethod
    def close(self):
        """ Closes the reader
        
        :return: Nothing is returned
        :rtype: None
        :raise data_allocation.exceptions.DataReadException:\
            If an error occurs closing the underlying storage
        """
