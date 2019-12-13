from unittest import TestCase
from unittest.mock import patch, Mock

from qilib.configuration_helper import InstrumentConfiguration
from qilib.configuration_helper.instrument_configuration_set import InstrumentConfigurationSet, DuplicateTagError
from qilib.utils.storage import StorageMemory


class TestInstrumentConfigurationSet(TestCase):
    def setUp(self):
        self._storage = StorageMemory('test_storage')

    def test_constructor(self):
        instrument_configuration_set = InstrumentConfigurationSet(self._storage)
        self.assertEqual(instrument_configuration_set.instrument_configurations, [])
        self.assertIs(instrument_configuration_set.storage, self._storage)
        self.assertEqual(len(instrument_configuration_set.tag), 2)
        self.assertEqual(instrument_configuration_set.tag[0], 'configuration_set')
        self.assertRegex(instrument_configuration_set.tag[1], r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{6}')

    def test_load(self):
        instrument_configuration_set = InstrumentConfigurationSet(self._storage)
        instrument_configuration_set.store()

        instrument_configuration_set_new = InstrumentConfigurationSet.load(instrument_configuration_set.tag,
                                                                           self._storage)

        self.assertEqual(instrument_configuration_set_new.tag, instrument_configuration_set.tag)
        self.assertEqual(instrument_configuration_set_new.instrument_configurations,
                         instrument_configuration_set.instrument_configurations)

    def test_load_with_instruments(self):
        with patch('qilib.configuration_helper.instrument_configuration.InstrumentAdapterFactory'):
            instrument_1 = InstrumentConfiguration('DummyClass', 'fake-address-1', self._storage, tag=['instrument_1'])
            instrument_2 = InstrumentConfiguration('DummyClass', 'fake-address-2', self._storage, tag=['instrument_2'])

            instrument_configuration_set = InstrumentConfigurationSet(self._storage,
                                                                      instrument_configurations=[instrument_1,
                                                                                                 instrument_2])
            instrument_configuration_set.store()

            instrument_configuration_set_new = InstrumentConfigurationSet.load(instrument_configuration_set.tag,
                                                                               self._storage)

        self.assertEqual(instrument_configuration_set_new.tag, instrument_configuration_set.tag)
        self.assertEqual(len(instrument_configuration_set_new.instrument_configurations), 2)
        self.assertEqual(instrument_configuration_set_new.instrument_configurations[0].tag, instrument_1.tag)
        self.assertEqual(instrument_configuration_set_new.instrument_configurations[1].tag, instrument_2.tag)

    def test_store(self):
        instrument_configuration_set = InstrumentConfigurationSet(self._storage)
        instrument_configuration_set.store()

        self.assertTrue(self._storage.tag_in_storage(instrument_configuration_set.tag))

    def test_store_with_instruments(self):
        with patch('qilib.configuration_helper.instrument_configuration.InstrumentAdapterFactory'):
            instrument_1 = InstrumentConfiguration('DummyClass', 'fake-address-1', self._storage, tag=['instrument_1'])
            instrument_2 = InstrumentConfiguration('DummyClass', 'fake-address-2', self._storage, tag=['instrument_2'])
            instrument_1.store()
            instrument_2.store()

            instrument_configuration_set = InstrumentConfigurationSet(self._storage,
                                                                      instrument_configurations=[instrument_1,
                                                                                                 instrument_2])

            instrument_configuration_set.store()

            self.assertTrue(self._storage.tag_in_storage(instrument_configuration_set.tag))
            self.assertTrue(self._storage.tag_in_storage(instrument_1.tag))
            self.assertTrue(self._storage.tag_in_storage(instrument_2.tag))

    def test_store_raises_error(self):
        instrument_configuration_set = InstrumentConfigurationSet(self._storage)
        instrument_configuration_set.store()

        self.assertRaises(DuplicateTagError, instrument_configuration_set.store)

    def test_apply(self):
        instrument_1 = Mock()
        instrument_2 = Mock()

        instrument_configuration_set = InstrumentConfigurationSet(self._storage,
                                                                  instrument_configurations=[instrument_1,
                                                                                             instrument_2])
        instrument_configuration_set.apply()

        instrument_1.apply.assert_called_once_with()
        instrument_2.apply.assert_called_once_with()

    def test_apply_delta(self):
        instrument_1 = Mock()
        instrument_2 = Mock()

        instrument_configuration_set = InstrumentConfigurationSet(self._storage,
                                                                  instrument_configurations=[instrument_1,
                                                                                             instrument_2])
        instrument_configuration_set.apply_delta()

        instrument_1.apply_delta.assert_called_once()
        instrument_2.apply_delta.assert_called_once()

    def test_apply_delta_lazy(self):
        instrument_1 = Mock()
        instrument_2 = Mock()

        instrument_configuration_set = InstrumentConfigurationSet(self._storage,
                                                                  instrument_configurations=[instrument_1,
                                                                                             instrument_2])
        instrument_configuration_set.apply_delta_lazy()

        instrument_1.apply_delta_lazy.assert_called_once_with()
        instrument_2.apply_delta_lazy.assert_called_once_with()

    def test_snapshot(self):
        with patch('qilib.configuration_helper.instrument_configuration.InstrumentAdapterFactory') as factory_mock:
            instrument_mock = Mock()
            factory_mock.get_instrument_adapter.return_value = instrument_mock
            instrument_mock.read.return_value = {'hello': 'world'}

            instrument_1 = InstrumentConfiguration('DummyClass', 'fake-address-1', self._storage, tag=['instrument_1'])
            instrument_2 = InstrumentConfiguration('DummyClass', 'fake-address-2', self._storage, tag=['instrument_2'])

            instrument_configuration_set = InstrumentConfigurationSet(self._storage, tag=['test'],
                                                                      instrument_configurations=[instrument_1,
                                                                                                 instrument_2])
            tag = instrument_configuration_set.tag
            tag_1 = instrument_1.tag
            tag_2 = instrument_2.tag

            instrument_configuration_set.snapshot()

            self.assertNotEqual(instrument_configuration_set.tag, tag)
            self.assertNotEqual(instrument_1.tag, tag_1)
            self.assertNotEqual(instrument_2.tag, tag_2)
