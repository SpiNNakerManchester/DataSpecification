# Copyright (c) 2017-2019 The University of Manchester
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

""" Utility calls for interpreting bits of the DSG
"""

import os
import threading
import tempfile
from spinn_storage_handlers import FileDataWriter
from .constants import APP_PTR_TABLE_HEADER_BYTE_SIZE
from .data_specification_generator import DataSpecificationGenerator

# used to stop file conflicts
_lock_condition = threading.Condition()


def _mkdir(directory):
    # Guarded to stop us from hitting things twice internally; it's not
    # perfect since other processes could also happen along.
    with _lock_condition:
        try:
            if not os.path.exists(directory):
                os.mkdir(directory)
        except OSError:
            # Assume an external race beat us
            pass


def get_region_base_address_offset(app_data_base_address, region):
    """ Find the address of the of a given region for the DSG
    :param app_data_base_address: base address for the core
    :param region: the region ID we're looking for
    """
    return (app_data_base_address +
            APP_PTR_TABLE_HEADER_BYTE_SIZE + (region * 4))


_DAT_TMPL = "{}_dataSpec_{}_{}_{}.dat"
_RPT_TMPL = "{}_dataSpec_{}_{}_{}.txt"
_RPT_DIR = "data_spec_text_files"


def get_data_spec_and_file_writer_filename(
        processor_chip_x, processor_chip_y, processor_id,
        hostname, report_directory="TEMP", write_text_specs=False,
        application_run_time_report_folder="TEMP"):
    """ Encapsulates the creation of the DSG writer and the file paths
    :param processor_chip_x: x-coordinate of the chip
    :type processor_chip_x: int
    :param processor_chip_y: y-coordinate of the chip
    :type processor_chip_y: int
    :param processor_id: The processor ID
    :type processor_id: int
    :param hostname: The hostname of the SpiNNaker machine
    :type hostname: str
    :param report_directory: the directory for the reports folder
    :type report_directory: file path
    :param write_text_specs:\
        True if a textual version of the specification should be written
    :type write_text_specs: bool
    :param application_run_time_report_folder:\
        The folder to contain the resulting specification files; if 'TEMP'\
        then a temporary directory is used.
    :type application_run_time_report_folder: str
    :return: the filename of the data writer and the data specification object
    :rtype: tuple(str, \
        :py:class:`~data_specification.DataSpecificationGenerator`)
    """
    # pylint: disable=too-many-arguments
    if application_run_time_report_folder == "TEMP":
        application_run_time_report_folder = tempfile.gettempdir()

    data_writer = FileDataWriter(os.path.join(
        application_run_time_report_folder, _DAT_TMPL.format(
            hostname, processor_chip_x, processor_chip_y, processor_id)))

    # check if text reports are needed and if so initialise the report
    # writer to send down to DSG
    report_writer = get_report_writer(
        processor_chip_x, processor_chip_y, processor_id,
        hostname, report_directory=report_directory,
        write_text_specs=write_text_specs)

    # build the file writer for the spec
    spec = DataSpecificationGenerator(data_writer, report_writer)

    return data_writer.filename, spec


def get_report_writer(
        processor_chip_x, processor_chip_y, processor_id,
        hostname, report_directory="TEMP", write_text_specs=False):
    """ check if text reports are needed and if so initialise the report
        writer to send down to DSG
    :param processor_chip_x: x-coordinate of the chip
    :type processor_chip_x: int
    :param processor_chip_y: y-coordinate of the chip
    :type processor_chip_y: int
    :param processor_id: The processor ID
    :type processor_id: int
    :param hostname: The hostname of the SpiNNaker machine
    :type hostname: str
    :param report_directory: the directory for the reports folder
    :type report_directory: file path
    :param write_text_specs:\
        True if a textual version of the specification should be written
    :type write_text_specs: bool
    :return: the report_writer_object or None if not reporting
    """
    # pylint: disable=too-many-arguments

    # check if text reports are needed and if so initialise the report
    # writer to send down to DSG
    report_writer = None
    if write_text_specs:
        if report_directory == "TEMP":
            report_directory = tempfile.gettempdir()
        new_report_directory = os.path.join(report_directory, _RPT_DIR)
        _mkdir(new_report_directory)
        report_writer = FileDataWriter(
            os.path.join(new_report_directory, _RPT_TMPL.format(
                hostname, processor_chip_x, processor_chip_y, processor_id)))

    return report_writer
