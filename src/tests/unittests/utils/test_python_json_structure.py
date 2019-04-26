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
from functools import partial

import numpy as np

from qilib.utils import PythonJsonStructure
from qilib.utils.serialization import serialize, unserialize


class TestPythonJsonStructure(unittest.TestCase):

    def setUp(self):
        key_error_msg = "Invalid key"
        data_error_msg = "Data is not serializable"
        self.assert_raises_invalid_key = partial(self.assertRaisesRegex, TypeError, key_error_msg)
        self.assert_raises_invalid_data = partial(self.assertRaisesRegex, TypeError, data_error_msg)

    def test_init_invalid_arguments(self):
        with self.assert_raises_invalid_data():
            PythonJsonStructure(a=object())

    def test_init_valid_arguments(self):
        data = {'a': 1, 'b': 2}
        json_object_1 = PythonJsonStructure(data)
        json_object_2 = PythonJsonStructure(json_object_1)
        self.assertDictEqual(json_object_1, json_object_2)

    def test_dict_instance(self):
        json_object = PythonJsonStructure()
        self.assertIsInstance(json_object, dict)

    def test_setitem_invalid_argument(self):
        json_object = PythonJsonStructure()
        with self.assert_raises_invalid_data():
            json_object['a'] = object()

    def test_setitem_valid_arguments(self):
        settable_objects = {
            'none': None,
            'bool': False,
            'int': 25,
            'float': 3.141592,
            'list': [1, 2, 3],
            'str': 'some_string',
            'bytes': b'1010101',
            'tuple': (1, 2, 3),
            'dict': {'a': 1, 'b': 2, 'c': 3},
            'ndarray': np.array([[1, 2], [3, 4, 5]]),
            'json_object': PythonJsonStructure()
        }

        json_object = PythonJsonStructure()
        for key, expected in settable_objects.items():
            json_object[key] = expected
            np.testing.assert_array_equal(expected, json_object[key])

    def test_update_valid_data(self):
        json_object = PythonJsonStructure()
        expected = {'a': 1, 'b': 2}
        json_object.update(expected)
        self.assertDictEqual(expected, json_object)

        json_object = PythonJsonStructure()
        expected = {'c': 3, 'd': 4}
        json_object.update(c=3, d=4)
        self.assertDictEqual(expected, json_object)

    def test_update_invalid_data(self):
        json_object = PythonJsonStructure()
        args_data = {'a': 1, 'b': object()}
        kwargs_data = {'c': 3, 'd': object()}
        self.assert_raises_invalid_data(json_object.update, args_data)
        self.assert_raises_invalid_data(json_object.update, **kwargs_data)
        with self.assert_raises_invalid_data():
            json_object['bla'] = [[], [], [[], [[object()]]]]

    def test_setdefault_value_not_present(self):
        key = 'test'
        json_object = PythonJsonStructure()
        return_value = json_object.setdefault(key)
        self.assertIsNone(json_object[key])
        self.assertIsNone(return_value)

    def test_setdefault_value_already_present(self):
        key = 'test'
        expected = 12
        json_object = PythonJsonStructure()
        json_object[key] = expected
        return_value = json_object.setdefault(key, 10)
        self.assertEqual(expected, json_object[key])
        self.assertEqual(expected, return_value)

    def test_setdefault_default_present(self):
        key = 'test'
        expected = 12
        json_object = PythonJsonStructure()
        return_value = json_object.setdefault(key, expected)
        self.assertEqual(expected, json_object[key])
        self.assertEqual(expected, return_value)

    def test_setdefault_dict_type(self):
        key = 'test'
        expected = {'a': 1, 'b': 2}
        json_object = PythonJsonStructure()
        return_value = json_object.setdefault(key, expected)
        self.assertEqual(expected, json_object[key])
        self.assertEqual(expected, return_value)

    def test_setdefault_container_type(self):
        key = 'test'
        containers = [
            [1, [2, 3], 2, [2, 3, [4, 5]]],
            (1, (2, 3), 8, (9, 10), (7, (1, 2))),
            np.random.rand(3, 2, 5, 1, 3),
        ]

        for expected in containers:
            json_object = PythonJsonStructure()
            return_value = json_object.setdefault(key, expected)
            np.testing.assert_equal(expected, json_object[key])
            np.testing.assert_equal(expected, return_value)

    def test_setdefault_invalid_value_type(self):
        key = 'test'
        value = object()
        json_object = PythonJsonStructure()
        self.assert_raises_invalid_data(json_object.setdefault, key, value)

    def test_setdefault_invalid_key_type(self):
        key = object()
        value = 1
        json_object = PythonJsonStructure()
        self.assert_raises_invalid_key(json_object.setdefault, key, value)

    def test_setobject_invalid_container_item(self):
        key = 'test'
        value = np.array([object()])
        json_object = PythonJsonStructure()
        self.assert_raises_invalid_data(json_object.setdefault, key, value)

    def test_length(self):
        object_a = PythonJsonStructure()
        self.assertEqual(0, len(object_a), 0)
        object_b = PythonJsonStructure({'a': 1})
        self.assertEqual(1, len(object_b))
        object_b['b'] = 2
        self.assertEqual(2, len(object_b))

    def test_recursive_update(self):
        json_object = PythonJsonStructure()
        data = {'a1': [1, 2, 3], 'b1': {'a2': 2}}
        json_object.update(data)
        with self.assert_raises_invalid_data():
            json_object['c1'] = object()
        with self.assert_raises_invalid_data():
            json_object['b1']['b2'] = object()

    def test_serialization_data_types(self):
        settable_objects = {
            'none': None,
            'bool': False,
            'int': 25,
            'float': 3.141592,
            'str': 'some_string',
            'bytes': b'1010101',
        }
        for key, expected in settable_objects.items():
            json_object = PythonJsonStructure({key: expected})
            serialized_object = serialize(json_object)
            unserialized_object = unserialize(serialized_object)
            self.assertEqual(json_object, unserialized_object)

    def test_serialization_container_types(self):
        """ Creates a PythonJsonStucture with all the data-types. Serializes the
            object and directly afterwards unserializes. The unserialized object
            should equal the original created PythonJsonStructure.

            Note:
                Currently a PythonJsonStructure with a tuple is not tested. A tuple
                object can only be serialized to a list.
        """
        settable_containers = {
            'list': [1, 2, 3],
            'dict': {'a': 1, 'b': 2, 'c': 3},
            'ndarray': np.random.rand(3, 2, 4, 5).astype(np.cfloat),
            # 'tuple': (1, 2, 3),
            'json_object': PythonJsonStructure()
        }
        for key, expected in settable_containers.items():
            json_object = PythonJsonStructure({key: expected})
            serialized_object = serialize(json_object)
            unserialized_object = unserialize(serialized_object)
            np.testing.assert_equal(json_object, unserialized_object)

    def test_storage_numpy_array(self):
        json_object = PythonJsonStructure()
        large_numpy_array = np.zeros((10000, 2000, 3))
        json_object['array'] = large_numpy_array
        self.assertIsInstance(json_object['array'], np.ndarray)

    def test_boolean_numpy_array(self):
        json_object = PythonJsonStructure()
        json_object['boolean_array'] = np.array([True, False])
        self.assertEqual(json_object['boolean_array'].dtype, bool)
