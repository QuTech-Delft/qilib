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
import base64
from functools import partial
from json import JSONDecoder, JSONEncoder
from typing import Any, Callable, ClassVar, Dict

import numpy as np

from qilib.data_set import MongoDataSetIO

# A callable type for transforming a given argument with a type to another type
TransformFunction = Callable[[Any], Any]


class JsonSerializeKey:
    """ The custom value types for the JSON serializer """
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
        self.decoders: ClassVar[Dict[str, TransformFunction]] = {}

    def _object_hook(self, obj):
        if isinstance(obj, dict):
            if JsonSerializeKey.OBJECT in obj:
                if obj[JsonSerializeKey.OBJECT] in self.decoders:
                    return self.decoders[obj[JsonSerializeKey.OBJECT]](obj)
                else:
                    raise ValueError(f'object key {obj[JsonSerializeKey.OBJECT]} not in decoders')

        return obj


def _encode_bytes(data: Any) -> Dict[str, Any]:
    return {JsonSerializeKey.OBJECT: bytes.__name__, JsonSerializeKey.CONTENT: data.decode('utf-8')}


def _decode_bytes(data: Dict[str, Any]) -> bytes:
    return data[JsonSerializeKey.CONTENT].encode('utf-8')


def _encode_tuple(item):
    return {
        JsonSerializeKey.OBJECT: tuple.__name__,
        JsonSerializeKey.CONTENT: [serializer.encode_data(value) for value in item]
    }


def _decode_tuple(data: Dict[str, Any]) -> tuple:
    return tuple(data[JsonSerializeKey.CONTENT])


def _encode_numpy_number(item):
    return {
        JsonSerializeKey.OBJECT: '__npnumber__',
        JsonSerializeKey.CONTENT: {
            '__npnumber__': base64.b64encode(item.tobytes()).decode('ascii'),
            '__data_type__': item.dtype.str,
        }
    }


def _decode_numpy_number(item):
    obj = item[JsonSerializeKey.CONTENT]
    return np.frombuffer(base64.b64decode(obj['__npnumber__']), dtype=np.dtype(obj['__data_type__']))[0]


def _encode_dataclass(object_: Any, class_name: str) -> Dict[str, Any]:
    """ Encodes a JSON dataclass object

    Args:
        object_: Object to be encoded
        class_name: Object dataclass name

    Returns:
        Dictionary that can be serialized
    """
    return {JsonSerializeKey.OBJECT: class_name,
            JsonSerializeKey.CONTENT: object_.to_dict()}


def _decode_dataclass(data: Any, class_type: type) -> Any:
    """ Decodes a JSON dataclass object

    Args:
        data: Data to be decoded
        class_type: The dataclass type to decode

    Returns
        Object of specified class_type type with decoded data
    """
    return class_type.from_dict(data[JsonSerializeKey.CONTENT])


class Serializer:
    """ A general serializer to serialize data to JSON and vice versa. It allows
     extending the types with a custom encoder and decoder."""

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
        for numpy_integer_type in [np.int16, np.int32, np.int64, np.float16, np.float32, np.float64, np.bool_]:
            self.register(numpy_integer_type, _encode_numpy_number, '__npnumber__', _decode_numpy_number)

    def register(self, type_: type, encode_func: TransformFunction, type_name: str,
                 decode_func: TransformFunction) -> None:
        """ Registers an encoder and decoder for a given type

        An encode function is expected to return a JSON valid type or a dictionary with the keys
        `JsonSerializeKey.OBJECT` (the name of the type) and `JsonSerializeKey.CONTENT` (the JSON valid encoded content)

        Args:
            type_: The type to encode
            encode_func: The transform function for encoding that type
            type_name: The type name to decode
            decode_func: The transform function for decoding
        """

        self.encoder.encoders[type_] = encode_func
        self.decoder.decoders[type_name] = decode_func

    def register_dataclass(self, type_: type) -> None:
        """ Registers an encoder and decoder for a dataclass with a given type

        Args:
            type_: The dataclass type to decode
        """

        type_name = f'_dataclass_{type_.__name__}'
        encode_function = partial(_encode_dataclass, class_name=type_name)
        decode_function = partial(_decode_dataclass, class_type=type_)
        self.register(type_, encode_function, type_name, decode_function)

    def serialize(self, data: Any) -> str:
        """ Serializes a Python object to JSON

        Args:
            data: Any Python object

        Returns:
            JSON encoded string
        """

        return self.encoder.encode(self.encode_data(data))

    def unserialize(self, data: str) -> Any:
        """ Unserializes a JSON string to a Python object

        Args:
            data: The JSON encoded string

        Returns:
            A Python object decoded from the JSON string
        """

        return self.decoder.decode(data)

    def encode_data(self, data: Any) -> Any:
        """ Recursively transform a Python object and apply transform functions to it

        Args:
            data: Any Python object that can be handled by an encode/transform function for that type

        Returns:
            The transformed data
        """

        if isinstance(data, dict):
            new_dict = {}

            for key, value in data.items():
                new_dict[key] = self.encode_data(value)

            return new_dict

        elif isinstance(data, list):
            new_list = []
            for item in data:
                new_list.append(self.encode_data(self._encode(item)))

            return new_list

        return self._encode(data)

    def _encode(self, data: Any) -> Any:
        type_ = type(data)
        if type_ in self.encoder.encoders:
            return self.encoder.encoders[type_](data)

        return data

    def decode_data(self, data: Any) -> Any:
        """ Recursively transform an object and apply transform functions to it

        Args:
            data: Any Python object that can be handled by an decode/transform function for that type

        Returns:
            The transformed data
        """

        if isinstance(data, dict):
            new_dict = {}
            for key, value in data.items():
                new_dict[key] = self.decode_data(value)

            return self._decode(new_dict)

        if isinstance(data, list):
            new_list = []
            for item in data:
                new_list.append(self.decode_data(item))
            return new_list

        return data

    def _decode(self, data: Any) -> Any:
        if isinstance(data, dict):
            if JsonSerializeKey.OBJECT in data:
                if data[JsonSerializeKey.OBJECT] in self.decoder.decoders:
                    return self.decoder.decoders[data[JsonSerializeKey.OBJECT]](data)
                else:
                    raise ValueError(f'object key {data[JsonSerializeKey.OBJECT]} not in decoders')

        return data


def serialize(data: Any) -> bytes:
    """ Serializes a Python object to JSON using the default serializer. Dictionary keys should be hashable.

    Args:
        data: Any Python object
    Returns:
        JSON encoded string
    """

    return serializer.serialize(data).encode('utf8')


def unserialize(data: bytes) -> Any:
    """ Unserializes a JSON string to a Python object using the default serializer

    Args:
        data: The JSON encoded string
    Returns:
        A Python object decoded from the JSON string
    """

    return serializer.unserialize(data.decode('utf8'))


# The default Serializer to use
serializer = Serializer()
