"""
utility calls for interpreting bits of the dsg
"""

from data_specification import constants
from data_specification.data_specification_generator import \
    DataSpecificationGenerator
from spinn_storage_handlers.file_data_writer import FileDataWriter

import tempfile
import os
import threading

# used to stop file conflicts
_lock_condition = threading.Condition()


def get_region_base_address_offset(app_data_base_address, region):
    """
    helper method which finds the address of the of a given region for the dsg
    :param app_data_base_address: base address for the core
    :param region: the region id we're looking for
    :return:
    """
    return (app_data_base_address +
            constants.APP_PTR_TABLE_HEADER_BYTE_SIZE + (region * 4))


def get_data_spec_and_file_writer_filename(
        processor_chip_x, processor_chip_y, processor_id,
        hostname, report_directory, write_text_specs,
        application_run_time_report_folder):
    """

    :param processor_chip_x:
    :param processor_chip_y:
    :param processor_id:
    :param hostname:
    :param report_directory:
    :param write_text_specs:
    :param application_run_time_report_folder:
    :return:
    """

    binary_file_path = get_data_spec_file_path(
        processor_chip_x, processor_chip_y, processor_id, hostname,
        application_run_time_report_folder)
    data_writer = FileDataWriter(binary_file_path)

    # check if text reports are needed and if so initialise the report
    # writer to send down to dsg
    report_writer = None
    if write_text_specs:
        new_report_directory = os.path.join(report_directory,
                                            "data_spec_text_files")

        # uses locks to stop multiple instances of this writing the same
        # folder at the same time (os breaks down and throws exception
        # otherwise)
        _lock_condition.acquire()
        if not os.path.exists(new_report_directory):
            os.mkdir(new_report_directory)
        _lock_condition.release()

        file_name = "{}_dataSpec_{}_{}_{}.txt" \
            .format(hostname, processor_chip_x, processor_chip_y,
                    processor_id)
        report_file_path = os.path.join(new_report_directory, file_name)
        report_writer = FileDataWriter(report_file_path)

    # build the file writer for the spec
    spec = DataSpecificationGenerator(data_writer, report_writer)

    return data_writer.filename, spec


def get_data_spec_file_path(processor_chip_x, processor_chip_y,
                            processor_id, hostname,
                            application_run_time_folder):
    """
    :param processor_chip_x:
    :param processor_chip_y:
    :param processor_id:
    :param hostname:
    :param application_run_time_folder:
    :return:
    """

    if application_run_time_folder == "TEMP":
        application_run_time_folder = tempfile.gettempdir()

    binary_file_path = (
        application_run_time_folder + os.sep +
        "{}_dataSpec_{}_{}_{}.dat".format(
            hostname, processor_chip_x, processor_chip_y, processor_id))
    return binary_file_path
