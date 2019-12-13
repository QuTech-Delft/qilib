import unittest
from unittest.mock import MagicMock, Mock, patch

from qilib.configuration_helper import InstrumentConfiguration, InstrumentConfigurationSet
from qilib.configuration_helper.configuration_helper import ConfigurationHelper
from qilib.utils import PythonJsonStructure
from qilib.utils.storage import StorageMemory


class TestConfigurationHelper(unittest.TestCase):
    def test_snapshot(self):
        storage = StorageMemory('some_name')
        mock_configuration = MagicMock()
        configuration_helper = ConfigurationHelper(storage, mock_configuration)
        configuration_helper.snapshot(['some', 'tag'])
        mock_configuration.snapshot.assert_called_once_with(['some', 'tag'])

    def test_retrieve_inactive_configuration_from_storage(self):
        tag = ['some']
        storage = Mock()
        configuration_tags = [['some_tag']]
        configuration = {'adapter_class_name': 'Dummy', 'address': 'fake', 'configuration': {'param': 'value'}}
        storage.load_data.side_effect = [configuration_tags, configuration]
        with patch('qilib.configuration_helper.instrument_configuration.InstrumentAdapterFactory'):
            configuration_helper = ConfigurationHelper(storage)
            configuration_helper.retrieve_inactive_configuration_from_storage(tag)
        inactive_configuration = configuration_helper._inactive_configuration
        self.assertListEqual(inactive_configuration.tag, tag)
        self.assertListEqual(inactive_configuration.instrument_configurations[0].tag, ['some_tag'])
        self.assertEqual(inactive_configuration.instrument_configurations[0].address, 'fake')
        self.assertDictEqual(inactive_configuration.instrument_configurations[0].configuration, {'param': 'value'})

    def test_configuration_helper_integration(self):
        storage = StorageMemory('some_name')
        configuration_1 = PythonJsonStructure(amper=0.005)
        configuration_2 = PythonJsonStructure(frequency='2.4 GHz')
        with patch('qilib.configuration_helper.instrument_configuration.InstrumentAdapterFactory'):
            instrument_1 = InstrumentConfiguration('DummyClass', 'fake-address-1', storage, tag=['instrument_1'],
                                                   configuration=configuration_1)
            instrument_2 = InstrumentConfiguration('DummyClass', 'fake-address-2', storage, tag=['instrument_2'],
                                                   configuration=configuration_2)
            instrument_configuration_set = InstrumentConfigurationSet(storage, tag=['set'],
                                                                      instrument_configurations=[instrument_1,
                                                                                                 instrument_2])
            instrument_configuration_set.store()

            configuration_helper = ConfigurationHelper(storage)
            configuration_helper.retrieve_inactive_configuration_from_storage(['set'])
        inactive_configuration = configuration_helper.inactive_configuration
        self.assertListEqual(inactive_configuration.tag, ['set'])
        self.assertListEqual(inactive_configuration.instrument_configurations[0].tag, ['instrument_1'])
        self.assertListEqual(inactive_configuration.instrument_configurations[1].tag, ['instrument_2'])
        self.assertDictEqual(configuration_1, inactive_configuration.instrument_configurations[0].configuration)
        self.assertDictEqual(configuration_2, inactive_configuration.instrument_configurations[1].configuration)
        repr_str = r"ConfigurationHelper\(StorageMemory\('some_name'\), InstrumentConfigurationSet\(StorageMemory\(" \
                   r"'some_name'\), \['configuration_set', '.*'\], \[\]\), " \
                   r"InstrumentConfigurationSet\(StorageMemory\('some_name'\), \['set'\], \[InstrumentConfiguration\(" \
                   r"'DummyClass', 'fake-address-1', StorageMemory\('some_name'\), \['instrument_1'\], " \
                   r"\{'amper': 0.005\}, None\), InstrumentConfiguration\('DummyClass', 'fake-address-2', " \
                   r"StorageMemory\('some_name'\), \['instrument_2'\], \{'frequency': '2.4 GHz'\}, None\)\]\)\)"
        self.assertRegex(repr(configuration_helper), repr_str)

    def test_write_active_configuration_to_storage(self):
        storage = Mock()
        configuration_set = Mock()
        configuration_helper = ConfigurationHelper(storage, configuration_set)
        configuration_helper.write_active_configuration_to_storage()
        configuration_set.store.assert_called_once_with()

    def test_write_inactive_configuration_to_storage(self):
        storage = Mock()
        configuration_set = Mock()
        configuration_helper = ConfigurationHelper(storage, inactive_configuration=configuration_set)
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
