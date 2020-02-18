import unittest
from unittest.mock import patch

from qilib.utils.storage.interface import StorageInterface


class TestStorage(unittest.TestCase):

    def test_tag_to_list(self):
        tag_to_list = StorageInterface._tag_to_list('a/b')
        self.assertEqual(tag_to_list, ['a', 'b'])

    def test_tag_to_list_invalid_type(self):
        with self.assertRaisesRegex(TypeError, 'tag should be of type %s' % list):
            _ = StorageInterface._tag_to_list(3)

    def test_tag_to_string(self):
        tag_to_string = StorageInterface._tag_to_string(['a', 'b'])
        self.assertEqual(tag_to_string, 'a/b')

    def test_tag_to_string_invalid_type(self):
        with self.assertRaisesRegex(TypeError, 'tag should be of type %s' % list):
            _ = StorageInterface._tag_to_string(3)

    def test_abc_dummy_tests(self):
        with patch.multiple(StorageInterface, __abstractmethods__=set()):
            storage_interface = StorageInterface('test_abc')
            storage_interface.save_data(None, None)
            storage_interface.load_data(None)
            storage_interface.get_latest_subtag(None)
            storage_interface.list_data_subtags(None)
            storage_interface.load_individual_data(None, None)
            storage_interface.update_individual_data(None, None, None)
            self.assertRaises(NotImplementedError, storage_interface.search, None)
