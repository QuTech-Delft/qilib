import unittest
from unittest.mock import MagicMock

from qilib.data_set import DataSet, DataArray
from qilib.data_set.memory_data_set_io_reader import MemoryDataSetIOReader
from qilib.utils.memory_storage_queue import MemoryStorageQueue


class TestMemoryDataSetIOReader(unittest.TestCase):
    def test_sync_from_storage(self):
        self._test_sync_from_storage(-1)

    def test_load_is_not_implemented(self):
        error_args = (NotImplementedError, 'The load function cannot be used with the MemoryDataSetIOReader!')
        self.assertRaisesRegex(*error_args, MemoryDataSetIOReader.load)

    def test_sync_from_storage_with_timeout(self):
        self._test_sync_from_storage(0.01)

    def test_read_from_empty_queue_timeout(self):
        timeout = 0.001
        queue = MemoryStorageQueue()
        data_set_io_reader = MemoryDataSetIOReader(queue)
        data_set = MagicMock(spec=DataSet)
        data_set_io_reader.bind_data_set(data_set)
        error_args = (TimeoutError, '')
        self.assertRaisesRegex(*error_args, data_set_io_reader.sync_from_storage, timeout)

    def test_sync_from_storage_none_blocking(self):
        self._test_sync_from_storage(0)

    def test_read_from_empty_queue(self):
        timeout = 0
        queue = MemoryStorageQueue()
        data_set_io_reader = MemoryDataSetIOReader(queue)
        data_set = MagicMock(spec=DataSet)
        data_set_io_reader.bind_data_set(data_set)

        data_set_io_reader.sync_from_storage(timeout)
        data_set.add_array.assert_not_called()
        data_set.add_data.assert_not_called()

    def _test_sync_from_storage(self, timeout):
        queue = MemoryStorageQueue()
        data_set_io_reader = MemoryDataSetIOReader(queue)
        data_set = MagicMock(spec=DataSet)
        data_set_io_reader.bind_data_set(data_set)
        data_array = DataArray(name='bla', label='blu', shape=(2, 2))
        queue.add_array(data_array)
        queue.add_data(4, {'z': [42]})
        queue.add_meta_data('name', 'bob')
        data_set_io_reader.sync_from_storage(timeout)

        self.assertEqual('bob', data_set.name)
        data_set.add_data.assert_called_once_with(4, {'z': [42]})
        data_set.add_array.assert_called_once_with(data_array)
