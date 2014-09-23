from data_specification.abstract_data_writer import AbstractDataWriter
from data_specification.exceptions import DataWriteException


class FileDataWriter(AbstractDataWriter):
    def __init__(self, filename):
        """
        :param filename: The file to write to
        :type filename: str
        :raise data_specification.exceptions.DataWriteException: If the file\
                    cannot found or opened for writing
        """
        self.filename = filename
        try:
            self.file_handle = open(self.filename, "wb")
        except:
            raise DataWriteException(
                "Unable to open file {} for writing\n".format(filename))

    def write(self, data):
        """ See :py:meth:`data_specification.abstract_data_writer.AbstractDataWriter.write`
        """
        try:
            self.file_handle.write(data)
        except:
            raise IOError(
                "FileDataWriter.write: unable to write {0:d} bytes to file {1:s}".format(
                    len(data), self.filename))

    def tell(self):
        """ Returns the position of the file cursor

        :return: Position of the file cursor
        :rtype: int
        """
        return self.file_handle.tell()

    def close(self):
        """ Closes the file
        
        :return: Nothing is returned
        :rtype: None
        :raise data_specification.exceptions.DataWriteException: If the file\
                    cannot be closed
        """
        self.filename = None

        try:
            self.file_handle.close()
        except:
            raise IOError(
                "FileDataWriter.close: unable to close file {}"
                .format(self.filename))
