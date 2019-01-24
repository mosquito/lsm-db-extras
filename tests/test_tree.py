from functools import partial

import pytest
from lsm_extras import LSMTree
from tempfile import NamedTemporaryFile


@pytest.fixture
def get_tree():
    with NamedTemporaryFile(suffix=".ldb", mode="r") as tmpfile:
        yield partial(LSMTree, tmpfile.name)


def test_simple(get_tree):
    tree = get_tree()

    count = 5000

    prefixes = (
        ('first',),
        ('second',),
        (43,),
        (9, None, 'Foo'),
        (9, None, 'bar')
    )

    for prefix in prefixes:
        with tree.transaction():
            expected = sorted(((prefix + (i,)), i * 2) for i in range(count))

            for i in range(count):
                tree[prefix + (i,)] = i * 2

            assert sorted(tree.find(*prefix)) == expected

    for prefix in prefixes:
        with tree.transaction():
            assert list(tree.find(*prefix))
            tree.remove_range(*prefix)
            assert not list(tree.find(*prefix))

    for i in range(count):
        tree['purged', i] = i * 2

    assert sorted(tree.items()) != []

    tree.purge()

    assert sorted(tree.items()) == []
