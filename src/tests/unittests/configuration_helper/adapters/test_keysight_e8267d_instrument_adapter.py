import unittest
from unittest.mock import call, patch, Mock, MagicMock

from qilib.configuration_helper import InstrumentAdapterFactory


class TestKeysightE8267DInstrumentAdapter(unittest.TestCase):

    def test_read_filter_out_val_mapping(self):
        with patch('qilib.configuration_helper.adapters.keysight_e8267d_instrument_adapter.Keysight_E8267D') \
                as mock_instrument:
            mock_instrument_instance = MagicMock()
            mock_instrument.return_value = mock_instrument_instance
            mock_instrument_instance.snapshot.return_value = {
                'name': 'some_keysight',
                'parameters': {
                    'good_parameter': {'value': 42},
                    'filtered_parameter_1': {'val_mapping': {1: True, 0: False}, 'value': False},
                    'filtered_parameter_2': {'on_off_mapping': {1: 'ON', 0: 'OFF'}, 'value': 'OFF'}
                }
            }
            adapter = InstrumentAdapterFactory.get_instrument_adapter('KeysightE8267DInstrumentAdapter', 'fake')
        config = adapter.read()
        self.assertNotIn('val_mapping', config['filtered_parameter_1'])
        self.assertNotIn('on_off_mapping', config['filtered_parameter_2'])
        self.assertEqual(42, config['good_parameter']['value'])
        self.assertEqual('some_keysight', config['name'])
        self.assertFalse(config['filtered_parameter_1']['value'])
        self.assertEqual('OFF', config['filtered_parameter_2']['value'])
        adapter.close_instrument()

