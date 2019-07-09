import unittest
from unittest.mock import call, patch, Mock, MagicMock

from qilib.configuration_helper import InstrumentAdapterFactory


class TestKeysightE8267DInstrumentAdapter(unittest.TestCase):

    def test_read_and_apply(self):
        with patch('qilib.configuration_helper.adapters.keysight_e8267d_instrument_adapter.Keysight_E8267D') \
                as mock_instrument:
            mock_instrument_instance = MagicMock()
            mock_instrument.return_value = mock_instrument_instance
            mock_instrument_instance.snapshot.return_value = {
                'parameters': {
                    'good_parameter': {'value': 42},
                    'filtered_parameter_1': {'val_mapping': {1: True, 0: False}, 'value': False},
                    'filtered_parameter_2': {'on_off_mapping': {1: 'ON', 0: 'OFF'}, 'value': 'OFF'}
                }
            }
            adapter = InstrumentAdapterFactory.get_instrument_adapter('KeysightE8267DInstrumentAdapter', 'fake')
        config = adapter.read()
        adapter.apply(config)

        mock_calls = [
            call().set('good_parameter', 42),
            call().set('filtered_parameter_1', False),
            call().set('filtered_parameter_2', 'OFF')
        ]
        mock_instrument.assert_has_calls(mock_calls)
