import unittest
from unittest.mock import MagicMock, Mock

from qilib.configuration_helper.configuration_helper import ConfigurationHelper
from qilib.utils.storage import StorageMemory


class TestConfigurationHelper(unittest.TestCase):
    def test_snapshot(self):
        storage = StorageMemory('some_name')
        mock_configuration = MagicMock()
        configuration_helper = ConfigurationHelper(storage, mock_configuration)
        configuration_helper.snapshot(['some', 'tag'])
        mock_configuration.snapshot.assert_called_once_with(['some', 'tag'])

    def test_retrieve_inactive_configuration_from_storage(self):
        tag = ['some', 'tag']
        storage = StorageMemory('some_name')
        mock_configuration = {'some': 'config'}
        storage.save_data(mock_configuration, tag)
        configuration_helper = ConfigurationHelper(storage)
        configuration_helper.retrieve_inactive_configuration_from_storage(tag)
        # TODO Fix after merging the actual InstrumentConfigurationSet
        self.assertListEqual(tag, configuration_helper.inactive_configuration)

    def test_write_active_configuration_to_storage(self):
        storage = Mock()
        configuration_set = Mock()
        configuration_helper = ConfigurationHelper(storage, configuration_set)
        configuration_helper.write_active_configuration_to_storage()
        configuration_set.store.assert_called_once_with()

    def test_write_inactive_configuration_to_storage(self):
        storage = Mock()
        configuration_set = Mock()
        configuration_helper = ConfigurationHelper(storage)
        configuration_helper.inactive_configuration = configuration_set
        configuration_helper.write_inactive_configuration_to_storage()
        configuration_set.store.assert_called_once_with()

    def test_apply_inactive(self):
        storage = Mock()
        inactive_configuration_set = Mock()
        configuration_helper = ConfigurationHelper(storage, None, inactive_configuration_set)
        configuration_helper.apply_inactive()
        inactive_configuration_set.apply.assert_called_once_with()
        self.assertIs(inactive_configuration_set, configuration_helper.active_configuration)

    def test_apply_inactive_delta(self):
        storage = Mock()
        inactive_configuration_set = Mock()
        configuration_helper = ConfigurationHelper(storage, None, inactive_configuration_set)
        configuration_helper.apply_inactive_delta()
        inactive_configuration_set.apply_delta.assert_called_once_with()
        self.assertIs(inactive_configuration_set, configuration_helper.active_configuration)

    def test_apply_inactive_delta_lazy(self):
        storage = Mock()
        inactive_configuration_set = Mock()
        configuration_helper = ConfigurationHelper(storage, None, inactive_configuration_set)
        configuration_helper.apply_inactive_delta_lazy()
        inactive_configuration_set.apply_delta_lazy.assert_called_once_with()
        self.assertIs(inactive_configuration_set, configuration_helper.active_configuration)

    def test_get_tag_by_label(self):
        storage = Mock()
        configuration_helper = ConfigurationHelper(storage)
        configuration_helper.get_tag_by_label('online')
        storage.load_data.assert_called_once_with(['labels', 'online'])

    def test_label_tag(self):
        storage = StorageMemory('some_name')
        configuration_helper = ConfigurationHelper(storage)
        tag = ['some', 'tag']
        label = 'online'
        configuration_helper.label_tag(label, tag)
        self.assertListEqual(tag, configuration_helper.get_tag_by_label(label))



