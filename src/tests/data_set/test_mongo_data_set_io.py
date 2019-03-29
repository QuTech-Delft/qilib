import unittest
from collections import namedtuple
from unittest.mock import patch, MagicMock, call

from bson import ObjectId

from qilib.data_set import MongoDataSetIO
from qilib.data_set.mongo_data_set_io import DocumentNotFoundError


class TestMongoDataSetIO(unittest.TestCase):
    def test_constructor_only_name(self):
        mock_mongo_client = MagicMock()
        with patch('qilib.data_set.mongo_data_set_io.MongoClient',
                   return_value={'test': {'inventory': mock_mongo_client}}) as mongo_client:
            mock_mongo_client.find_one.return_value = {'_id': ObjectId('5c9a3457e3306c41f7ae1f3e'),
                                                       'name': 'test_data_set'}
            mock_mongo_client.insert_one.return_value.inserted_id = ObjectId('5c9a3457e3306c41f7ae1f3e')

            mongo_data_set_io = MongoDataSetIO(name='test_data_set')

            mongo_client.assert_called_once()
            mock_mongo_client.find_one.assert_called_once_with({'name': 'test_data_set'})
            self.assertEqual(mongo_data_set_io.name, 'test_data_set')
            self.assertEqual(mongo_data_set_io.id, '5c9a3457e3306c41f7ae1f3e')

    def test_constructor_name_not_found(self):
        mock_mongo_client = MagicMock()
        with patch('qilib.data_set.mongo_data_set_io.MongoClient',
                   return_value={'test': {'inventory': mock_mongo_client}}) as mongo_client:
            insert_one = namedtuple('insert_one', 'inserted_id')
            insert_one.inserted_id = ObjectId('5c9a3457e3306c41f7ae1f3e')
            mock_mongo_client.find_one.return_value = None
            mock_mongo_client.insert_one.return_value = insert_one

            mongo_data_set_io = MongoDataSetIO(name='test_data_set')

            mongo_client.assert_called_once()
            mock_mongo_client.find_one.assert_called_once_with({'name': 'test_data_set'})
            self.assertEqual(mongo_data_set_io.name, 'test_data_set')
            self.assertEqual(mongo_data_set_io.id, '5c9a3457e3306c41f7ae1f3e')

    def test_constructor_name_not_found_raises_error(self):
        mock_mongo_client = MagicMock()
        with patch('qilib.data_set.mongo_data_set_io.MongoClient',
                   return_value={'test': {'inventory': mock_mongo_client}}):
            mock_mongo_client.find_one.return_value = None

            error = DocumentNotFoundError, "Document not found in database."
            self.assertRaisesRegex(*error, MongoDataSetIO, name='test_data_set', create_if_not_found=False)
            mock_mongo_client.find_one.assert_called_once_with({'name': 'test_data_set'})

    def test_constructor_only_id(self):
        mock_mongo_client = MagicMock()
        with patch('qilib.data_set.mongo_data_set_io.MongoClient',
                   return_value={'test': {'inventory': mock_mongo_client}}) as mongo_client:
            mock_mongo_client.find_one.return_value = {'_id': ObjectId('5c9a3457e3306c41f7ae1f3e'),
                                                       'name': 'test_data_set'}
            mongo_data_set_io = MongoDataSetIO(document_id='5c9a3457e3306c41f7ae1f3e')

            mongo_client.assert_called_once()
            mock_mongo_client.find_one.assert_called_once_with({'_id': ObjectId('5c9a3457e3306c41f7ae1f3e')})
            self.assertEqual(mongo_data_set_io.name, 'test_data_set')
            self.assertEqual(mongo_data_set_io.id, '5c9a3457e3306c41f7ae1f3e')

    def test_constructor_id_not_found(self):
        mock_mongo_client = MagicMock()
        with patch('qilib.data_set.mongo_data_set_io.MongoClient',
                   return_value={'test': {'inventory': mock_mongo_client}}):
            mock_mongo_client.find_one.return_value = None

            error = DocumentNotFoundError, "Document not found in database."
            self.assertRaisesRegex(*error, MongoDataSetIO, document_id='5c9a3457e3306c41f7ae1f3e')
            mock_mongo_client.find_one.assert_called_once_with({'_id': ObjectId('5c9a3457e3306c41f7ae1f3e')})

    def test_constructor_name_and_id(self):
        mock_mongo_client = MagicMock()
        with patch('qilib.data_set.mongo_data_set_io.MongoClient',
                   return_value={'test': {'inventory': mock_mongo_client}}) as mongo_client:
            mock_mongo_client.find_one.return_value = {'_id': ObjectId('5c9a3457e3306c41f7ae1f3e'),
                                                       'name': 'test_data_set'}
            mock_mongo_client.insert_one.return_value.inserted_id = ObjectId('5c9a3457e3306c41f7ae1f3e')

            mongo_data_set_io = MongoDataSetIO(name='test_data_set', document_id='5c9a3457e3306c41f7ae1f3e')

            mongo_client.assert_called_once()
            mock_mongo_client.find_one.assert_called_once_with(
                {'_id': ObjectId('5c9a3457e3306c41f7ae1f3e'), 'name': 'test_data_set'})
            self.assertEqual(mongo_data_set_io.name, 'test_data_set')
            self.assertEqual(mongo_data_set_io.id, '5c9a3457e3306c41f7ae1f3e')

    def test_constructor_name_and_id_not_found(self):
        mock_mongo_client = MagicMock()
        with patch('qilib.data_set.mongo_data_set_io.MongoClient',
                   return_value={'test': {'inventory': mock_mongo_client}}):
            mock_mongo_client.find_one.return_value = None

            error = DocumentNotFoundError, "Document not found in database."
            self.assertRaisesRegex(*error, MongoDataSetIO, name='test_data_set', document_id='5c9a3457e3306c41f7ae1f3e')
            mock_mongo_client.find_one.assert_called_once_with(
                {'_id': ObjectId('5c9a3457e3306c41f7ae1f3e'), 'name': 'test_data_set'})

    def test_constructor_no_name_no_document_id(self):
        error = (DocumentNotFoundError, "Neither 'name' nor 'document_id' were provided.")
        self.assertRaisesRegex(*error, MongoDataSetIO)

    def test_watch(self):
        mock_mongo_client = MagicMock()
        with patch('qilib.data_set.mongo_data_set_io.MongoClient',
                   return_value={'test': {'inventory': mock_mongo_client}}):
            mock_mongo_client.find_one.return_value = {'_id': ObjectId('5c9a3457e3306c41f7ae1f3e'),
                                                       'name': 'test_data_set'}
            mock_mongo_client.watch.return_value = 'Watching'
            mongo_data_set_io = MongoDataSetIO(name='test_data_set')
            watcher = mongo_data_set_io.watch()
            pipeline = [{'$match': {'fullDocument.name': 'test_data_set'}}]
            mock_mongo_client.watch.assert_called_with(pipeline=pipeline, full_document='updateLookup')
            self.assertEqual('Watching', watcher)

    def test_get_document(self):
        mock_mongo_client = MagicMock()
        with patch('qilib.data_set.mongo_data_set_io.MongoClient',
                   return_value={'test': {'inventory': mock_mongo_client}}):
            db_document = {'_id': ObjectId('5c9a3457e3306c41f7ae1f3e'),
                           'name': 'test_data_set'}
            mock_mongo_client.find_one.return_value = db_document
            mongo_data_set_io = MongoDataSetIO(name='test_data_set')
            document = mongo_data_set_io.get_document()
            self.assertDictEqual(db_document, document)

    def test_finalize(self):
        with patch('qilib.data_set.mongo_data_set_io.MongoClient') as mock_client:
            mongo_data_set_io = MongoDataSetIO(name='test_data_set')
            mongo_data_set_io.finalize()
            mock_client.assert_has_calls([call().close()])

    def test_append_to_document(self):
        mock_mongo_client = MagicMock()
        with patch('qilib.data_set.mongo_data_set_io.MongoClient',
                   return_value={'test': {'inventory': mock_mongo_client}}):
            mongo_data_set_io = MongoDataSetIO(name='test_data_set')
            mongo_data_set_io.append_to_document({'metadata.label': 'test_data'})
            mock_mongo_client.update_one.called_once_with({'name': 'test_data_set'},
                                                          {'$push': {'metadata.label': 'test_data'},
                                                           "$currentDate": {"lastModified": True}})

    def test_update_document(self):
        mock_mongo_client = MagicMock()
        with patch('qilib.data_set.mongo_data_set_io.MongoClient',
                   return_value={'test': {'inventory': mock_mongo_client}}):
            mongo_data_set_io = MongoDataSetIO(name='test_data_set')
            mongo_data_set_io.update_document({'array_updates': ('(2,2)', {'test': 5})})
            mock_mongo_client.update_one.called_once_with({'name': 'test_data_set'},
                                                          {'$set': {'array_updates': ('(2,2)', {'test': 5})},
                                                           "$currentDate": {"lastModified": True}})
