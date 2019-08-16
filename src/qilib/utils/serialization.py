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
from typing import Any, Dict, Callable, ClassVar

from qilib.data_set import MongoDataSetIO
import numpy as np

TransformFunction = Callable[[Any], Any]


class JsonSerializeKey:
    """ The custum value types for the JSON serializer."""
    OBJECT = '__object__'
    CONTENT = '__content__'


class Encoder(JSONEncoder):
    """ A JSON encoder """

    encoders: ClassVar[Dict[type, TransformFunction]] = {}

    def default(self, o):
        if type(o) in self.encoders:
            return self.encoders[type(o)](o)

        return JSONEncoder.default(self, o)


class Decoder(JSONDecoder):
    """ A JSON dncoder """

    decoders: ClassVar[Dict[type, TransformFunction]] = {}

    def __init__(self):
        super().__init__(object_hook=self._object_hook)

    def _object_hook(self, obj):
        if isinstance(obj, dict):
            if JsonSerializeKey.OBJECT in obj:
                if obj[JsonSerializeKey.OBJECT] in self.decoders:
                    return self.decoders[obj[JsonSerializeKey.OBJECT]](obj)
                else:
                    raise ValueError()

        return obj


def serialize(data: Any) -> str:
    """ Serializes a Python object to JSON

    Args:
        data: Any Python object

    Returns:
        JSON encoded string

    """

    return dumps(transform_data(data), cls=Encoder)


def unserialize(data: str) -> Any:
    """ Unserializes a JSON string to a Python object

    Args:
        data: The JSON encoded string

    Returns:
        A Python object decoded from the JSON string
    """

    return loads(data, cls=Decoder)


def _transform(data):
    type_ = type(data)
    if type_ in Encoder.encoders:
        return Encoder.encoders[type_](data)

    return data


def transform_data(data: Any) -> Any:
    """ Recursively transfer a Python object and apply transform functions to it

    Args:
        data: Any Python object

    Returns:
        The transformed data
    """

    if isinstance(data, dict):
        new = {}
        for key, value in data.items():
            if isinstance(value, (dict, list, tuple)):
                new[key] = transform_data(value)
            else:
                new[key] = _transform(value)

        return new

    elif isinstance(data, (list,)):
        new = []
        for item in data:
            new.append(transform_data(_transform(item)))

        return new

    return _transform(data)


def encode_bytes(data):
    return {JsonSerializeKey.OBJECT: bytes.__name__, JsonSerializeKey.CONTENT: data.decode('utf-8')}


def decode_bytes(data):
    return data[JsonSerializeKey.CONTENT].encode('utf-8')


def register_encoder(type_: type, encode_func: TransformFunction) -> None:
    """ Registers an encoder for a given type

    Args:
        type_: The type
        encode_func: The transform function

    """

    Encoder.encoders[type_] = encode_func


def register_decoder(type_name: str, decode_func: TransformFunction) -> None:
    """ Registers a decoder for a given type

    Args:
        type_name: The type name
        decode_func: The transform function
    """

    Decoder.decoders[type_name] = decode_func


register_encoder(bytes, encode_bytes)
register_decoder(bytes.__name__, decode_bytes)

register_encoder(np.ndarray, MongoDataSetIO.encode_numpy_array)
register_decoder(np.array.__name__, MongoDataSetIO.decode_numpy_array)
