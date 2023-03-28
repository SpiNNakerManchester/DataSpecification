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

from .exceptions import (
    RegionInUseException, NoRegionSelectedException)


class MemoryRegionCollection(object):
    """
    Collection of memory regions (:py:class:`AbstractMemoryRegion`).
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
        :rtype: AbstractMemoryRegion
        """
        return self._regions[key]

    def __setitem__(self, key, value):
        """
        :param int key:
        :param AbstractMemoryRegion value:
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
        :rtype: iterable(AbstractMemoryRegion)
        """
        return iter(self._regions)

    def is_empty(self, region):
        """
        :param int region: The ID of the region
        :rtype: bool
        """
        return self._regions[region] is None
