import unittest
from threading import ThreadError
from unittest.mock import patch, MagicMock

import numpy as np
from pymongo.errors import OperationFailure

from qilib.data_set import MongoDataSetIOReader, DataSet, DataArray, MongoDataSetIO


class TestMongoDataSetIOReader(unittest.TestCase):
    def test_sync_from_storage_meta_data(self):
        mock_queue = MagicMock()
        with patch('qilib.data_set.mongo_data_set_io_reader.MongoDataSetIO') as mock_io, patch(
                'qilib.data_set.mongo_data_set_io_reader.Thread') as thread, \
                patch('qilib.data_set.mongo_data_set_io_reader.Queue', return_value=mock_queue):
            reader = MongoDataSetIOReader(name='test')
            thread.assert_called_once()
            mock_io.assert_called_once_with('test', None, create_if_not_found=False, collection='data_sets',
                                            database='qilib')
            data_set = DataSet(storage_reader=reader)

            mock_queue.get.return_value = {'updateDescription': {'updatedFields': {'metadata': {'name': 'test_name'}}}}
            data_set.sync_from_storage(-1)
            self.assertEqual('test_name', data_set.name)

            mock_queue.get.return_value = {
                'updateDescription': {'updatedFields': {'metadata.default_array_name': 'some_array'}}}
            data_set.sync_from_storage(-1)
            self.assertEqual('some_array', data_set.default_array_name)

    def test_sync_from_storage_array_update(self):
        mock_queue = MagicMock()
        with patch('qilib.data_set.mongo_data_set_io_reader.MongoDataSetIO') as mock_io, patch(
                'qilib.data_set.mongo_data_set_io_reader.Thread') as thread, \
                patch('qilib.data_set.mongo_data_set_io_reader.Queue', return_value=mock_queue):
            reader = MongoDataSetIOReader(name='test')
            thread.assert_called_once()
            mock_io.assert_called_once_with('test', None, create_if_not_found=False, collection='data_sets',
                                            database='qilib')
            data_set = DataSet(storage_reader=reader)
            data_array = DataArray(name='test_array', label='lab', shape=(2, 2))
            data_set.add_array(data_array)

            mock_queue.get.return_value = {'updateDescription': {
                'updatedFields': {'array_updates': [[(0, 0), {'test_array': 42}], [(0, 1), {'test_array': 25}]]}}}
            data_set.sync_from_storage(-1)
            self.assertListEqual([42, 25], list(data_set.test_array[0]))

            mock_queue.get.return_value = {'updateDescription': {
                'updatedFields': {'array_updates.1': [(1, 1), {'test_array': 67}]}}}
            data_set.sync_from_storage(-1)
            self.assertEqual(67, data_set.test_array[1][1])

    def test_sync_from_storage_array(self):
        mock_queue = MagicMock()
        with patch('qilib.data_set.mongo_data_set_io_reader.MongoDataSetIO') as mock_io, patch(
                'qilib.data_set.mongo_data_set_io_reader.Thread') as thread, \
                patch('qilib.data_set.mongo_data_set_io_reader.Queue', return_value=mock_queue):
            mock_io.decode_numpy_array = MongoDataSetIO.decode_numpy_array
            reader = MongoDataSetIOReader(name='test')
            thread.assert_called_once()
            mock_io.assert_called_once_with('test', None, create_if_not_found=False, collection='data_sets',
                                            database='qilib')
            data_set = DataSet(storage_reader=reader)
            set_array = DataArray(name='setter', label='for_testing', is_setpoint=True,
                                  preset_data=np.array(range(0, 2)))
            set_array[0] = 42
            set_array[1] = 25
            data_array = DataArray(name='test_array', label='lab', unit='V', is_setpoint=False, set_arrays=[set_array],
                                   shape=(2,))

            update_data = {"data_arrays": {"setter": {
                "name": set_array.name,
                "label": set_array.label,
                "unit": set_array.unit,
                "is_setpoint": set_array.is_setpoint,
                "set_arrays": [array.name for array in set_array.set_arrays],
                "preset_data": MongoDataSetIO.encode_numpy_array(set_array)}}}
            mock_queue.get.return_value = {'updateDescription': {'updatedFields': update_data}}
            data_set.sync_from_storage(-1)
            update_data = {"data_arrays.test_array": {
                "name": data_array.name,
                "label": data_array.label,
                "unit": data_array.unit,
                "is_setpoint": data_array.is_setpoint,
                "set_arrays": [array.name for array in data_array.set_arrays],
                "preset_data": MongoDataSetIO.encode_numpy_array(data_array)}}

            mock_queue.get.return_value = {'updateDescription': {'updatedFields': update_data}}
            data_set.sync_from_storage(-1)
            self.assertEqual('test_array', data_set.test_array.name)
            self.assertEqual('lab', data_set.test_array.label)
            self.assertEqual('V', data_set.test_array.unit)
            self.assertFalse(data_set.test_array.is_setpoint)
            self.assertEqual('setter', data_array.set_arrays[0].name)
            self.assertListEqual([42, 25], list(data_array.set_arrays[0]))

            data_array[0] = 255
            update_data["data_arrays.test_array"]["preset_data"] = MongoDataSetIO.encode_numpy_array(data_array)
            data_set.sync_from_storage(-1)

            self.assertEqual(255, data_set.test_array[0])

    def test_sync_from_storage_error_on_queue(self):
        mock_queue = MagicMock()
        with patch('qilib.data_set.mongo_data_set_io_reader.MongoDataSetIO') as mock_io, patch(
                'qilib.data_set.mongo_data_set_io_reader.Thread') as thread, \
                patch('qilib.data_set.mongo_data_set_io_reader.Queue', return_value=mock_queue):
            reader = MongoDataSetIOReader(name='test')
            thread.assert_called_once()
            mock_io.assert_called_once_with('test', None, create_if_not_found=False, collection='data_sets',
                                            database='qilib')

            mock_queue.get.return_value = {'thread_error': OperationFailure('Error')}
            error = ThreadError, 'Watcher thread has stopped unexpectedly.'
            self.assertRaisesRegex(*error, reader.sync_from_storage, -1)

    def test_sync_from_storage_array_update_timeout(self):
        with patch('qilib.data_set.mongo_data_set_io_reader.MongoDataSetIO') as mock_io, patch(
                'qilib.data_set.mongo_data_set_io_reader.Thread') as thread:
            reader = MongoDataSetIOReader(name='test')
            thread.assert_called_once()
            mock_io.assert_called_once_with('test', None, create_if_not_found=False, collection='data_sets',
                                            database='qilib')
            error = TimeoutError, ''
            self.assertRaisesRegex(*error, reader.sync_from_storage, 0.001)

    def test_bind_data_set(self):
        mock_mongo_data_set_io = MagicMock()
        with patch('qilib.data_set.mongo_data_set_io_reader.MongoDataSetIO',
                   return_value=mock_mongo_data_set_io) as mock_io, \
                patch('qilib.data_set.mongo_data_set_io_reader.Thread') as thread:
            mock_mongo_data_set_io.get_document.return_value = {'name': 'test',
                                                                'metadata': {'default_array_name': 'array'}}
            reader = MongoDataSetIOReader(name='test')
            thread.assert_called_once()
            mock_io.assert_called_once_with('test', None, create_if_not_found=False, collection='data_sets',
                                            database='qilib')
            data_set = DataSet()
            reader.bind_data_set(data_set)
            self.assertEqual('test', data_set.name)
            self.assertEqual('array', data_set.default_array_name)

    def test_load(self):
        with patch('qilib.data_set.mongo_data_set_io_reader.MongoDataSetIO') as mock_io, \
                patch('qilib.data_set.mongo_data_set_io_reader.Thread') as thread:
            data_set = MongoDataSetIOReader.load('test', '0x2A')
            thread.assert_called_once()
            mock_io.assert_called_once_with('test', '0x2A', create_if_not_found=False, collection='data_sets',
                                            database='qilib')
            self.assertIsInstance(data_set.storage, MongoDataSetIOReader)

    def test_thread_and_queue(self):
        mock_queue_instance = MagicMock()
        with patch('qilib.data_set.mongo_data_set_io_reader.MongoDataSetIO'), patch(
                'qilib.data_set.mongo_data_set_io_reader.Thread') as mock_thread, \
                patch('qilib.data_set.mongo_data_set_io_reader.Queue', return_value=mock_queue_instance):

            def work(target, args):
                target(*args)
                return mock_thread

            mock_thread.side_effect = work
            iteration_error = StopIteration('Boom!')
            mock_queue_instance.put.side_effect = [iteration_error, None]
            MongoDataSetIOReader(name='test')
            mock_queue_instance.put.assert_called_with({'thread_error': iteration_error})
