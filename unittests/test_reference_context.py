# Copyright (c) 2021 The University of Manchester
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
