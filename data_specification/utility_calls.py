"""
utility calls for interpreting bits of the dsg
"""

from data_specification import constants


def get_region_base_address_offset(app_data_base_address, region):
    """
    helper method which finds the address of the of a gvien region for the dsg
    :param app_data_base_address: base address for
    :param region:
    :return:
    """
    return (app_data_base_address +
            constants.APP_PTR_TABLE_HEADER_BYTE_SIZE + (region * 4))
