import unittest
from unittest.mock import patch, call

from qilib.data_set import MongoDataSetIOWriter, DataArray, MongoDataSetIO


class TestMongoDataSetIOWriter(unittest.TestCase):

    def test_sync_metadata_to_storage(self):
        with patch('qilib.data_set.mongo_data_set_io_writer.MongoDataSetIO') as mongo_data_set_io:
            name = 'test'
            document_id = '0x2A'
            writer = MongoDataSetIOWriter(name=name, document_id=document_id)
            mongo_data_set_io.assert_called_once_with(name, document_id, collection='data_sets', database='qilib')

            field = 'label'
            value = 'measurement'
            writer.sync_metadata_to_storage(field, value)

            mongo_data_set_io.assert_has_calls([call().update_document({'metadata.label': value})])

    def test_sync_data_to_storage(self):
        with patch('qilib.data_set.mongo_data_set_io_writer.MongoDataSetIO') as mongo_data_set_io:
            name = 'test'
            document_id = '0x2A'
            writer = MongoDataSetIOWriter(name=name, document_id=document_id)
            mongo_data_set_io.assert_called_once_with(name, document_id, collection='data_sets', database='qilib')

            index = 5
            data = {'some_array': 25}
            writer.sync_data_to_storage(index, data)

            mongo_data_set_io.assert_has_calls([call().append_to_document({'array_updates': (index, data)})])

    def test_sync_data_array_to_storage(self):
        with patch('qilib.data_set.mongo_data_set_io_writer.MongoDataSetIO') as mongo_data_set_io:
            mongo_data_set_io.encode_numpy_array = MongoDataSetIO.encode_numpy_array
            name = 'test'
            document_id = '0x2A'
            writer = MongoDataSetIOWriter(name=name, document_id=document_id)
            mongo_data_set_io.assert_called_once_with(name, document_id, collection='data_sets', database='qilib')

            set_array = DataArray(name='set_array', label='for_testing', is_setpoint=True, shape=(2, 2))
            data_array = DataArray(name='the_array', label='unit_test', unit='T', is_setpoint=False, preset_data=None,
                                   set_arrays=[set_array], shape=(2, 2))
            writer.sync_add_data_array_to_storage(data_array)

            expected = {
                'data_arrays.the_array': {'name': 'the_array', 'label': "unit_test", 'unit': 'T', 'is_setpoint': False,
                                          'set_arrays': ['set_array'],
                                          'preset_data': MongoDataSetIO.encode_numpy_array(data_array)}}
            mongo_data_set_io.assert_has_calls(
                [call('test', '0x2A', collection='data_sets', database='qilib'), call().update_document(expected)])

    def test_finalize(self):
        with patch('qilib.data_set.mongo_data_set_io_writer.MongoDataSetIO') as mongo_data_set_io:
            name = 'test'
            document_id = '0x2A'
            writer = MongoDataSetIOWriter(name=name, document_id=document_id)
            mongo_data_set_io.assert_called_once_with(name, document_id, collection='data_sets', database='qilib')

            writer.finalize()
            mongo_data_set_io.assert_has_calls([call().finalize()])

            error_args = (ValueError, 'Operation on closed IO writer.')
            self.assertRaisesRegex(*error_args, writer.sync_metadata_to_storage, field_name='name', value='test')
