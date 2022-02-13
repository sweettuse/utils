from itertools import repeat

import pytest

from utils.core import interleave, pairwise, take


def test_interleave():
    assert [0, 'blah', 1, 'blah'] == list(interleave(range(2), repeat('blah')))
    assert [0, 3, 1, 4, 2, 5] == list(interleave(range(3), range(3, 6)))
    assert [0, 2, 4, 1, 3, 5] == list(interleave(range(2), range(2, 4), range(4, 6)))

    rs = range(2), range(2, 4), range(4, 5)
    assert [0, 2, 4, 1, 3] == list(interleave(*rs, longest=True))
    assert [0, 2, 4] == list(interleave(*rs))


def test_pairwise():
    assert [(0, 1), (1, 2)] == list(pairwise(range(3)))


def test_take():
    with pytest.raises(ValueError):
        take(-1, range(3))
    with pytest.raises(ValueError):
        take('jeb', range(3))
    assert take(0, range(3)) == []
    assert take(1, range(3)) == [0]
    assert take(62, range(3)) == [0, 1, 2]
