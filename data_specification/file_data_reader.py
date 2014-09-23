from data_specification.abstract_data_reader import AbstractDataReader
from data_specification.exceptions import DataReadException
from io import BlockingIOError

class FileDataReader(AbstractDataReader):
    """ A reader that can read data from a file
    """

    def __init__(self, filename):
        """
        :param filename: The file to read
        :type filename: str
        :raise data_specification.exceptions.DataReadException: If the file\
                    cannot found or opened for reading
        """
        self.filename = filename
        try:
            self.file_handle = open(filename, "rb")
        except:
            raise DataReadException(
                "Unable to open file {} for reading".format(filename))

    def read(self, n_bytes):
        """ See :py:meth:
        `data_specification.abstract_data_reader.AbstractDataReader.read`
        """
        try:
            data = self.file_handle.read(n_bytes)
        except BlockingIOError:
            raise IOError(
                "FileDataReader.read: unable to read {} bytes from file {}".format(
                    n_bytes, self.filename))
        byte_data = bytearray(data)
        return byte_data

    def readinto(self, data):
        """ See :py:meth:`data_specification.abstract_data_reader.AbstractDataReader.readinto`
        """
        try:
            length = self.file_handle.readinto(data)
        except BlockingIOError:
            raise IOError(
                "FileDataReader.readinto: unable to read {} bytes from file {}".format(
                    len(data), self.filename))

        return length

    def tell(self):
        """ Returns the position of the file cursor

        :return: Position of the file cursor
        :rtype: int
        """
        return self.file_handle.tell()

    def close(self):
        """ Closes the file
        
        :return: Nothing is returned:
        :rtype: None
        :raise data_specification.exceptions.DataReadException: If the file\
                    cannot be closed
        """
        try:
            self.file_handle.close()
        except Exception:
            DataReadException("File {} cannot be closed".format(self.filename))
