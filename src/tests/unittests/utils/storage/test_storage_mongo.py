import datetime
import unittest
from unittest.mock import patch

import numpy as np
from bson import BSON
from bson.codec_options import TypeRegistry, CodecOptions
from mongomock import MongoClient

from qilib.utils.storage import StorageMongoDb
from qilib.utils.storage.interface import NoDataAtKeyError, NodeAlreadyExistsError
from qilib.utils.storage.mongo import NumpyArrayCodec


class TestStorageMongo(unittest.TestCase):
    def setUp(self) -> None:
        with patch('qilib.utils.storage.mongo.MongoClient', return_value=MongoClient()):
            self.storage = StorageMongoDb('test')
            self.test_data = [10, 3.14, 'string', {'a': 1, 'b': 2}, [1, 2], [1, [2, 3]], {'test': {'test': 2}}]

    def tearDown(self) -> None:
        self.storage._collection.drop()

    def test_save_load_basic_data(self):
        for index, value in enumerate(self.test_data):
            self.storage.save_data(value, ['data', str(index)])
        for index, value in enumerate(self.test_data):
            value_loaded = self.storage.load_data(['data', str(index)])
            self.assertEqual(value, value_loaded)

    def test_encode_decode_numpy_data(self):
        data = {'array': np.array([1, 2, 3])}

        type_registry = TypeRegistry([NumpyArrayCodec()])
        codec_options = CodecOptions(type_registry=type_registry)
        encoded = BSON.encode(data, codec_options=codec_options)
        decoded = BSON.decode(encoded, codec_options=codec_options)

        self.assertIsInstance(decoded, type(data))
        self.assertIn('array', decoded)
        np.testing.assert_array_equal(data['array'], decoded['array'])

    def test_tag_type(self):
        self.assertRaises(TypeError, self.storage.load_data, 3)
        self.assertRaises(TypeError, self.storage.load_data, '/str/tag/')

    def test_search(self):
        self.assertRaises(NotImplementedError, self.storage.search, None)

    def test_datetag_implicit(self):
        t = self.storage.datetag()
        self.assertIsInstance(t, str)
        self.assertRegex(t, r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{6}')

    def test_datetag_explicit(self):
        dt = datetime.datetime(2019, 2, 18, 13, 37, 0, 23)
        t = self.storage.datetag(dt)
        self.assertEqual(t, '2019-02-18T13:37:00.000023')

    def test_node_overwrite(self):
        storage = self.storage
        storage.save_data((1, 2), ['aap', 'noot'])
        self.assertRaises(NodeAlreadyExistsError, storage.save_data, 'mies', ['aap'])

    def test_no_data(self):
        self.assertRaises(NoDataAtKeyError, self.storage.load_data, ['nosuchdata'])
        self.assertRaises(NoDataAtKeyError, self.storage.load_data, ['nonode', 'nosuchdata'])

    def test_load(self):
        self.assertRaises(NoDataAtKeyError, self.storage.load_data, [])

    def test_list_subtags(self):
        results = self.storage.list_data_subtags(['nodata'])
        self.assertEqual(results, [])
        self.storage.save_data('1', ['1'])
        results = self.storage.list_data_subtags(['1', 'nodata'])
        self.assertEqual(results, [])

        results = self.storage.list_data_subtags(['1'])
        self.assertEqual(results, [])

        results = self.storage.list_data_subtags(['1a', '2', '3'])
        self.assertEqual(results, [])

        self.storage.save_data('test', ['hello', 'world'])
        results = self.storage.list_data_subtags(['hello'])
        self.assertEqual(results, ['world'])

    def test_save_load(self):
        storage = self.storage
        storage.save_data((1, 2), ['aap'])
        self.assertRaises(NodeAlreadyExistsError, storage.save_data, 'x', ['aap', 'noot'])
        storage.save_data('x', ['aapjes', 'noot'])
        storage.save_data('x2', ['aapjes', 'mies'])

        result = storage.load_data(['aapjes', 'noot'])
        self.assertEqual(result, 'x')
        results = storage.list_data_subtags(['aapjes'])
        self.assertIsInstance(results, list)
        self.assertEqual(results, ['noot', 'mies'])

        storage.save_data('x2', ['1', '2', '3'])
        self.assertRaises(NoDataAtKeyError, storage.load_data, ['1', '2'])
        results = storage.list_data_subtags(['1', '2'])
        self.assertEqual(results, ['3'])

    def test_get_latest(self):
        storage = self.storage
        test_tags = [
            '2018-05-04T09:14:21.418753',
            '2018-05-04T09:14:22.789361',
            '2018-05-04T09:16:42.230137',
            '2018-05-05T16:03:11.927642',
        ]
        for index in range(len(test_tags)):
            storage.save_data(index, ['times', test_tags[index]])
        latest_tag = storage.get_latest_subtag(['times'])
        self.assertEqual(storage.load_data(latest_tag), index)
        tag = storage.get_latest_subtag(['nosuchtag'])
        self.assertIsNone(tag)

    def test_leaf_node_in_path(self):
        self.storage.save_data('foo', ['foo', 'bar'])
        result = self.storage.list_data_subtags(['foo', 'bar'])
        self.assertListEqual(result, [])
