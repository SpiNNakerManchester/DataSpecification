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

import unittest
from data_specification import MemoryRegionCollection, MemoryRegionReal
from data_specification.config_setup import unittest_setup
from data_specification.exceptions import (
    RegionInUseException, NoRegionSelectedException)


class MyTestCase(unittest.TestCase):

    def setUp(self):
        unittest_setup()

    def test_mrc_basics(self):
        mrc = MemoryRegionCollection(16)
        self.assertEqual(len(mrc), 16)
        mr = MemoryRegionReal(False, 32)
        mr_b = MemoryRegionReal(True, 16)
        mrc[2] = mr
        self.assertEqual(len(mrc), 16)
        with self.assertRaises(RegionInUseException):
            mrc[2] = mr
        with self.assertRaises(NoRegionSelectedException):
            mrc[-2] = mr
        with self.assertRaises(NoRegionSelectedException):
            mrc[16] = mr
        for r in mrc:
            assert r is None or r == mr
        self.assertFalse(mrc.is_empty(2))
        for r in range(16):
            if r != 2:
                self.assertTrue(mrc.is_empty(r))
        mrc[7] = mr_b
        self.assertFalse(mrc.is_empty(7))
        mr0 = MemoryRegionReal(True, 0)
        for r in range(7):
            if mrc.is_empty(r):
                mrc[r] = mr0
        assert mrc[7] == mr_b
        assert [region is not None for region in mrc] == [
            True, True, True, True, True, True, True, True,
            False, False, False, False, False, False, False, False]


if __name__ == '__main__':
    unittest.main()
