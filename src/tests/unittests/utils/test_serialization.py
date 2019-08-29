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

import unittest
import numpy as np

from qilib.utils import PythonJsonStructure
from qilib.utils.serialization import serializer, serialize, unserialize, Encoder, Decoder


class CustomType:
    def __init__(self, x, y):
        self.x, self.y = x, y


class TestSerialization(unittest.TestCase):
    def setUp(self):
        self.testdata = [(1, 2, 3), 10, 3.14, 'string', b'bytes', {'a': 1, 'b': 2}, [1, 2], [1, [2, 3]]]
        self.testdata_arrays = [np.array([1, 2, 3]), np.array([1.0, 2.0]), np.array([[1.0, 0], [0, -.2], [0.123, .0]])]

    def test_serialization_default_types(self):
        for x in self.testdata:
            s = serialize(x)
            xx = unserialize(s)
            self.assertEqual(x, xx)
        for x in self.testdata_arrays:
            s = serialize(x)
            xx = unserialize(s)
            self.assertSequenceEqual(x.tolist(), xx.tolist())

    def test_serialization_default_types_2(self):
        for x in self.testdata:
            s = serializer.encode_data(x)
            xx = serializer.decode_data(s)
            self.assertEqual(x, xx)
        for x in self.testdata_arrays:
            s = serializer.encode_data(x)
            xx = serializer.decode_data(s)
            self.assertSequenceEqual(x.tolist(), xx.tolist())

    def test_non_serializable_objects(self):
        with self.assertRaisesRegex(TypeError, 'is not JSON serializable'):
            serialize(object())

    def test_transform_data_unknown_type(self):
        data = {'test': CustomType(13, 37)}
        transformed = serializer.encode_data(data)

        self.assertNotEqual(transformed, {'test': {'x': 13, 'y': 37}})

    def test_transform_data_with_registered_type(self):
        def dummy_transform(obj):
            return {'x': obj.x, 'y': obj.y}

        serializer.register(CustomType, dummy_transform, '', None)

        data = {'test': CustomType(13, 37)}
        transformed = serializer.encode_data(data)

        self.assertEqual(transformed, {'test': {'x': 13, 'y': 37}})

    def test_json_encode_external_type(self):
        encoder = Encoder()
        encoder.encoders[CustomType] = lambda data: (data.x, data.y)

        encoded = encoder.encode({'test': CustomType(13, 37)})
        self.assertEqual(encoded, '{"test": [13, 37]}')

    def test_json_decode_unknown_type(self):
        decoder = Decoder()
        self.assertRaises(ValueError, decoder.decode, '{"__object__": "CustomType", "__content__": [1, 2, 3]}')

    def test_serialize_non_string_keys(self):
        data = PythonJsonStructure({'a': 1, 1: 'a'})
        self.assertDictEqual(unserialize(serialize(data)), {'a': 1, '1': 'a'})

    def test_serialize_subclass(self):
        class SubClass(np.ndarray):
            pass

        data = SubClass([1, 2, 3, 4, 5])
        self.assertRaises(TypeError, serialize, data)

    def test_encode_decode_complex(self):
        data = {'results': [{'result_1': np.array([1, 2, 3, 4, 5])}]}
        new_data = serializer.decode_data(serializer.encode_data(data))
        self.assertTrue(np.array_equal(data['results'][0]['result_1'], new_data['results'][0]['result_1']))

    def test_decode_unknown_type(self):
        self.assertRaises(ValueError, serializer.decode_data, {'__object__': 'CustomType', '__content__': [1, 2, 3]})
