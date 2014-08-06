from data_specification import exceptions


class MemoryRegionCollection(object):
    """Collection of memory regions.
    """
    def __init__(self, n_regions):
        """Create a new MemoryRegionCollection with the given number of regions.
        """
        self._n_regions = n_regions
        self._regions = [None] * n_regions
        self._mem_pointers = [0] * n_regions
        self._unfilled = [None] * n_regions

    def __len__(self):
        return self._n_regions

    def __getitem__(self, key):
        return self._regions[key]

    def __setitem__(self, key, value):
        if self._regions[key] is not None:
            raise exceptions.DataSpecificationRegionInUseException(key)
        self._regions[key] = value

    def __iter__(self):
        return iter(self._regions)

    @property
    def regions(self):
        for region in self._regions:
            yield region

    def is_empty(self, region):
        return self._regions[region] is None

    def set_unfilled(self, region):
        self._unfilled[region] = True

    def set_filled(self, region):
        self._unfilled[region] = False

    def is_unfilled(self, region):
        return self._unfilled[region]

    def count_used_regions(self):
        count = 0
        for i in self._regions:
            if i is not None:
                count += 1
        return count
