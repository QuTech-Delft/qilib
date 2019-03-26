import unittest

from qilib.data_set import DataArray
from qilib.data_set.memory_data_set_io_writer import MemoryDataSetIOWriter
from qilib.utils.memory_storage_queue import MemoryStorageQueue


class TestMemoryDataSetIOWriter(unittest.TestCase):
    def setUp(self):
        self.queue = MemoryStorageQueue()
        self.data_set_io_writer = MemoryDataSetIOWriter(self.queue)

    def test_sync_metadata_to_storage(self):
        meta_data = ('name', 'some_result')
        self.data_set_io_writer.sync_metadata_to_storage(*meta_data)
        data_type, storage_data = self.queue.get(block=False)
        self.assertEqual(data_type, self.queue.META_DATA)
        self.assertTupleEqual(meta_data, storage_data)

    def test_sync_data_to_storage(self):
        data = (4, {'some_result': 0.2})
        self.data_set_io_writer.sync_data_to_storage(*data)
        data_type, storage_data = self.queue.get(block=False)
        self.assertEqual(data_type, self.queue.DATA)
        self.assertTupleEqual(data, storage_data)

    def test_sync_add_data_array_to_storage(self):
        array = DataArray(name='stuffsi', label='V', shape=(1,1))
        array[0] = 42
        self.data_set_io_writer.sync_add_data_array_to_storage(array)

        data_type, storage_array = self.queue.get(block=False)

        self.assertEqual(42, storage_array[0])
        self.assertEqual(data_type, self.queue.ARRAY)
        self.assertEqual(array.name, storage_array.name)
        self.assertEqual(array.shape, storage_array.shape)
        self.assertEqual(array.label, storage_array.label)

    def test_finalize_is_not_implemented(self):
        error_args = (NotImplementedError, 'The finalize function cannot be used with the MemoryDataSetIOWriter!')
        self.assertRaisesRegex(*error_args, self.data_set_io_writer.finalize)

