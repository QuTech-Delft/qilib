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

import operator
import unittest
from copy import copy

import numpy as np
from qilib.data_set import DataArray


class TestDataArray(unittest.TestCase):
    def setUp(self):
        self.x_points = np.array(range(0, 10))
        self.y_points = np.array(range(100, 105))
        self.z_points = np.array(range(200, 203))

    def test_1d_raise_error(self):
        setpoints = DataArray('x', 'setpoints', 'V', is_setpoint=True, preset_data=self.x_points)
        with self.assertRaises(ValueError) as error:
            DataArray('x_data', 'data', 'A', shape=(9,), set_arrays=[setpoints])
        self.assertEqual(("Dimensions of 'set_arrays' and 'data' do not match.",), error.exception.args)

        with self.assertRaises(ValueError) as error:
            DataArray('x_data', 'data', 'A', shape=(11,), set_arrays=[setpoints])
        self.assertEqual(("Dimensions of 'set_arrays' and 'data' do not match.",), error.exception.args)

    def test_2d_raise_error(self):
        x_setpoints = DataArray('x', 'setpoints', 'V', is_setpoint=True, preset_data=self.x_points)
        y_setpoints = DataArray('y', 'setpoints', 'V', is_setpoint=True,
                                preset_data=np.tile(np.array(self.y_points), [self.x_points.size, 1]))
        with self.assertRaises(ValueError) as error:
            DataArray('x_data', 'data', 'A', shape=(5, 10), set_arrays=[y_setpoints, x_setpoints])
        self.assertEqual(("Dimensions of 'set_arrays' and 'data' do not match.",), error.exception.args)

        with self.assertRaises(ValueError) as error:
            DataArray('x_data', 'data', 'A', shape=(9, 5), set_arrays=[x_setpoints, y_setpoints])
        self.assertEqual(("Dimensions of 'set_arrays' and 'data' do not match.",), error.exception.args)

        with self.assertRaises(ValueError) as error:
            DataArray('x_data', 'data', 'A', shape=(10, 5), set_arrays=[x_setpoints])
        self.assertEqual(("Dimensions of 'set_arrays' and 'data' do not match.",), error.exception.args)

    def test_3d_raise_error(self):
        x_setpoints = DataArray('x', 'setpoints', 'V', is_setpoint=True, preset_data=self.x_points)
        y_setpoints = DataArray('y', 'setpoints', 'V', is_setpoint=True,
                                preset_data=np.tile(np.array(self.y_points), [self.x_points.size, 1]))
        z_setpoints = DataArray('z', 'setpoints', 'V', is_setpoint=True, preset_data=np.ndarray((10, 5, 10)))

        with self.assertRaises(ValueError) as error:
            DataArray('x_data', 'data', 'A', shape=(10, 5, 9), set_arrays=[x_setpoints, y_setpoints, z_setpoints])
        self.assertEqual(("Dimensions of 'set_arrays' and 'data' do not match.",), error.exception.args)

        with self.assertRaises(ValueError) as error:
            DataArray('x_data', 'data', 'A', shape=(10, 6, 10), set_arrays=[x_setpoints, z_setpoints, y_setpoints])
        self.assertEqual(("Dimensions of 'set_arrays' and 'data' do not match.",), error.exception.args)

        with self.assertRaises(ValueError) as error:
            DataArray('x_data', 'data', 'A', shape=(10, 5, 10), set_arrays=[x_setpoints, y_setpoints])
        self.assertEqual(("Dimensions of 'set_arrays' and 'data' do not match.",), error.exception.args)

        with self.assertRaises(ValueError) as error:
            DataArray('x_data', 'data', 'A', shape=(10, 5,), set_arrays=[x_setpoints, y_setpoints, z_setpoints])
        self.assertEqual(("Dimensions of 'set_arrays' and 'data' do not match.",), error.exception.args)

    def test_array_with_float_data(self):
        preset_array = np.array([1., 2.], dtype=np.float32)
        data_array = DataArray('x', 'x', preset_data=preset_array)
        self.assertEqual(data_array._data.dtype, preset_array.dtype)
        self.assertIsInstance(data_array[0], np.float32)

    def test_1d_constructor_with_shape(self):
        setpoints = DataArray('x', 'setpoints', 'V', is_setpoint=True, preset_data=self.x_points)
        data_array = DataArray('x_data', 'data', 'A', shape=(10,), set_arrays=[setpoints])
        self.assertIs(setpoints, data_array.set_arrays[0])
        self.assertEqual('x_data', data_array.name)
        self.assertEqual('data', data_array.label)
        self.assertEqual('A', data_array.unit)
        self.assertFalse(data_array.is_setpoint)
        self.assertTrue(setpoints.is_setpoint)

    def test_wrong_set_array_with_set_array_raises_error(self):
        x_points = np.array(range(0, 10))
        y_points = np.array(range(0, 5))
        x = DataArray(name='x', label='x-axis', unit='mV', is_setpoint=True,
                      preset_data=np.array(x_points))
        with self.assertRaises(ValueError) as error:
            DataArray(name='y', label='y-axis', unit='mV', is_setpoint=True,
                      set_arrays=[x,], preset_data=np.tile(np.array(y_points), [x.size + 1, 1]))
        self.assertEqual(("Dimensions of 'set_arrays' do not match.",), error.exception.args)

    def test_2d_set_array_with_set_array(self):
        x_points = np.array(range(0, 10))
        y_points = np.array(range(0, 5))

        x = DataArray(name='x', label='x-axis', unit='mV', is_setpoint=True,
                      preset_data=np.array(x_points))
        self.assertEqual('x', x.name)
        self.assertEqual('x-axis', x.label)
        self.assertEqual('mV', x.unit)
        self.assertTrue(x.is_setpoint)
        self.assertListEqual(list(x_points), list(x))

        y = DataArray(name='y', label='y-axis', unit='mV', is_setpoint=True,
                      set_arrays=[x,], preset_data=np.tile(np.array(y_points), [x.size, 1]))
        self.assertEqual('y', y.name)
        self.assertEqual('y-axis', y.label)
        self.assertEqual('mV', y.unit)
        self.assertTrue(y.is_setpoint)
        self.assertIs(x, y.set_arrays[0])

        z = DataArray(name='z', label='z-axis', unit='ma', set_arrays=[x, y],
                      preset_data=np.NaN * np.ones((x_points.size, y_points.size)))
        self.assertEqual('z', z.name)
        self.assertEqual('z-axis', z.label)
        self.assertEqual('ma', z.unit)
        self.assertFalse(z.is_setpoint)
        self.assertIs(x, z.set_arrays[0])
        self.assertIs(y, z.set_arrays[1])

    def test_2d_set_array_with_set_array_out_of_order(self):
        x_points = np.array(range(0, 10))
        y_points = np.array(range(0, 5))

        x = DataArray(name='x', label='x-axis', unit='mV', is_setpoint=True,
                      preset_data=np.array(x_points))
        y = DataArray(name='y', label='y-axis', unit='mV', is_setpoint=True,
                      set_arrays=[x,], preset_data=np.tile(np.array(y_points), [x.size, 1]))
        z = DataArray(name='z', label='z-axis', unit='ma', set_arrays=[y, x],
                      preset_data=np.NaN * np.ones((x_points.size, y_points.size)))
        self.assertEqual('z', z.name)
        self.assertEqual('z-axis', z.label)
        self.assertEqual('ma', z.unit)
        self.assertFalse(z.is_setpoint)
        self.assertIs(x, z.set_arrays[1])
        self.assertIs(y, z.set_arrays[0])

    def test_type_error(self):
        with self.assertRaises(TypeError) as error:
            DataArray('name', 'label')
        self.assertEqual(("Required arguments 'shape' or 'preset_data' not found",), error.exception.args)

    def test_constructor_with_preset_data(self):
        setpoints = DataArray('x', 'setpoints', 'V', is_setpoint=True, preset_data=self.x_points)
        data_array = DataArray('x_data', 'data', 'A', preset_data=self.x_points, set_arrays=[setpoints])
        self.assertIs(setpoints, data_array.set_arrays[0])

    def test_dir(self):
        np_array = np.ndarray((1, 2))
        np_dir = dir(np_array)
        data_array = DataArray('x', 'setpoints', 'V', is_setpoint=True, shape=(1, 2))
        data_array_dir = dir(data_array)
        self.assertLess(data_array_dir, np_dir)
        for value in np_dir:
            self.assertIn(value, data_array_dir)

    def test_str(self):
        preset_data = np.ndarray((3,), buffer=np.array([1, 2, 3]), dtype=int)
        set_array = DataArray('x', 'setpoints', 'V', is_setpoint=True, preset_data=preset_data)
        data_array = DataArray('x', 'setpoints', 'V', set_arrays=[set_array], preset_data=np.ones((3,)))
        expected_string = "DataArray (3,): x\ndata: [1. 1. 1.]\nset_arrays:['x']"
        self.assertEqual(expected_string, data_array.__str__())

    def test_repr(self):
        preset_data = np.ndarray((3,), buffer=np.array([1, 2, 3]), dtype=int)
        set_array = DataArray('x', 'setpoints', 'V', is_setpoint=True, preset_data=preset_data)
        data_array = DataArray('x', 'setpoints', 'V', set_arrays=[set_array], preset_data=np.ones((3,)))
        expected_string = "DataArray(id={}, name='x', label='setpoints', unit='V', is_setpoint=False, " \
                          "data=array([1., 1., 1.]), set_arrays=[DataArray(id={}, name='x', label='setpoints', " \
                          "unit='V', is_setpoint=True, data=array([1, 2, 3]), " \
                          "set_arrays=[])])".format(id(data_array), id(data_array.set_arrays[0]))
        self.assertEqual(expected_string, data_array.__repr__())

    def test_attribute_error(self):
        data_array = DataArray('x', 'setpoints', 'V', is_setpoint=True, shape=(5,))
        with self.assertRaises(AttributeError) as error:
            data_array.update()
        self.assertEqual(("DataArray has no attribute 'update'",), error.exception.args)

    def test_indexing_support(self):
        preset_data = np.array(range(10))
        data_array = DataArray('name', 'label', preset_data=preset_data.copy())
        self.assertEqual(preset_data[0], data_array[0])
        for i in range(10):
            data_array[i] = i + 10
        for i in range(10, 20):
            self.assertEqual(i, data_array[i - 10])

    def _test_binary_operation(self, op, rhs):
        np_array = np.array(range(10))
        data_array = DataArray(name='x', label='x-axis', unit='mV', is_setpoint=True, preset_data=np_array)
        self.assertListEqual(list(np_array), list(data_array))
        expected_result = op(np_array, rhs)
        result = op(data_array, rhs)
        self.assertListEqual(list(expected_result), list(result))

    def test_multiplication(self):
        self._test_binary_operation(operator.mul, 20)
        self._test_binary_operation(operator.imul, 20)

    def test_matmul(self):
        np_array = np.array(range(10))
        data_array = DataArray(name='x', label='x-axis', unit='mV', is_setpoint=True, preset_data=np_array.copy())
        self.assertListEqual(list(np_array), list(data_array))
        expected_result = np_array @ np_array
        result = data_array @ data_array
        self.assertEqual(expected_result, result)

    def test_pow(self):
        self._test_binary_operation(operator.pow, 2)
        self._test_binary_operation(operator.ipow, 2)

    def test_addition(self):
        self._test_binary_operation(operator.add, 20)
        self._test_binary_operation(operator.iadd, 20)

    def test_subtraction(self):
        self._test_binary_operation(operator.sub, 20)
        self._test_binary_operation(operator.isub, 20)

    def test_division(self):
        self._test_binary_operation(operator.truediv, 2)

    def test_division_floor(self):
        self._test_binary_operation(operator.floordiv, 2)
        self._test_binary_operation(operator.ifloordiv, 2)

    def test_modulus(self):
        self._test_binary_operation(operator.mod, 2)
        self._test_binary_operation(operator.imod, 2)

    def test_lshift(self):
        self._test_binary_operation(operator.lshift, 2)
        self._test_binary_operation(operator.ilshift, 2)

    def test_rshift(self):
        self._test_binary_operation(operator.rshift, 2)
        self._test_binary_operation(operator.irshift, 2)

    def test_and(self):
        self._test_binary_operation(operator.and_, 2)
        self._test_binary_operation(operator.iand, 2)

    def test_or(self):
        self._test_binary_operation(operator.or_, 2)
        self._test_binary_operation(operator.ior, 2)

    def test_xor(self):
        self._test_binary_operation(operator.xor, 2)
        self._test_binary_operation(operator.ixor, 2)

    def test_properties(self):
        data_array = DataArray(name='x', label='x-axis', unit='mV', shape=(5, 5))
        self.assertEqual('x', data_array.name)
        self.assertEqual('x-axis', data_array.label)
        self.assertEqual('mV', data_array.unit)

        data_array.name = 'y'
        self.assertEqual('y', data_array.name)
        data_array.label = 'y-axis'
        self.assertEqual('y-axis', data_array.label)
        data_array.unit = 'Hz'
        self.assertEqual('Hz', data_array.unit)

    def test_array_interface(self):
        data_array = DataArray(name='x', label='x-axis', unit='mV', shape=(5, 5))

        array_interface = data_array.__array_interface__
        self.assertIn('data', array_interface)
        self.assertIn('strides', array_interface)
        self.assertIn('descr', array_interface)
        self.assertIn('typestr', array_interface)
        self.assertIn('shape', array_interface)
        self.assertIn('version', array_interface)
        self.assertTupleEqual((5, 5), array_interface['shape'])
        self.assertTupleEqual((5, 5), data_array.shape)

        data_np_array = DataArray(name='np', label='test', preset_data=np.array([5, 6, 3, 7, 2, 1, 4]))
        mean = np.mean(data_np_array)
        self.assertEqual(4, mean)
        data_np_array.sort()
        self.assertListEqual([1, 2, 3, 4, 5, 6, 7], list(data_np_array))

        np_data_array = np.array(data_np_array)
        self.assertListEqual(list(data_np_array), list(np_data_array))

    def test_copy(self):
        data_array = DataArray(name='x', label='x-axis', unit='mV', shape=(5, 5))
        copied_array = copy(data_array)

        self.assertEqual(len(data_array), len(copied_array))
        self.assertEqual(data_array.label, copied_array.label)
        self.assertEqual(data_array.name, copied_array.name)
        self.assertEqual(data_array.unit, copied_array.unit)
        self.assertIsNot(copied_array, data_array)
