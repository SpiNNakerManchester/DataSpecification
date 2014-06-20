from abc import ABCMeta, abstractmethod


class AbstractDataWriter(object):
    """ Abstract writer used to write data somewhere
    """
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def write_bytes(self, data):
        """ Write some bytes of data to the underlying storage.\
            Does not return until all the bytes have been written.
        
        :param data: The data to write
        :type data: iterable of bytes
        :return: Nothing is returned
        :rtype: None
        :raise data_allocation.exceptions.DataWriteException:\
            If an error occurs writing to the underlying storage
        """
        pass
    
    @abstractmethod
    def close(self):
        """ Closes the writer, flushing any outstanding data to the underlying\
            storage.  Does not return until all data has been written.
        
        :return: Nothing is returned
        :rtype: None
        :raise data_allocation.exceptions.DataWriteException:\
            If an error occurs writing to the underlying storage
        """
