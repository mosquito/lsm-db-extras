from functools import partial

import itertools
import pytest
from multiprocessing.pool import ThreadPool, Pool
from lsm_extras.dict import LSMDict
from tempfile import NamedTemporaryFile


def insert_range(items, filename):
    with LSMDict(filename) as shelf:
        for i in items:
            shelf[i] = i


def remove_range(items, filename):
    with LSMDict(filename) as shelf:
        for key in items:
            del shelf[key]


def split_seq(iterable, size):
    it = iter(iterable)
    item = list(itertools.islice(it, size))

    while item:
        yield item
        item = list(itertools.islice(it, size))


@pytest.fixture
def get_dict():
    with NamedTemporaryFile(suffix=".ldb", mode="r") as tmpfile:
        yield partial(LSMDict, tmpfile.name)


def test_simple(get_dict):
    shelf = get_dict()
    shelf['foo'] = True
    shelf.sync()
    assert shelf['foo']
    assert 'foo' in shelf
    assert shelf.get('foo')
    assert shelf.get('bar') is None

    with pytest.raises(KeyError):
        shelf['bar']

    shelf.close()

    assert shelf.closed

    with pytest.raises(RuntimeError):
        shelf['foo']

    assert shelf.filename in repr(shelf)


def test_len(get_dict):
    shelf = get_dict()
    for i in range(1000):
        shelf['foo %d' % i] = True

    assert len(shelf) == 1000


def test_iter(get_dict):
    shelf = get_dict()
    for i in range(1000):
        shelf['%d' % i] = True

    sorted(iter(shelf)) == list(map(str, range(1000)))


def test_reopen(get_dict):
    shelf1 = get_dict()

    for i in range(1000):
        shelf1['%d' % i] = True

    shelf1.close()

    shelf2 = get_dict()
    sorted(iter(shelf2)) == list(map(str, range(1000)))


def test_concurrent_threads(get_dict):
    pool = ThreadPool(16)

    with get_dict() as shelf:
        filename = shelf.filename

    for _ in pool.imap_unordered(partial(insert_range, filename=filename), split_seq(range(1000), 100)):
        pass

    for _ in pool.imap_unordered(partial(remove_range, filename=filename), split_seq(range(1000), 100)):
        pass

    assert sorted(iter(get_dict())) == list()


def test_concurrent_processes(get_dict):
    pool = Pool(16)

    with get_dict() as shelf:
        filename = shelf.filename

    for _ in pool.imap_unordered(partial(insert_range, filename=filename), split_seq(range(10000), 1000)):
        pass

    for _ in pool.imap_unordered(partial(remove_range, filename=filename), split_seq(range(10000), 1000)):
        pass

    assert sorted(iter(get_dict())) == list()
