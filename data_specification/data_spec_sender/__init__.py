import os.path

# Name of the executor APLX in the same directory as this file
_FILENAME = "data_specification_executor.aplx"


def data_specification_executor():
    """ Gets the absolute path of the data specification executor binary that\
        can be loaded onto a SpiNNaker board.

    :return: A fully-qualified filename.
    """
    return os.path.join(os.path.dirname(__file__), _FILENAME)


__all__ = ["data_specification_executor"]
