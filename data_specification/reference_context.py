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


class ReferenceContext(object):
    """
    Allows the generation of unique references within a context.
    """

    # Next available reference within the current context,
    # or None if no context has been created.
    __next_reference = None

    # Depth of current context; allows nesting without error
    __context_depth = 0

    def __enter__(self):
        # If this is the first context, start now
        if ReferenceContext.__context_depth == 0:
            ReferenceContext.__next_reference = 0

        # Increment the depth to allow nesting
        ReferenceContext.__context_depth += 1

    def __exit__(self, exc_type, exc_val, exc_tb):
        if ReferenceContext.__context_depth == 0:
            raise ValueError("Not currently in a reference context!")

        # Decrement the depth to allow nesting
        ReferenceContext.__context_depth -= 1

        # If we are now out of all the contexts, reset
        if ReferenceContext.__context_depth == 0:
            ReferenceContext.__next_reference = None

        return False

    @classmethod
    def next(cls):
        """
        Get the next reference ID in the current context.

        :rtype: int
        """
        if cls.__next_reference is None:
            raise ValueError("Not currently in a reference context!")
        ref = cls.__next_reference
        cls.__next_reference += 1
        return ref
