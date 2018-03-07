from .exceptions \
    import RegionInUseException, NoRegionSelectedException


class MemoryRegionCollection(object):
    """Collection of memory regions.
    """

    __slots__ = [
        # map of region id to region data
        "_regions"
    ]

    def __init__(self, n_regions):
        """Create a new MemoryRegionCollection with the given number of regions.
        """
        self._regions = [None] * n_regions

    def __len__(self):
        return len(self._regions)

    def __getitem__(self, key):
        return self._regions[key]

    def __setitem__(self, key, value):
        if key < 0 or key >= len(self._regions):
            raise NoRegionSelectedException(
                "the region id requested is beyond the supported number of"
                "available region ids")
        if self._regions[key] is not None:
            raise RegionInUseException(key)
        self._regions[key] = value

    def __iter__(self):
        return iter(self._regions)

    @property
    def regions(self):
        for r in self._regions:
            yield r

    def is_empty(self, region):
        return self._regions[region] is None

    def is_unfilled(self, region):
        if self.is_empty(region):
            return True
        return self._regions[region].unfilled

    def count_used_regions(self):
        return sum(r is not None for r in self._regions)

    def needs_to_write_region(self, region):
        """ Helper method which determines if a unfilled region actually \
            needs to be written (optimisation to stop large data files).

        :param region: the region id to which the test is being ran on
        :return: a boolean stating if the region needs to be written
        :rtype: bool
        :raise NoRegionSelectedException: \
            when the id is beyond the expected region range
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
