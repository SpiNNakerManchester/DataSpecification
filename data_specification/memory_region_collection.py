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

from .exceptions import (
    RegionInUseException, NoRegionSelectedException)


class MemoryRegionCollection(object):
    """ Collection of memory regions.
    """

    __slots__ = [
        # map of region ID to region data
        "_regions"
    ]

    def __init__(self, n_regions):
        """
        :param int n_regions: The number of regions in the collection.
        """
        self._regions = [None] * n_regions

    def __len__(self):
        """
        :rtype: int
        """
        return len(self._regions)

    def __getitem__(self, key):
        """
        :rtype: MemoryRegion
        """
        return self._regions[key]

    def __setitem__(self, key, value):
        """
        :param int key:
        :param MemoryRegion value:
        """
        if key < 0 or key >= len(self._regions):
            raise NoRegionSelectedException(
                "the region ID requested is beyond the supported number of "
                "available region IDs")
        if self._regions[key] is not None:
            raise RegionInUseException(key)
        self._regions[key] = value

    def __iter__(self):
        """
        :rtype: iterable(MemoryRegion)
        """
        return iter(self._regions)

    def is_empty(self, region):
        """
        :param int region: The ID of the region
        :rtype: bool
        """
        return self._regions[region] is None
