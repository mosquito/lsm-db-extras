import itertools
from functools import partial
from multiprocessing.pool import Pool, ThreadPool
from tempfile import NamedTemporaryFile

import pytest

from lsm_extras.dict import LSMDict


def insert_range(items, filename):
    with LSMDict(filename) as storage:
        for i in items:
            storage[i] = i


def remove_range(items, filename):
    with LSMDict(filename) as storage:
        for key in items:
            del storage[key]


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
    storage = get_dict()
    storage['foo'] = True
    storage.sync()
    assert storage['foo']
    assert 'foo' in storage
    assert storage.get('foo')
    assert storage.get('bar') is None

    storage.update({"boo": "1", "foo": 2})

    assert storage['boo'] == '1'
    assert storage['foo'] == 2

    with pytest.raises(KeyError):
        storage['bar']

    storage.close()

    assert storage.closed

    with pytest.raises(RuntimeError):
        storage['foo']

    assert storage.filename in repr(storage)


def test_len(get_dict):
    storage = get_dict()
    for i in range(1000):
        storage['foo %d' % i] = True

    assert len(storage) == 1000


def test_iter(get_dict):
    storage = get_dict()
    for i in range(1000):
        storage['%d' % i] = True

    sorted(iter(storage)) == list(map(str, range(1000)))


def test_reopen(get_dict):
    storage1 = get_dict()

    for i in range(1000):
        storage1['%d' % i] = True

    storage1.close()

    storage2 = get_dict()
    sorted(iter(storage2)) == list(map(str, range(1000)))


def test_concurrent_threads(get_dict):
    pool = ThreadPool(16)

    with get_dict() as storage:
        filename = storage.filename

    for _ in pool.imap_unordered(partial(insert_range, filename=filename),
                                 split_seq(range(1000), 100)):
        pass

    for _ in pool.imap_unordered(partial(remove_range, filename=filename),
                                 split_seq(range(1000), 100)):
        pass

    assert sorted(iter(get_dict())) == list()


def test_concurrent_processes(get_dict):
    pool = Pool(16)

    with get_dict() as storage:
        filename = storage.filename

    for _ in pool.imap_unordered(partial(insert_range, filename=filename),
                                 split_seq(range(10000), 1000)):
        pass

    for _ in pool.imap_unordered(partial(remove_range, filename=filename),
                                 split_seq(range(10000), 1000)):
        pass

    assert sorted(iter(get_dict())) == list()


def insert_args(items, filename):
    with LSMDict(
            filename, mmap=0, autowork=0, automerge=4, autoflush=1024
    ) as storage:
        for i in items:
            storage[i] = i
