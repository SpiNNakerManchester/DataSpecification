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

""" Constants used by the Data Structure Generator (DSG) \
    and the Specification Executor.
"""

# MAGIC Numbers:
# Data spec magic number
DSG_MAGIC_NUM = 0x5B7CA17E

# Application data magic number
APPDATA_MAGIC_NUM = 0xAD130AD6

# Version of the file produced by the DSE
DSE_VERSION = 0x00010000

# DSG Arrays and tables sizes:
MAX_REGISTERS = 16
MAX_MEM_REGIONS = 16
MAX_STRUCT_SLOTS = 16
MAX_STRUCT_ELEMENTS = 255
MAX_PACKSPEC_SLOTS = 16
MAX_CONSTRUCTORS = 16
MAX_PARAM_LISTS = 16
MAX_RNGS = 16
MAX_RANDOM_DISTS = 16

APP_PTR_TABLE_HEADER_BYTE_SIZE = 8
APP_PTR_TABLE_BYTE_SIZE = APP_PTR_TABLE_HEADER_BYTE_SIZE + MAX_MEM_REGIONS * 4

# Constants used by DSG command encoding:
LEN1 = 0
LEN2 = 1
LEN3 = 2
LEN4 = 3

NO_REGS = 0
DEST_ONLY = 4
SRC1_ONLY = 2
SRC1_AND_SRC2 = 3
DEST_AND_SRC1 = 6
ALL_REGS = 7

# return values from functions of the data spec executor
END_SPEC_EXECUTOR = -1
