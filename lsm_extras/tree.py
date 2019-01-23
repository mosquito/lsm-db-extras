from io import BytesIO

from .base import Base

try:
    import cPickle as pickle
except ImportError:
    import pickle


class LSMTree(Base):
    def _encode_value(self, value):
        return pickle.dumps(value, protocol=3)

    def _decode_value(self, value):
        return pickle.loads(value)

    _encode_key = _encode_value
    _decode_key = _decode_value

    def items(self):
        for key, value in self._db:
            yield self._decode_key(key), self._decode_value(value)

    def update(self, data):
        """

        :type data: dict
        """
        self._db.update({
            self._encode_key(key): self._encode_value(value)
            for key, value in data.items()
        })

    def _encode_key_part(self, val):
        return pickle.dumps(val)

    def _decode_key_part(self, val):
        return pickle.loads(val)

    def _encode_key(self, key):
        with BytesIO() as buffer:
            for part in key:
                buffer.write(self._encode_key_part(part))
                buffer.write(b"\x00\xff")
            return buffer.getvalue()

    def _decode_key(self, key):
        key_parts = key.split(b"\x00\xff")[:-1]

        res = []
        for part in key_parts:
            res.append(self._decode_key_part(part))

        return tuple(res)

    def find(self, *prefix):
        key_parts = self._encode_key(prefix)
        for k, v in self._db.fetch_range(
                key_parts + b"\x00", key_parts + b"\xff"
        ):
            yield self._decode_key(k), self._decode_value(v)

    def remove(self, *prefix):
        key_parts = self._encode_key(prefix)
        self._db.delete_range(key_parts + b"\x00", key_parts + b"\xff")
