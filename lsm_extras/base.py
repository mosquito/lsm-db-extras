import abc
import os.path
from lsm import LSM
from threading import RLock
from collections import MutableMapping


_LOCKS = {}


class Base(MutableMapping):
    __slots__ = "__db", "__lock", "__closed", "__filename",

    def __init__(self, filename):
        self.__filename = os.path.abspath(filename)

        if self.__filename not in _LOCKS:
            _LOCKS[self.__filename] = RLock()

        self.__lock = _LOCKS[self.__filename]
        self.__db = LSM(self.__filename)
        self.__closed = False

    @property
    def _db(self):
        if self.__closed:
            raise RuntimeError("Database closed")

        return self.__db

    def __iter__(self):
        with self.__lock:
            for key in self._db.keys():
                yield self._decode_key(key)

    def __len__(self):
        # FIXME: It's so slow
        with self.__lock:
            return sum(1 for _ in self._db.keys())

    def __contains__(self, key):
        return self._encode_key(key) in self._db

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def __getitem__(self, key):
        _key = self._encode_key(key)
        return self._decode_value(self._db[_key])

    def __setitem__(self, key, value):
        _key = self._encode_key(key)
        _value = self._encode_value(value)

        with self.__lock:
            error = True
            while error:
                try:
                    self._db[_key] = _value
                    error = False
                except Exception as e:
                    if e.args[0] != "Busy":
                        raise
                    continue

    def __delitem__(self, key):
        return self.delete(key)

    def delete(self, key):
        with self.__lock:
            error = True
            while error:
                try:
                    self._db.delete(self._encode_key(key))
                    error = False
                except Exception as e:
                    if e.args[0] != "Busy":
                        raise
                    continue

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    @property
    def closed(self):
        return self.__closed

    @property
    def filename(self):
        return self.__filename

    def close(self):
        if self.__closed:
            return

        self.__closed = True

        with self.__lock:
            self.__db.close()

    def __del__(self):
        if self.filename in _LOCKS:
            del _LOCKS[self.filename]

        self.close()

    def sync(self):
        with self.__lock:
            self._db.flush()

    def __repr__(self):
        return "<LSMShelf: %r>" % self.filename

    @abc.abstractmethod
    def _encode_key(self, key):
        raise NotImplementedError

    @abc.abstractmethod
    def _decode_key(self, key):
        raise NotImplementedError

    @abc.abstractmethod
    def _encode_value(self, value):
        raise NotImplementedError

    @abc.abstractmethod
    def _decode_value(self, value):
        raise NotImplementedError
