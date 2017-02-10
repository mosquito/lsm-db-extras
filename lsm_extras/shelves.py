from .base import Base

try:
    import cPickle as pickle
except ImportError:
    import pickle


class LSMShelf(Base):
    __slots__ = "__encoding", "__protocol"

    def __init__(self, filename, encoding="utf-8", protocol=3):
        super().__init__(filename)
        self.__encoding = encoding
        self.__protocol = protocol

    def _encode_value(self, value):
        return pickle.dumps(value, protocol=self.__protocol)

    def _decode_value(self, value):
        return pickle.loads(value)

    def _encode_key(self, key):
        return key.encode(self.__encoding)

    def _decode_key(self, key):
        return key.decode(self.__encoding)


Shelf = LSMShelf
