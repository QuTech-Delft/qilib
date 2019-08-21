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

from json import JSONEncoder, JSONDecoder
from typing import Any, Dict, Callable, ClassVar
from qilib.data_set import MongoDataSetIO
import numpy as np

# A callable type for transforming a given argument with a type to another type
TransformFunction = Callable[[Any], Any]


class JsonSerializeKey:
    """ The custum value types for the JSON serializer """
    OBJECT = '__object__'
    CONTENT = '__content__'


class Encoder(JSONEncoder):
    """ A JSON encoder """

    def __init__(self, **kwargs):
        """ Constructs a JSON Encoder """
        super().__init__(**kwargs)

        # creates a new transform table
        self.encoders: ClassVar[Dict[type, TransformFunction]] = {}

    def default(self, o):
        if type(o) in self.encoders:
            return self.encoders[type(o)](o)

        return JSONEncoder.default(self, o)


class Decoder(JSONDecoder):
    """ A JSON decoder """

    def __init__(self):
        """ Constructs a JSON Decoder """
        super().__init__(object_hook=self._object_hook)

        # creates a new transform table
        self.decoders: ClassVar[Dict[type, TransformFunction]] = {}

    def _object_hook(self, obj):
        if isinstance(obj, dict):
            if JsonSerializeKey.OBJECT in obj:
                if obj[JsonSerializeKey.OBJECT] in self.decoders:
                    return self.decoders[obj[JsonSerializeKey.OBJECT]](obj)
                else:
                    raise ValueError()

        return obj


def _encode_bytes(data: Any) -> Dict[str, Any]:
    return {JsonSerializeKey.OBJECT: bytes.__name__, JsonSerializeKey.CONTENT: data.decode('utf-8')}


def _decode_bytes(data: Dict[str, Any]) -> bytes:
    return data[JsonSerializeKey.CONTENT].encode('utf-8')


def _encode_tuple(item):
    return {
        JsonSerializeKey.OBJECT: tuple.__name__,
        JsonSerializeKey.CONTENT: [serializer.transform_data(value) for value in item]
    }


def _decode_tuple(data: Dict[str, Any]) -> tuple:
    return tuple(data[JsonSerializeKey.CONTENT])


class Serializer:
    """ A general serializer to serialize data to JSON and vice versa. It allows
     extending the types with a custom encoder and decoder"""

    def __init__(self, encoders: Dict[type, TransformFunction] = None,
                 decoders: Dict[str, TransformFunction] = None):
        """ Creates a serializer

        Args:
            encoders: The default encoders if any
            decoders: The default decoders if any
        """

        self.encoder = Encoder()
        self.decoder = Decoder()

        if encoders is None:
            encoders = {}
        self.encoder.encoders = encoders
        if decoders is None:
            decoders = {}
        self.decoder.decoders = decoders

        self.register(bytes, _encode_bytes, bytes.__name__, _decode_bytes)
        self.register(np.ndarray, MongoDataSetIO.encode_numpy_array, np.array.__name__,
                      MongoDataSetIO.decode_numpy_array)
        self.register(tuple, _encode_tuple, tuple.__name__, _decode_tuple)

    def register(self, type_: type, encode_func: TransformFunction, type_name: str,
                 decode_func: TransformFunction) -> None:
        """ Registers an encoder and decoder for a given type

        Args:
            type_: The type to encode
            encode_func: The transform function for encoding that type
            type_name: The type name to decode
            decode_func: The transform function for decoding
        """

        self.encoder.encoders[type_] = encode_func
        self.decoder.decoders[type_name] = decode_func

    def serialize(self, data: Any) -> str:
        """ Serializes a Python object to JSON

        Args:
            data: Any Python object

        Returns:
            JSON encoded string
        """

        return self.encoder.encode(self.transform_data(data))

    def unserialize(self, data: str) -> Any:
        """ Unserializes a JSON string to a Python object

        Args:
            data: The JSON encoded string

        Returns:
            A Python object decoded from the JSON string
        """

        return self.decoder.decode(data)

    def transform_data(self, data: Any) -> Any:
        """ Recursively transfer a Python object and apply transform functions to it

        Args:
            data: Any Python object that can be handled by an encode/transform function for that type

        Returns:
            The transformed data
        """

        if isinstance(data, dict):
            new = {}
            for key, value in data.items():
                if isinstance(value, dict):
                    new[key] = self.transform_data(value)
                else:
                    new[key] = self._transform(value)

            return new

        elif isinstance(data, list):
            new = []
            for item in data:
                new.append(self.transform_data(self._transform(item)))

            return new

        return self._transform(data)

    def _transform(self, data):
        type_ = type(data)
        if type_ in self.encoder.encoders:
            return self.encoder.encoders[type_](data)

        return data


def serialize(data: Any) -> str:
    """ Serializes a Python object to JSON using the default serializer

    Args:
        data: Any Python object
    Returns:
        JSON encoded string
    """

    return serializer.serialize(data)


def unserialize(data: str) -> Any:
    """ Unserializes a JSON string to a Python object using the default serializer

    Args:
        data: The JSON encoded string
    Returns:
        A Python object decoded from the JSON string
    """

    return serializer.unserialize(data)


# The default Serializer to use
serializer = Serializer()
