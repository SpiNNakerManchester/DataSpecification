# Copyright (c) 2014 The University of Manchester
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Used to generate memory images for a SpiNNaker CPU core from a set of
instructions.

The main part of this package is the
:py:class:`DataSpecificationGenerator`
class. This is used to generate a "Data Specification", which can then be
executed to produce a memory image.  This package also handles this function
if required, through the
:py:class:`DataSpecificationExecutor` class.

Functional Requirements
=======================

Creation of a Data Specification Language file which can be executed to
produce a memory image.

* Any errors that can be checked during the creation of the specification
  should throw an exception.

* It will be impossible to detect all errors at creation time.

* There should be no assumption of where the data specification will be
  stored, although a default provision of a way to write the specification to
  a file is acceptable.

Execution of a Data Specification Language file, producing a memory image.

* This should detect any errors during execution and report them, halting the
  execution.

* There should be no assumption of where the data specification is read from,
  although a default provision of a way to read the specification from a file
  is acceptable.

Use Cases
=========

There are a number of use-cases of this library:

* :py:class:`DataSpecificationGenerator` is used to create a compressed memory
  image which can be expanded later, to reduce the amount of data that needs
  to be transferred over a slow connection.

* :py:class:`DataSpecificationExecutor` is used to execute a previously
  generated specification at the receiving end of a slow connection.

Main API
========
"""
from data_specification._version import (
    __version__, __version_name__, __version_month__, __version_year__)
from .data_specification_executor import DataSpecificationExecutor
from .data_specification_executor_functions import (
    DataSpecificationExecutorFunctions)
from .data_specification_generator import DataSpecificationGenerator
from .abstract_memory_region import AbstractMemoryRegion
from .memory_region_real import MemoryRegionReal
from .memory_region_reference import MemoryRegionReference
from .memory_region_collection import MemoryRegionCollection
from .reference_context import ReferenceContext

__all__ = [
    "__version__", "__version_name__", "__version_month__", "__version_year__",
    "DataSpecificationExecutor", "DataSpecificationExecutorFunctions",
    "DataSpecificationGenerator", "AbstractMemoryRegion",
    "MemoryRegionReal", "MemoryRegionReference",
    "MemoryRegionCollection", "ReferenceContext"]
