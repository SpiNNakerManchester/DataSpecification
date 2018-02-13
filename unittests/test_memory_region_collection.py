import unittest
from data_specification import MemoryRegionCollection, MemoryRegion
from data_specification.exceptions import RegionInUseException,\
    NoRegionSelectedException


class MyTestCase(unittest.TestCase):
    def test_mrc_basics(self):
        mrc = MemoryRegionCollection(16)
        self.assertEqual(len(mrc), 16)
        self.assertEqual(mrc.count_used_regions(), 0)
        mr = MemoryRegion(0, False, 32)
        mrB = MemoryRegion(32, True, 16)
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
        mrc[7] = mrB
        self.assertEqual(mrc.count_used_regions(), 2)
        self.assertFalse(mrc.is_empty(7))
        self.assertTrue(mrc.is_unfilled(7))
        mr0 = MemoryRegion(0, True, 0)
        for r in range(7):
            if mrc.is_empty(r):
                mrc[r] = mr0
        assert mrc[7] == mrB
        self.assertEqual(mrc.count_used_regions(), 8)
        assert [mrc[r] is not None for r in range(len(mrc))] == [
            True, True, True, True, True, True, True, True,
            False, False, False, False, False, False, False, False]
        assert [mrc.needs_to_write_region(r) for r in range(len(mrc))] == [
            True, True, True, False, False, False, False, False,
            False, False, False, False, False, False, False, False]
        with self.assertRaises(NoRegionSelectedException):
            mrc.needs_to_write_region(49)


if __name__ == '__main__':
    unittest.main()
