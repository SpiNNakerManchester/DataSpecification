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

from .memory_region import MemoryRegion


class MemoryRegionReference(MemoryRegion):
    """ A reference to another memory region
    """

    __slots__ = ["__ref"]

    def __init__(self, ref):
        """
        :param int ref: Identifies what this refers to
        """
        self.__ref = ref

    @property
    def ref(self):
        """ Identifies what this references

        :rtype: int
        """
        return self.__ref
