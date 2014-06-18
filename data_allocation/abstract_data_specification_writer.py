from abc import ABCMeta, abstractmethod


class AbstractDataSpecificationWriter(object):
    """ Abstract writer used to write a specification somewhere
    """
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def write_bytes(self, data):
        """ Write some bytes of data to the underlying storage
        
        :param data: The data to write
        :type data: iterable of bytes
        :return: Nothing is returned
        :rtype: None
        :raise data_allocation.exceptions.DataSpecificationWriteException:\
            If an error occurs writing to the underlying storage
        """
        pass
    
    @abstractmethod
    def close(self):
        """ Closes the writer
        
        :return: Nothing is returned
        :rtype: None
        :raise data_allocation.exceptions.DataSpecificationWriteException:\
            If an error occurs writing to the underlying storage
        """
