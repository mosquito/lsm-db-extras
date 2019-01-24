import struct
from io import BytesIO

from .base import Base

try:
    import cPickle as pickle
except ImportError:
    import pickle


class LSMTree(Base):
    SEP_START = b"\x00"
    SEP_END = b"\xff"
    SEPARATOR = SEP_START + SEP_END

    KEY_HDR = ">H"
    KEY_HDR_SIZE = struct.calcsize(KEY_HDR)

    PACKER = pickle.dumps
    UNPACKER = pickle.loads

    def _encode_value(self, value):
        return self.PACKER(value, protocol=3)

    def _decode_value(self, value):
        return self.UNPACKER(value)

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

    def _encode_key(self, key):
        with BytesIO() as buffer:
            for part in key:
                data = self._encode_value(part)
                buffer.write(struct.pack(self.KEY_HDR, len(data)))
                buffer.write(data)
                buffer.write(self.SEPARATOR)
            return buffer.getvalue()

    def _decode_key(self, key):
        key_parts = []
        with BytesIO(key) as buffer:
            while True:
                hdr = buffer.read(self.KEY_HDR_SIZE)
                if not hdr:
                    break

                size = struct.unpack(self.KEY_HDR, hdr)[0]
                key_parts.append(self._decode_value(buffer.read(size)))

                if not buffer.read(len(self.SEPARATOR)):
                    break

        return tuple(key_parts)

    def _encode_range(self, prefix):
        key_parts = self._encode_key(prefix)
        return (
            key_parts + self.SEP_START,
            key_parts + self.SEP_END,
        )

    def find(self, *prefix):
        r = self._encode_range(prefix)
        for k, v in self._db.fetch_range(*r):
            key = self._decode_key(k)
            value = self._decode_value(v)
            yield key, value

    def remove_range(self, *prefix):
        self._db.delete_range(*self._encode_range(prefix))
