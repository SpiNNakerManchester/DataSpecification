from abc import ABCMeta
from abc import abstractmethod
from six import add_metaclass

@add_metaclass(ABCMeta)
class AbstractDataWriter(object):
    """ Abstract writer used to write data somewhere
    """
    
    @abstractmethod
    def write_bytes(self, data):
        """ Write some bytes of data to the underlying storage.\
            Does not return until all the bytes have been written.
        
        :param data: The data to write
        :type data: bytearray
        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataWriteException:\
            If an error occurs writing to the underlying storage
        """
        pass
    
    @abstractmethod
    def close(self):
        """ Closes the writer, flushing any outstanding data to the underlying\
            storage.  Does not return until all data has been written.
        
        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataWriteException:\
            If an error occurs writing to the underlying storage
        """
        pass
