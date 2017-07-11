import os.path as path

__all__ = ["get_executor_filename"]

# Name of the executor APLX in the same directory as this file
_FILENAME = "data_specification_executor.aplx"


def get_executor_filename():
    """Gets the absolute path of the data specification executor binary that
    can be loaded onto a SpiNNaker board."""
    return path.join(path.dirname(path.realpath(__file__)), _FILENAME)
