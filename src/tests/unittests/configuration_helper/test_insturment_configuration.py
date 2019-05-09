import unittest
from unittest.mock import patch, MagicMock

from qilib.configuration_helper import InstrumentConfiguration, InstrumentAdapter
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
                                                               tag=['some-tag'], configuration=config)
        self.assertDictEqual(config, instrument_configuration.configuration)
        self.assertListEqual(['some-tag'], instrument_configuration.tag)

    def test_load(self):
        some_data = {'adapter_class_name': 'Dummy',
                     'address': 'dev42',
                     'configuration': {'power': 'MAX',
                                       'other': 'SOME',
                                       'one_more': 0.42}}

        self._storage.save_data(some_data, ['4242'])
        with patch('qilib.configuration_helper.instrument_configuration.InstrumentAdapterFactory') as mock_factory:
            instrument_configuration = InstrumentConfiguration.load(['4242'], self._storage)  # TODO: Make me real
            mock_factory.get_instrument_adapter.assert_called_with('Dummy', 'dev42')
            self.assertListEqual(['4242'], instrument_configuration.tag)
            self.assertDictEqual(some_data['configuration'], instrument_configuration.configuration)

    def test_apply_delta(self):
        mock_adapter = MagicMock(spec=InstrumentAdapter)
        with patch('qilib.configuration_helper.instrument_configuration.InstrumentAdapterFactory') as mock_factory:
            mock_factory.get_instrument_adapter.return_value = mock_adapter
            instrument_configuration = InstrumentConfiguration('Dummy', 'fake', self._storage)
