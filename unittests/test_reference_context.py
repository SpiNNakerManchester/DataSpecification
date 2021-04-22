import pytest
from data_specification.reference_context import ReferenceContext


def test_reference_context():

    # Not in a context, so raise error
    with pytest.raises(ValueError):
        ReferenceContext.next()

    with ReferenceContext():
        for i in range(10):
            assert(ReferenceContext.next() == i)

        # Even when nested, it stays global
        with ReferenceContext():
            for i in range(10):
                assert(ReferenceContext.next() == i + 10)

        # Even when the nested version exits, it stays global
        for i in range(10):
            assert(ReferenceContext.next() == i + 20)

    # Back outside a context, so raise error
    with pytest.raises(ValueError):
        ReferenceContext.next()
