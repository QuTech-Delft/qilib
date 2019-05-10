import unittest
from unittest.mock import patch, MagicMock

from qilib.configuration_helper import InstrumentConfiguration, InstrumentAdapter
from qilib.configuration_helper.instrument_configuration import DuplicateTagError
from qilib.utils import PythonJsonStructure
from qilib.utils.storage import StorageMemory


class TestInstrumentConfiguration(unittest.TestCase):
    def setUp(self):
        self._storage = StorageMemory('test_storage')

    def test_constructor(self):
        with patch('qilib.configuration_helper.instrument_configuration.InstrumentAdapterFactory'):
            instrument_configuration = InstrumentConfiguration('DummyClass', 'fake-address', self._storage)
        self.assertIsInstance(instrument_configuration.configuration, PythonJsonStructure)
        self.assertDictEqual({}, instrument_configuration.configuration)
        self.assertEqual('fake-address', instrument_configuration.address)
        self.assertRegex(instrument_configuration.tag[0], r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{6}')

    def test_constructor_full(self):
        config = PythonJsonStructure(voltage='low', current='lower', frequency='high-enough')
        with patch('qilib.configuration_helper.instrument_configuration.InstrumentAdapterFactory'):
            instrument_configuration = InstrumentConfiguration('DummyClass', 'fake-address', self._storage,
                                                               tag=['2019-05-09T11:29:51.523636'], configuration=config)
        self.assertDictEqual(config, instrument_configuration.configuration)
        self.assertListEqual(['2019-05-09T11:29:51.523636'], instrument_configuration.tag)

    def test_load(self):
        some_data = {'adapter_class_name': 'Dummy',
                     'address': 'dev42',
                     'configuration': {'power': 'MAX',
                                       'other': 'SOME',
                                       'one_more': 0.42}}

        self._storage.save_data(some_data, ['2019-05-09T11:29:51.523636'])
        with patch('qilib.configuration_helper.instrument_configuration.InstrumentAdapterFactory') as mock_factory:
            instrument_configuration = InstrumentConfiguration.load(['2019-05-09T11:29:51.523636'], self._storage)
            mock_factory.get_instrument_adapter.assert_called_with('Dummy', 'dev42')
            self.assertListEqual(['2019-05-09T11:29:51.523636'], instrument_configuration.tag)
            self.assertDictEqual(some_data['configuration'], instrument_configuration.configuration)

    def test_store_raises_error(self):
        with patch('qilib.configuration_helper.instrument_configuration.InstrumentAdapterFactory'):
            instrument_configuration = InstrumentConfiguration('DummyClass', 'fake-address', self._storage,
                                                               tag=['2019-05-09T11:29:51.523636'])
            instrument_configuration.store()
            error = "InstrumentConfiguration with tag '\['2019-05-09T11:29:51.523636'\]' already in storage"
            self.assertRaisesRegex(DuplicateTagError, error, instrument_configuration.store)

    def test_store(self):
        with patch('qilib.configuration_helper.instrument_configuration.InstrumentAdapterFactory'):
            instrument_configuration = InstrumentConfiguration('DummyClass', 'fake-address', self._storage,
                                                               tag=['2019-07-11T00:00:00.424242'])
            instrument_configuration.store()
            self.assertTrue(self._storage.tag_in_storage(['2019-07-11T00:00:00.424242']))

    def test_apply(self):
        with patch('qilib.configuration_helper.instrument_configuration.InstrumentAdapterFactory') as mock_factory:
            mock_adapter = MagicMock()
            mock_factory.get_instrument_adapter.return_value = mock_adapter
            instrument_configuration = InstrumentConfiguration('DummyClass', 'fake-address', self._storage,
                                                               configuration=PythonJsonStructure(
                                                                   how_many_instruments='all_the_instruments'))
            instrument_configuration.apply()
        mock_adapter.apply.assert_called_once_with({'how_many_instruments': 'all_the_instruments'})

    def test_apply_delta(self):
        with patch('qilib.configuration_helper.instrument_configuration.InstrumentAdapterFactory') as mock_factory:
            mock_adapter = MagicMock()
            mock_adapter.read.return_value = PythonJsonStructure(param1={'value': 1}, param2={'value': 2},
                                                                 param3={'value': 3}, param4={'value': 4})
            mock_factory.get_instrument_adapter.return_value = mock_adapter
            instrument_configuration = InstrumentConfiguration('DummyClass', 'fake-address', self._storage,
                                                               configuration=PythonJsonStructure(param1={'value': 1},
                                                                                                 param2={'value': 42},
                                                                                                 param3={'value': 3},
                                                                                                 param4={'value': 4}))
            instrument_configuration.apply_delta()
            mock_adapter.read.assert_called_once_with(update=True)
            mock_adapter.apply.assert_called_once_with({'param2': {'value': 42}})

    def test_apply_delta_lazy(self):
        with patch('qilib.configuration_helper.instrument_configuration.InstrumentAdapterFactory') as mock_factory:
            mock_adapter = MagicMock()
            mock_adapter.read.return_value = PythonJsonStructure(param1={'value': 1}, param2={'value': 2},
                                                                 param3={'value': 3}, param4={'value': 4})
            mock_factory.get_instrument_adapter.return_value = mock_adapter
            instrument_configuration = InstrumentConfiguration('DummyClass', 'fake-address', self._storage,
                                                               configuration=PythonJsonStructure(param1={'value': 1},
                                                                                                 param2={'value': 42},
                                                                                                 param3={'value': 33}))
            instrument_configuration.apply_delta_lazy()
            mock_adapter.read.assert_called_once_with(update=False)
            mock_adapter.apply.assert_called_once_with({'param2': {'value': 42}, 'param3': {'value': 33}})

    def test_refresh(self):
        with patch('qilib.configuration_helper.instrument_configuration.InstrumentAdapterFactory') as mock_factory:
            mock_adapter = MagicMock()
            instrument_settings = PythonJsonStructure(param1={'value': 1}, param2={'value': 2},
                                                      param3={'value': 3}, param4={'value': 4})
            mock_adapter.read.return_value = instrument_settings
            mock_factory.get_instrument_adapter.return_value = mock_adapter
            instrument_configuration = InstrumentConfiguration('DummyClass', 'fake-address', self._storage,
                                                               configuration=PythonJsonStructure(
                                                                   param1={'value': 11},
                                                                   param2={'value': 22},
                                                                   param3={'value': 33},
                                                                   param4={'value': 444}))
            instrument_configuration.refresh()
        self.assertDictEqual(instrument_settings, instrument_configuration.configuration)
