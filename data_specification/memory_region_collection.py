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
        """ Create a new MemoryRegionCollection with the given number of\
            regions.

        :type n_regions: int
        """
        self._regions = [None] * n_regions

    def __len__(self):
        """
        :rtype: int
        """
        return len(self._regions)

    def __getitem__(self, key):
        """
        :rtype: :py:class:`~data_specification.MemoryRegion`
        """
        return self._regions[key]

    def __setitem__(self, key, value):
        """
        :type key: int
        :type value: :py:class:`~data_specification.MemoryRegion`
        """
        if key < 0 or key >= len(self._regions):
            raise NoRegionSelectedException(
                "the region ID requested is beyond the supported number of"
                "available region IDs")
        if self._regions[key] is not None:
            raise RegionInUseException(key)
        self._regions[key] = value

    def __iter__(self):
        """
        :rtype: iterable(:py:class:`~data_specification.MemoryRegion`)
        """
        return iter(self._regions)

    @property
    def regions(self):
        """
        :rtype: iterable(:py:class:`~data_specification.MemoryRegion`)
        """
        for r in self._regions:
            yield r

    def is_empty(self, region):
        """
        :rtype: bool
        """
        return self._regions[region] is None

    def is_unfilled(self, region):
        """
        :rtype: bool
        """
        if self.is_empty(region):
            return True
        return self._regions[region].unfilled

    def count_used_regions(self):
        """
        :rtype: int
        """
        return sum(r is not None for r in self._regions)

    def needs_to_write_region(self, region):
        """ Helper method which determines if a unfilled region actually \
            needs to be written (optimisation to stop large data files).

        :param region: the region ID to which the test is being ran on
        :return: a boolean stating if the region needs to be written
        :rtype: bool
        :raise NoRegionSelectedException: \
            when the ID is beyond the expected region range
        """
        if region >= len(self._regions):
            raise NoRegionSelectedException(
                "the region ID requested is beyond the supported number of"
                "available region IDs")
        if not self.is_unfilled(region):
            return True
        return any(
            not self.is_unfilled(r_id)
            for r_id in range(region, len(self._regions)))
