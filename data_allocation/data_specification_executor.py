class DataSpecificationExecutor(object):
    """ Used to execute a data specification language file to produce a memory\
        image
    """
    
    def __init__(self, spec_reader, mem_writer, space):
        """
        :param spec_reader: The object to read the specification language file\
                    from
        :type spec_reader: Implementation of\
                    :py:class:`data_allocation.abstract_data_reader.AbstractDataReader`
        :param mem_writer: The object to write the memory image to
        :type mem_writer: Implementation of\
                    :py:class:`data_allocation.abstract_data_writer.AbstractDataWriter`
        :param space: The amount of space into which the final image must fit,\
                    in bytes
        :type space: int
        :raise data_allocation.exceptions.DataReadException:\
                    If a read from external storage fails
        :raise data_allocation.exceptions.DataWriteException:\
                    If a write to external storage fails
        """
        pass
    
    def execute(self):
        """ Executes the specification
        
        :return: The number of bytes used by the image
        :rtype: int
        :raise data_allocation.exceptions.DataReadException:\
                    If a read from external storage fails
        :raise data_allocation.exceptions.DataWriteException:\
                    If a write to external storage fails
        :raise data_allocation.exceptions.DataSpecificationException:\
                    If there is an error when executing the specification
        """
        pass
