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

""" Used to generate memory images for a SpiNNaker CPU core from a set of \
    instructions.

The main part of this package is the \
:py:class:`data_specification.DataSpecificationGenerator` \
class. This is used to generate a "Data Specification", which can then be \
executed to produce a memory image.  This package also handles this function \
if required, through the \
:py:class:`data_specification.DataSpecificationExecutor` class.

Functional Requirements
=======================

Creation of a Data Specification Language file which can be executed to \
produce a memory image.

   * Any errors that can be checked during the creation of the \
     specification should throw an exception.

   * It will be impossible to detect all errors at creation time.

   * There should be no assumption of where the data specification will \
     be stored, although a default provision of a way to write the \
     specification to a file is acceptable.

Execution of a Data Specification Language file, producing a memory image.

   * This should detect any errors during execution and report them, \
     halting the execution.

   * There should be no assumption of where the data specification is \
     read from, although a default provision of a way to read the \
     specification from a file is acceptable.

Use Cases
=========

There are a number of use-cases of this library:

  * :py:class:`~data_specification.DataSpecificationGenerator` \
    is used to create a compressed memory image which can be expanded later, \
    to reduce the amount of data that needs to be transferred over a slow \
    connection.

  * :py:class:`~data_specification.DataSpecificationExecutor` \
    is used to execute a previously generated specification at the receiving \
    end of a slow connection.
"""
from data_specification._version import (  # noqa
    __version__, __version_name__, __version_month__, __version_year__)
from .data_specification_executor import DataSpecificationExecutor
from .data_specification_executor_functions import (
    DataSpecificationExecutorFunctions)
from .data_specification_generator import DataSpecificationGenerator
from .memory_region import MemoryRegion
from .memory_region_collection import MemoryRegionCollection

__all__ = ["DataSpecificationExecutor", "DataSpecificationExecutorFunctions",
           "DataSpecificationGenerator", "MemoryRegion",
           "MemoryRegionCollection"]
