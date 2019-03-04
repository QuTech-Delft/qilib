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

import queue
from unittest import TestCase
from unittest.mock import MagicMock, patch

import numpy as np

from qilib.data_set import DataArray, DataSet, MemoryDataSetIO
from qilib.utils import PythonJsonStructure


class TestDataSetIO(TestCase):

    def test_bind_data_set_is_already_called(self):
        memory_io = MemoryDataSetIO()
        dataset = MagicMock()
        other_dataset = MagicMock()
        memory_io.bind_data_set(dataset)
        with self.assertRaisesRegex(AttributeError, 'DataSet already bound!'):
            memory_io.bind_data_set(other_dataset)

    def test_not_bounded_other_functions(self):
        memory_io = MemoryDataSetIO()
        error_args = (ValueError, 'No DataSet bound to MemoryDataSetIO!')
        self.assertRaisesRegex(*error_args, memory_io.sync_from_storage, timeout=1234)
        self.assertRaisesRegex(*error_args, memory_io.sync_data_to_storage, data_array=None, index_or_slice=1234)
        self.assertRaisesRegex(*error_args, memory_io.sync_metadata_to_storage, field_name='test', value='abc')
        self.assertRaisesRegex(*error_args, memory_io.sync_add_data_array_to_storage, data_array=None)
        self.assertRaisesRegex(*error_args, memory_io.finalize)

    def test_sync_data_to_storage(self):
        data_set = DataSet()

        memory_io = MemoryDataSetIO()
        memory_io.bind_data_set(data_set)

        some_array = DataArray('some_array', 'label', shape=(5, 5))
        memory_io.sync_add_data_array_to_storage(some_array)

        value_0 = 1234
        some_array[0] = value_0
        value_1 = 4321
        some_array[1] = value_1
        memory_io.sync_data_to_storage(some_array, (4, 1))
        memory_io.sync_from_storage(-1)

        actual_array = memory_io.data_set.data_arrays['some_array']
        self.assertEqual(some_array, actual_array)

    def test_sync_data_to_storage_raises_value_error(self):
        data_set = DataSet()

        memory_io = MemoryDataSetIO()
        memory_io.bind_data_set(data_set)

        some_array = DataArray('some_array', 'label', shape=(5, 5))
        other_array = DataArray('other_array', 'label', shape=(5, 5))
        memory_io.sync_add_data_array_to_storage(some_array)

        error_args = (ValueError, 'The DataArray is not present and cannot be updated!')
        self.assertRaisesRegex(*error_args, memory_io.sync_data_to_storage, data_array=other_array, index_or_slice=(4, 1))

    def test_sync_metadata_to_storage_all_present(self):
        initial_user_data = PythonJsonStructure(item_0=0, item_1=1)
        data_set = DataSet(user_data=initial_user_data)

        memory_io = MemoryDataSetIO()
        memory_io.bind_data_set(data_set)
        self.assertEqual(data_set, memory_io.data_set)

        user_items = {'item_{0}'.format(i): i for i in range(2, 101)}
        other_user_data = PythonJsonStructure(user_items)
        for key, value in other_user_data.items():
            memory_io.sync_metadata_to_storage(key, value)

        memory_io.sync_from_storage(timeout=-1)
        actual_user_data = memory_io.data_set.user_data

        expected_user_data = PythonJsonStructure(initial_user_data, other_user_data)
        self.assertDictEqual(expected_user_data, actual_user_data)

    def test_sync_metadata_to_storage_is_blocking(self):
        initial_user_data = PythonJsonStructure(item_0=0, item_1=1)
        data_set = DataSet(user_data=initial_user_data)

        memory_io = MemoryDataSetIO()
        memory_io.bind_data_set(data_set)
        self.assertEqual(data_set, memory_io.data_set)

        expected = PythonJsonStructure(item_0=2, item_1=3)
        for key, value in expected.items():
            memory_io.sync_metadata_to_storage(key, value)

        memory_io.sync_from_storage(timeout=-1)
        self.assertDictEqual(expected, memory_io.data_set.user_data)

    def test_sync_metadata_to_storage_non_blocking(self):
        initial_user_data = PythonJsonStructure(item_0=0, item_1=1)
        data_set = DataSet(user_data=initial_user_data)

        memory_io = MemoryDataSetIO()
        memory_io.bind_data_set(data_set)
        self.assertEqual(data_set, memory_io.data_set)

        user_items = {'item_{0}'.format(i): i for i in range(2, 101)}
        other_user_data = PythonJsonStructure(user_items)
        for key, value in other_user_data.items():
            memory_io.sync_metadata_to_storage(key, value)

        timeout = 0
        memory_io.sync_from_storage(timeout)
        actual_user_data = memory_io.data_set.user_data

        expected_user_data = PythonJsonStructure(initial_user_data, other_user_data)
        self.assertDictEqual(expected_user_data, actual_user_data)

    def test_sync_metadata_to_storage_with_timeout(self):
        initial_user_data = PythonJsonStructure(item_0=0, item_1=1)
        data_set = DataSet(user_data=initial_user_data)

        memory_io = MemoryDataSetIO()
        memory_io.bind_data_set(data_set)
        self.assertEqual(data_set, memory_io.data_set)

        user_items = {'item_{0}'.format(i): i for i in range(2, 101)}
        other_user_data = PythonJsonStructure(user_items)
        for key, value in other_user_data.items():
            memory_io.sync_metadata_to_storage(key, value)

        timeout = 2
        memory_io.sync_from_storage(timeout)
        actual_user_data = memory_io.data_set.user_data

        expected_user_data = PythonJsonStructure(initial_user_data, other_user_data)
        self.assertDictEqual(expected_user_data, actual_user_data)

    def test_sync_data_arrays_to_storage_is_empty_not_updated(self):
        with patch('qilib.data_set.memory_data_set_io.queue.Queue') as queue_mock:
            data_set = DataSet()
            queue_mock.return_value.get.side_effect = queue.Empty
            queue_mock.return_value.empty.side_effect = [True, False]

            memory_io = MemoryDataSetIO()
            memory_io.bind_data_set(data_set)
            self.assertEqual(data_set, memory_io.data_set)

            some_array = DataArray('some_array', 'label', shape=(5, 5))
            memory_io.sync_add_data_array_to_storage(some_array)

            memory_io.sync_from_storage(timeout=-1)
            self.assertEqual(data_set, memory_io.data_set)

    def test_sync_metadata_to_storage_is_empty_not_updated(self):
        with patch('qilib.data_set.memory_data_set_io.queue.Queue') as queue_mock:
            user_data = PythonJsonStructure(item_0=0, item_1=1)
            data_set = DataSet(user_data=user_data)

            queue_mock.return_value.get.side_effect = queue.Empty
            queue_mock.return_value.empty.return_value = False

            memory_io = MemoryDataSetIO()
            memory_io.bind_data_set(data_set)
            self.assertEqual(data_set, memory_io.data_set)

            user_item = 'item_2'
            memory_io.sync_metadata_to_storage(user_item, 2)

            memory_io.sync_from_storage(timeout=-1)
            self.assertEqual(data_set, memory_io.data_set)

    def test_sync_data_array_to_storage_is_added(self):
        array_name = 'ItsAnArray'
        set_arrays = DataArray('setpoints', 'X', is_setpoint=True, preset_data=np.array([1, 2, 3, 4, 5]))
        data_arrays = DataArray(array_name, 'results', shape=(5,), set_arrays=[set_arrays])
        data_set = DataSet(data_arrays=data_arrays)

        memory_io = MemoryDataSetIO()
        memory_io.bind_data_set(data_set)
        self.assertEqual(data_set, memory_io.data_set)

        name = 'test'
        other_data_array = DataArray(name, 'Y', shape=(5,), set_arrays=[set_arrays])
        memory_io.sync_add_data_array_to_storage(other_data_array)

        memory_io.sync_from_storage(-1)
        self.assertEqual(memory_io.data_set.data_arrays[name], other_data_array)

    def test_finalize_is_done(self):

        class MemoryDataSetIOWithFinalize(MemoryDataSetIO):

            @property
            def is_finalized(self):
                return self._is_finalized

            @staticmethod
            def load():
                raise NotImplementedError()

        memory_io = MemoryDataSetIOWithFinalize()
        memory_io.bind_data_set(data_set=MagicMock())
        self.assertFalse(memory_io.is_finalized)
        memory_io.finalize()
        self.assertTrue(memory_io.is_finalized)

    def test_finalize_is_already_finalized(self):
        memory_io = MemoryDataSetIO()
        memory_io.bind_data_set(data_set=MagicMock())
        memory_io.finalize()
        error_args = (AttributeError, 'MemoryDataSetIO already finalized!')
        self.assertRaisesRegex(*error_args, memory_io.finalize)

    def test_finalize_is_already_finalized_other_functions(self):
        memory_io = MemoryDataSetIO()
        memory_io.bind_data_set(data_set=MagicMock())
        memory_io.finalize()
        error_args = (AttributeError, 'MemoryDataSetIO already finalized!')
        self.assertRaisesRegex(*error_args, memory_io.sync_data_to_storage, data_array=None, index_or_slice=1234)
        self.assertRaisesRegex(*error_args, memory_io.sync_metadata_to_storage, field_name='abc', value=123)
        self.assertRaisesRegex(*error_args, memory_io.sync_add_data_array_to_storage, data_array=None)

    def test_load_is_not_implemented(self):
        error_args = (NotImplementedError, 'The load function cannot be used with the MemoryDataSetIO!')
        self.assertRaisesRegex(*error_args, MemoryDataSetIO.load)
