# Copyright (c) 2021 The University of Manchester
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
import pytest
from data_specification import ReferenceContext


def test_reference_context():

    # Not in a context, so raise error
    with pytest.raises(ValueError):
        ReferenceContext.next()

    with ReferenceContext():
        for i in range(10):
            assert ReferenceContext.next() == i

        # Even when nested, it stays global
        with ReferenceContext():
            for i in range(10):
                assert ReferenceContext.next() == i + 10

        # Even when the nested version exits, it stays global
        for i in range(10):
            assert ReferenceContext.next() == i + 20

    # Back outside a context, so raise error
    with pytest.raises(ValueError):
        ReferenceContext.next()
