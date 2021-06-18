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


class ReferenceContext(object):
    """ Allows the generation of unique references within a context
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
        """ Get the next reference in the current context
        """
        if cls.__next_reference is None:
            raise ValueError("Not currently in a reference context!")
        ref = cls.__next_reference
        cls.__next_reference += 1
        return ref