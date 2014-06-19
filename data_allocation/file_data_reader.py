from data_allocation.abstract_data_reader import AbstractDataReader

class FileDataReader(AbstractDataReader):
    """ A reader that can read data from a file
    """
    
    def __init__(self, filename):
        """
        :param filename: The file to read
        :type filename: str
        :raise data_allocation.exceptions.DataReadException: If the file cannot
                    found or opened for reading
        """
        pass
    
    def read_bytes(self, n_bytes):
        # TODO
        return None
    
    def read_bytes_into(self, data, offset=0, length=None):
        # TODO
        return 0
