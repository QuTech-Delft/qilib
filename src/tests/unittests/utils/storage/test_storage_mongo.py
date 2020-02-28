import datetime
import unittest
from unittest.mock import patch

import numpy as np
from bson import BSON
from bson.codec_options import TypeRegistry, CodecOptions
from mongomock import MongoClient

from qilib.utils.storage import StorageMongoDb
from qilib.utils.storage.interface import NoDataAtKeyError, NodeAlreadyExistsError, ConnectionTimeoutError
from qilib.utils.storage.mongo import NumpyArrayCodec
from tests.test_data.dummy_storage import DummyStorage


class TestStorageMongo(unittest.TestCase):
    def setUp(self) -> None:
        with patch('qilib.utils.storage.mongo.MongoClient', return_value=MongoClient()):
            self.storage = StorageMongoDb('test')
            self.test_data = [10, 3.14, 'string', {'a': 1, 'b': 2}, [1, 2], [1, [2, 3]], {'test': {'test': 2}},
                              {'tuple': (1, 2, 3, 4, 5)}, (1, 2, 3, 4, 5), (1, 2, {'he.llo': 'world'}),
                              {'int64': np.int64(3.)}]
            self.test_individual_data = {
                1: 'integer_value',
                '1': 'string_value',
                'dict': {
                    1: 'another_integer_value',
                    '1': {
                        1: 'last_integer_value',
                        'something.with.dot': 'another.key.with.dot'
                    }
                },
                'something.with.dot': 'key.with.dot',
                'something.else.with.dots': {
                    'key.dot': 123
                },
                'something': {
                    'with.dot': 'nested values',
                    'with': {
                        'dot': 123
                    }
                },
                'li.st': ['is', {'a': 'list', 12: 34}],
                'tu.ple': (1, 2, 'tuple', (1, 2, 3)),
                'boolean_value': False
            }
            self.dummy_storage = DummyStorage('dummy')

    def tearDown(self) -> None:
        self.storage._collection.drop()

    def test_server_timeout(self):
        error_msg = 'Failed to connect to Mongo database within 0.01 milliseconds$'
        self.assertRaisesRegex(ConnectionTimeoutError, error_msg, StorageMongoDb, 'test', port=-1,
                               connection_timeout=0.01)

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
        t = self.storage.datetag_part()
        self.assertIsInstance(t, str)
        self.assertRegex(t, r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{6}')

    def test_datetag_explicit(self):
        dt = datetime.datetime(2019, 2, 18, 13, 37, 0, 23)
        t = self.storage.datetag_part(dt)
        self.assertEqual(t, '2019-02-18T13:37:00.000023')

    def test_node_overwrite(self):
        storage = self.storage
        storage.save_data((1, 2), ['aap', 'noot'])
        self.assertRaises(NodeAlreadyExistsError, storage.save_data, 'mies', ['aap'])

    def test_leaf_overwrite(self):
        storage = self.storage
        storage.save_data('over', ['aap', 'noot'])
        self.assertEqual(storage.load_data(['aap', 'noot']), 'over')
        storage.save_data('overwrite', ['aap', 'noot'])
        self.assertEqual(storage.load_data(['aap', 'noot']), 'overwrite')

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

    def test_save_with_wrong_tag_type(self):
        self.assertRaises(TypeError, self.storage.save_data, None, 'wrong/tag/type')

    def test_save_tag_mixed_list_raises_error(self):
        error_msg = r"Tag \['bla', 5\] should be a list of strings"
        self.assertRaisesRegex(TypeError, error_msg, self.storage.save_data, 'data', ['bla', 5])

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

    def test_tag_in_storage(self):
        tag_in_storage = self.storage.tag_in_storage(['some-other-tag'])
        self.assertFalse(tag_in_storage)

        self.storage.save_data('some-dat', ['some-other-tag'])
        tag_in_storage = self.storage.tag_in_storage(['some-other-tag'])
        self.assertTrue(tag_in_storage)

    def test_store_keys_with_integer(self):
        data = {1: 'key with integer'}
        self.storage.save_data(data, ['data'])
        self.assertEqual(data, self.storage.load_data(['data']))

    def test_store_keys_with_negative_integer(self):
        data = {-1: 'key with negative integer'}
        self.storage.save_data(data, ['data'])
        self.assertEqual(data, self.storage.load_data(['data']))

    def test_store_keys_with_dots(self):
        data = {'key.with': 'dots!'}
        self.storage.save_data(data, ['data'])
        self.assertEqual(data, self.storage.load_data(['data']))

    def test_store_keys_with_integers_and_dots(self):
        data = {
            1: 'integer_value',
            '1': 'string_value',
            'dict': {
                1: 'another_integer_value',
                '1': {
                    1: 'last_integer_value',
                    'something.with.dot': 'another.key.with.dot'
                }
            },
            'something.with.dot': 'key.with.dot',
            'something.else.with.dots': {
                'key.dot': 123
            },
            'something': {
                'with.dot': 'nested values',
                'with': {
                    'dot': 123
                }
            },
            'li.st': ['is', {'a': 'list', 12: 34}],
            'tu.ple': (1, 2, 'tuple', (1, 2, 3))
        }
        self.storage.save_data(data, ['data'])
        self.assertEqual(data, self.storage.load_data(['data']))

    def test_is_encoded_int(self):
        self.assertTrue(StorageMongoDb._is_encoded_int('_integer[1]'))

    def test_is_encoded_int_negative(self):
        self.assertTrue(StorageMongoDb._is_encoded_int('_integer[-1]'))

    def test_is_encoded_int_error_format(self):
        self.assertFalse(StorageMongoDb._is_encoded_int('_int[1]'))

    def test_is_encoded_int_error_integer(self):
        self.assertFalse(StorageMongoDb._is_encoded_int('_integer[helloworld]'))

    def test_encode_int(self):
        self.assertEqual(StorageMongoDb._encode_int(7), '_integer[7]')

    def test_decode_int(self):
        self.assertEqual(StorageMongoDb._decode_int('_integer[7]'), 7)

    def test_decode_int_incorrect(self):
        self.assertRaises(ValueError, StorageMongoDb._decode_int, '_int[7]')

    def test_encode_str(self):
        self.assertEqual(StorageMongoDb._encode_str('hello.world'), 'hello\\u002eworld')

    def test_decode_str(self):
        self.assertEqual(StorageMongoDb._decode_str('hello.world'), 'hello.world')

    def test_update_individual_data(self):
        tag = ['system', 'properties']
        self.storage.save_data(self.test_individual_data, tag)
        self.assertEqual(self.test_individual_data, self.storage.load_data(tag))

        test_tuple = (1, 2, 3)
        test_list = ['was', {'b': 'string', 24: 68}]
        test_string = 'New.Key.with.dot'
        test_dict = {
            2: 'another_integer_value',
            '2': {
                2: 'last_integer_value',
                'new.with.dot': 'new.key.with.dot'
            }
        }
        test_array = np.array([4., 5.])

        self.storage.update_individual_data(test_tuple, tag, 'something')
        self.storage.update_individual_data(test_list, tag, 'li.st')
        self.storage.update_individual_data(test_string, tag, 'something.with.dot')
        self.storage.update_individual_data(test_dict, tag, 'dict')
        self.storage.update_individual_data(test_dict, tag, 1)
        self.storage.update_individual_data(True, tag, 'boolean_value')
        self.storage.update_individual_data(test_array, tag, 'numpy.array')

        data = self.storage.load_data(tag)

        self.assertEqual(data['something'], test_tuple)
        self.assertEqual(data['li.st'], test_list)
        self.assertEqual(data['something.with.dot'], test_string)
        self.assertEqual(data['dict'], test_dict)
        self.assertEqual(data[1], test_dict)
        self.assertEqual(data['boolean_value'], True)
        np.testing.assert_array_equal(data['numpy.array'], test_array)

    def test_update_individual_data_raises_error(self):
        tag = ['system', 'properties']
        self.storage.save_data(self.test_individual_data, tag)

        test_dict = {
            2: 'another_integer_value',
            '2': {
                2: 'last_integer_value',
                'new.with.dot': 'new.key.with.dot'
            }
        }
        self.assertRaises(NodeAlreadyExistsError,
                          self.storage.update_individual_data,
                          test_dict, ['system'], 1)

        self.assertRaises(NoDataAtKeyError,
                          self.storage.update_individual_data,
                          test_dict, ['system', 'something'], 1)

        self.assertRaises(NoDataAtKeyError,
                          self.storage.update_individual_data,
                          test_dict, ['something', 'another'], 1)

        self.assertRaises(NodeAlreadyExistsError,
                          self.storage.update_individual_data,
                          test_dict, tag + ['extra'], 'a key')

        self.assertRaises(TypeError,
                          self.storage.update_individual_data,
                          test_dict, tag, {'dict_as_field': 1})

    def test_update_individual_data_with_new_key(self):
        tag = ['system', 'properties']
        self.storage.save_data(self.test_individual_data, tag)

        test_dict = {
            2: 'another_integer_value',
            '2': {
                2: 'last_integer_value',
                'new.with.dot': 'new.key.with.dot'
            }
        }

        test_string = 'hello'
        test_int = 236

        self.storage.update_individual_data(test_dict, tag, 'new key')
        data = self.storage.load_individual_data(tag, 'new key')
        self.assertEqual(test_dict, data)

        self.storage.update_individual_data(test_string, tag, 42)
        data = self.storage.load_individual_data(tag, 42)
        self.assertEqual(test_string, data)

        self.storage.update_individual_data(test_int, tag, 42)
        data = self.storage.load_individual_data(tag, 42)
        self.assertEqual(test_int, data)

    def test_load_individual_data(self):
        data = {
            1: 'integer_value',
            '1.1': 'string_value',
            'something.dot': {'value': 273, 'unit': 'K'},
            'boolean_value': False
        }

        tag = ['system', 'properties', 'level 2']
        self.storage.save_data(data, tag)
        self.assertEqual(data, self.storage.load_data(tag))

        individual_data = self.storage.load_individual_data(tag, 1)
        self.assertEqual(data[1], individual_data)

        individual_data = self.storage.load_individual_data(tag, '1.1')
        self.assertEqual(data['1.1'], individual_data)

        individual_data = self.storage.load_individual_data(tag, 'something.dot')
        self.assertEqual(data['something.dot'], individual_data)

        individual_data = self.storage.load_individual_data(tag, 'boolean_value')
        self.assertEqual(data['boolean_value'], individual_data)

    def test_load_individual_data_raises_error(self):
        data = {
            1: 'integer_value',
            '1.1': 'string_value',
            'something.dot': {'value': 273, 'unit': 'K'}
        }
        tag = ['system', 'properties', 'level 2']
        self.storage.save_data(data, tag)

        self.assertRaises(NoDataAtKeyError,
                          self.storage.load_individual_data,
                          ['undefined tag'], 1)
        self.assertRaises(NoDataAtKeyError,
                          self.storage.load_individual_data,
                          ['system'], 1)
        self.assertRaises(NoDataAtKeyError,
                          self.storage.load_individual_data,
                          [], 1)
        self.assertRaises(NoDataAtKeyError,
                          self.storage.load_individual_data,
                          ['system', 'new', 'another'], 1)

    def test_load_individual_data_with_new_key(self):
        data = {
            1: 'integer_value',
            '1.1': 'string_value',
            'something.dot': {'value': 273, 'unit': 'K'}
        }
        tag = ['system', 'properties', 'level 2']
        self.storage.save_data(data, tag)

        self.assertRaises(NoDataAtKeyError,
                          self.storage.load_individual_data,
                          tag, 'something.dot.NEW')

        self.assertRaises(NoDataAtKeyError,
                          self.storage.load_individual_data,
                          tag, 11)

    def test_numpy_array_encoded_data(self):
        np_array = np.array([10., 20., 30.])
        data = self.dummy_storage.encode_serialize_data(np_array)
        shape = data['__content__']['__shape__']

        self.assertEqual(shape, [3])
        self.assertIsInstance(shape[0], int)

    def test_list_encoded_data(self):
        list_of_integers = [42, 43, 44]
        data = self.dummy_storage.encode_serialize_data(list_of_integers)

        self.assertIsInstance(data[0], int)
        self.assertEqual(data, list_of_integers)

        list_of_strings_with_dots = ['hello.world', 'string.with.dots']
        data = self.dummy_storage.encode_serialize_data(list_of_strings_with_dots)

        self.assertNotIn('\\u002e', data[0])
        self.assertIn('.', data[0])
        self.assertListEqual(data, list_of_strings_with_dots)
