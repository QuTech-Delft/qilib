"""Quantum Inspire library

Copyright 2019 QuTech Delft

qilib is available under the [MIT open-source license](https://opensource.org/licenses/MIT):

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from json import JSONEncoder, JSONDecoder, dumps, loads
from qilib.data_set import MongoDataSetIO
import numpy as np


class Encoder(JSONEncoder):
    encoders = {}

    def default(self, o):
        if type(o) in self.encoders:
            return self.encoders[type(o)](o)

        return JSONEncoder.default(self, o)


class Decoder(JSONDecoder):
    decoders = {}

    def __init__(self):
        super().__init__(object_hook=self._object_hook)

    def _object_hook(self, obj):
        if isinstance(obj, dict):
            if '__object__' in obj:
                if obj['__object__'] in self.decoders:
                    return self.decoders[obj['__object__']](obj)
                else:
                    raise ValueError()

        return obj


def serialize(data):
    return dumps(data, cls=Encoder)


def unserialize(data):
    return loads(data, cls=Decoder)


def _transform(data):
    type_ = type(data)
    if type_ in Encoder.encoders:
        return Encoder.encoders[type_](data)

    return data


def transform_data(data):
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, (dict, list, tuple)):
                transform_data(_transform(value))
            else:
                data[key] = _transform(value)

    elif isinstance(data, (list, tuple)):
        for item in data:
            transform_data(item)

    return data


def encode_bytes(data):
    return {'__object__': bytes.__name__, '__content__': data.decode('utf-8')}


def decode_bytes(data):
    return data['__content__'].encode('utf-8')


def register_encoder(type_, encode_func):
    Encoder.encoders[type_] = encode_func


def register_decoder(type_name, decode_func):
    Decoder.decoders[type_name] = decode_func


register_encoder(bytes, encode_bytes)
register_decoder(bytes.__name__, decode_bytes)

register_encoder(np.ndarray, MongoDataSetIO.encode_numpy_array)
register_decoder(np.array.__name__, MongoDataSetIO.decode_numpy_array)
