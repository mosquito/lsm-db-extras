from .base import Base

try:
    import cPickle as pickle
except ImportError:
    import pickle


class LSMDict(Base):
    def _encode_value(self, value):
        return pickle.dumps(value, protocol=3)

    def _decode_value(self, value):
        return pickle.loads(value)

    _encode_key = _encode_value
    _decode_key = _decode_value
