from data_specification.abstract_data_writer import AbstractDataWriter

class FileDataWriter(AbstractDataWriter):
    
    def __init__(self, filename):
        """
        :param filename: The file to write to
        :type filename: str
        :raise data_specification.exceptions.DataWriteException: If the file\
                    cannot found or opened for writing
        """
    
    def write(self, data):
        """ See :py:meth:`data_specification.abstract_data_writer.AbstractDataWriter.write`
        """
        # TODO
        pass
    
    def close(self):
        """ Closes the file
        
        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataWriteException: If the file\
                    cannot be closed
        """
        # TODO
        pass
