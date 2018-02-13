import os.path


def data_specification_executor():
    """ Get the name of the executable for the on-chip DSE.

    :return: A fully-qualified filename.
    """
    return os.path.join(os.path.dirname(__file__),
                        "data_specification_executor.aplx")


__all__ = ["data_specification_executor"]
