import unittest
from queue import Queue
from unittest.mock import MagicMock

from qilib.data_set import DataSet
from qilib.data_set.memory_data_set_io_reader import MemoryDataSetIOReader
from qilib.utils.memory_storage_queue import MemoryStorageQueue


class TestMemoryDataSetIOReader(unittest.TestCase):
    def test_sync_from_storage(self):
        queue = MemoryStorageQueue()
        data_set_io_reader = MemoryDataSetIOReader(queue)
        data_set = MagicMock(spec=DataSet)
        data_set_io_reader.bind_data_set(data_set)

        queue.add_array([1, 2, 3])
        queue.add_data(4, {'z': [42]})
        queue.add_meta_data('name', 'bob')
        data_set_io_reader.sync_from_storage(-1)

        self.assertEqual('bob', data_set.name)
        data_set.add_data.assert_called_once_with(4, {'z': [42]})
        data_set.add_array.assert_called_once_with([1, 2, 3])

    def test_load_is_not_implemented(self):
        error_args = (NotImplementedError, 'The load function cannot be used with the MemoryDataSetIOReader!')
        self.assertRaisesRegex(*error_args, MemoryDataSetIOReader.load)
