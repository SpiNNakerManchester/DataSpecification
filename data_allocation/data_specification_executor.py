class DataSpecificationExecutor(object):
    """ Used to execute a data specification language file to produce a memory\
        image
    """
    
    def __init__(self, spec_reader, mem_writer):
        """
        :param spec_reader: The object to read the specification language file\
                    from
        :type spec_reader: Implementation of\
                data_allocation.abstract_data_specification_writer.AbstractDataReader
        :param mem_writer: The object to write the memory image to
        :type mem_writer: Implementation of\
                data_allocation.abstract_data_specification_writer.AbstractDataWriter
        :raise data_allocation.exceptions.DataReadException:\
                    If a read from external storage fails
        :raise data_allocation.exceptions.DataWriteException:\
                    If a write to external storage fails
        """
        pass
    
    def execute(self):
        """ Executes the specification
        
        :return: Nothing is returned
        :rtype: None
        :raise data_allocation.exceptions.DataReadException:\
                    If a read from external storage fails
        :raise data_allocation.exceptions.DataWriteException:\
                    If a write to external storage fails
        :raise data_allocation.exceptions.DataSpecificationException:\
                    If there is an error when executing the specification
        """
        pass
