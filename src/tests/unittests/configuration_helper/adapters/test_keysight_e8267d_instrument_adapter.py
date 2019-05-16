import unittest
from unittest.mock import patch, Mock, MagicMock

from qilib.configuration_helper import InstrumentAdapterFactory


class TestKeysightE8267DInstrumentAdapter(unittest.TestCase):
    def test_read_and_apply(self):
        with patch('qilib.configuration_helper.adapters.keysight_e8267d_instrument_adapter.Keysight_E8267D') \
                as mock_instrument:
            mock_instrument_instance = MagicMock()
            mock_instrument.return_value = mock_instrument_instance
            mock_instrument_instance.snapshot.return_value = {
                'parameters': {'good_parameter': {'value': 42}}}
            adapter = InstrumentAdapterFactory.get_instrument_adapter('KeysightE8267DInstrumentAdapter', 'fake')
        config = adapter.read()
        adapter.apply(config)
        mock_instrument_instance.set.assert_called_once_with('good_parameter', 42)
