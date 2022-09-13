import datetime
import unittest
import numpy as np

from qilib.utils.storage.interface import NoDataAtKeyError, NodeAlreadyExistsError, NodeDoesNotExistsError
from qilib.utils.storage.memory import StorageMemory


class TestStorageMemory(unittest.TestCase):

    def setUp(self):
        self.storage = StorageMemory('test')
        self.testdata = [10, 3.14, 'string', {'a': 1, 'b': 2}, [1, 2], [1, [2, 3]],
                         np.array([1, 2, 3])]

    def test_save_load_basic_data(self):
        for index, value in enumerate(self.testdata):
            self.storage.save_data(value, ['data', str(index)])
        for index, value in enumerate(self.testdata):
            value_loaded = self.storage.load_data(['data', str(index)])
            if isinstance(value, np.ndarray):
                np.testing.assert_array_equal(value, value_loaded)
            else:
                self.assertEqual(value, value_loaded)

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

    def test_list_subtags_limit(self):
        self.storage.save_data('1', ['a', '1'])
        self.storage.save_data('1', ['a', '2'])
        tags = self.storage.list_data_subtags(['a'], limit=0)
        self.assertEqual(tags, ['1', '2'])
        tags = self.storage.list_data_subtags(['a'], limit=1)
        self.assertEqual(tags, ['1'])

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
        self.assertEqual(storage.load_data(latest_tag), len(test_tags) - 1)
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

    def test_load_individual_data(self):
        for index, value in enumerate(self.testdata):
            self.storage.save_data(value, ['data', str(index)])

        value_loaded = self.storage.load_individual_data(['data', str(3)], 'a')
        self.assertEqual(1, value_loaded)

        value_loaded = self.storage.load_individual_data(['data', str(3)], 'b')
        self.assertEqual(2, value_loaded)

        self.assertRaises(TypeError, self.storage.load_individual_data, 1, 1)

        self.assertRaises(NoDataAtKeyError, self.storage.load_individual_data,
                          ['data', str(3)], 'C')

    def test_update_individual_data(self):
        for index, value in enumerate(self.testdata):
            self.storage.save_data(value, ['data', str(index)])

        self.storage.update_individual_data(42, ['data', str(3)], 'a')
        value_loaded = self.storage.load_individual_data(['data', str(3)], 'a')
        self.assertEqual(42, value_loaded)

        self.storage.update_individual_data(42, ['data', str(3)], 'NEW KEY')
        value_loaded = self.storage.load_individual_data(['data', str(3)], 'NEW KEY')
        self.assertEqual(42, value_loaded)

        self.storage.update_individual_data(42, ['data', str(3)], 9999999)
        value_loaded = self.storage.load_individual_data(['data', str(3)], 9999999)
        self.assertEqual(42, value_loaded)

        self.assertRaises(TypeError, self.storage.update_individual_data, 42, ['data', str(3)], {'dict_as_field': 1})

        self.assertRaises(NodeDoesNotExistsError, self.storage.update_individual_data, 42, ['data', str(3000)], 'a')
        self.assertRaises(NodeDoesNotExistsError, self.storage.update_individual_data, 42, ['data3000'], 'a')

    def test_load_data_from_subtag(self):
        storage_interface = StorageMemory('test')
        for ii in range(4):
            storage_interface.save_data(ii, ['s', f's{ii}'])
        self.assertEqual(list(storage_interface.load_data_from_subtag(['s'])), [0, 1, 2, 3])

    def test_query_data_tags(self):
        s = StorageMemory('test_database')  # 'test'+str(uuid.uuid4()))
        st = s.list_data_subtags([])
        assert st == []
        s.query_data_tags(['b'])

        for jj in range(5):
            s.save_data({'i': jj, 'ii': -jj}, ['a', str(jj)])
        tags, data = s.query_data_tags(['a'])
        assert len(tags) == 5

        s.save_data({'one': 1}, ['a', 'b', 'c'])


