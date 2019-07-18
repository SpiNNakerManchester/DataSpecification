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

import unittest
from data_specification import MemoryRegionCollection, MemoryRegion
from data_specification.exceptions import (
    RegionInUseException, NoRegionSelectedException)


class MyTestCase(unittest.TestCase):
    def test_mrc_basics(self):
        mrc = MemoryRegionCollection(16)
        self.assertEqual(len(mrc), 16)
        self.assertEqual(mrc.count_used_regions(), 0)
        mr = MemoryRegion(False, 32)
        mr_b = MemoryRegion(True, 16)
        mrc[2] = mr
        self.assertEqual(len(mrc), 16)
        self.assertEqual(mrc.count_used_regions(), 1)
        with self.assertRaises(RegionInUseException):
            mrc[2] = mr
        with self.assertRaises(NoRegionSelectedException):
            mrc[-2] = mr
        with self.assertRaises(NoRegionSelectedException):
            mrc[16] = mr
        for r in mrc:
            assert r is None or r == mr
        self.assertFalse(mrc.is_empty(2))
        self.assertFalse(mrc.is_unfilled(2))
        for r in range(16):
            if r != 2:
                self.assertTrue(mrc.is_empty(r))
        mrc[7] = mr_b
        self.assertEqual(mrc.count_used_regions(), 2)
        self.assertFalse(mrc.is_empty(7))
        self.assertTrue(mrc.is_unfilled(7))
        mr0 = MemoryRegion(True, 0)
        for r in range(7):
            if mrc.is_empty(r):
                mrc[r] = mr0
        assert mrc[7] == mr_b
        self.assertEqual(mrc.count_used_regions(), 8)
        assert [region is not None for region in mrc] == [
            True, True, True, True, True, True, True, True,
            False, False, False, False, False, False, False, False]
        assert [mrc.needs_to_write_region(r) for r in range(len(mrc))] == [
            True, True, True, False, False, False, False, False,
            False, False, False, False, False, False, False, False]
        with self.assertRaises(NoRegionSelectedException):
            mrc.needs_to_write_region(49)


if __name__ == '__main__':
    unittest.main()
