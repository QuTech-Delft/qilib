from unittest import TestCase
from unittest.mock import MagicMock

import numpy as np

from qilib.data_set import DataArray, DataSet, MemoryDataSetIO
from qilib.utils import PythonJsonStructure


class TestDataSetIO(TestCase):

    def test_bind_data_set_is_already_called(self):
        memory_io = MemoryDataSetIO()
        dataset = MagicMock()
        other_dataset = MagicMock()
        memory_io.bind_data_set(dataset)
        with self.assertRaisesRegex(AttributeError, 'Dataset already bound!'):
            memory_io.bind_data_set(other_dataset)

    def test_not_bounded_other_functions(self):
        memory_io = MemoryDataSetIO()
        error_args = (ValueError, 'No dataset bound to MemoryDataSetIO!')
        self.assertRaisesRegex(*error_args, memory_io.sync_from_storage, timeout=1234)
        self.assertRaisesRegex(*error_args, memory_io.sync_data_to_storage, data_array=None, index_spec=1234)
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

    def test_sync_metadata_to_storage_all_present(self):
        user_data = PythonJsonStructure(item_0=0, item_1=1)
        data_set = DataSet(user_data=user_data)

        memory_io = MemoryDataSetIO()
        memory_io.bind_data_set(data_set)
        self.assertEqual(data_set, memory_io.data_set)

        user_items = {'item_{0}'.format(i): i for i in range(2, 101)}
        other_user_data = PythonJsonStructure(user_items)
        for key, value in other_user_data.items():
            memory_io.sync_metadata_to_storage(key, value)

        memory_io.sync_from_storage(timeout=-1)
        actual_user_data = memory_io.data_set.user_data

        self.assertTrue(user_data.items() <= actual_user_data.items())
        self.assertTrue(other_user_data.items() <= actual_user_data.items())

    def test_sync_metadata_to_storage_is_overwritten(self):
        user_data = PythonJsonStructure(item_0=0, item_1=1)
        data_set = DataSet(user_data=user_data)

        memory_io = MemoryDataSetIO()
        memory_io.bind_data_set(data_set)
        self.assertEqual(data_set, memory_io.data_set)

        expected = PythonJsonStructure(item_0=2, item_1=3)
        for key, value in expected.items():
            memory_io.sync_metadata_to_storage(key, value)

        memory_io.sync_from_storage(timeout=-1)
        self.assertDictEqual(expected, memory_io.data_set.user_data)

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
        self.assertRaisesRegex(*error_args, memory_io.sync_data_to_storage, data_array=None, index_spec=1234)
        self.assertRaisesRegex(*error_args, memory_io.sync_metadata_to_storage, field_name='abc', value=123)
        self.assertRaisesRegex(*error_args, memory_io.sync_add_data_array_to_storage, data_array=None)

    def test_load_is_not_implemented(self):
        error_args = (NotImplementedError, 'The load function cannot be used with the MemoryDataSetIO!')
        self.assertRaisesRegex(*error_args, MemoryDataSetIO.load)
