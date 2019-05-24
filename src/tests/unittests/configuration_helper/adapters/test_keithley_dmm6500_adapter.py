import unittest
from unittest.mock import patch, Mock

from qilib.configuration_helper.adapters import Keithley6500InstrumentAdapter


class TestKeithley6500InstrumentAdapter(unittest.TestCase):
    def test_constructor(self):
        with patch('qilib.configuration_helper.adapters.keithley_dmm6500_adapter.requests') as mock_requests, \
                patch('qilib.configuration_helper.adapters.keithley_dmm6500_adapter.Keithley_6500') as mock_keithley:
            expected_name = 'Keithley6500InstrumentAdapter_TCPIP0::192.168.1.127::inst0::INSTR'
            Keithley6500InstrumentAdapter('TCPIP0::192.168.1.127::inst0::INSTR')
            mock_keithley.assert_called_with(expected_name, 'TCPIP0::192.168.1.127::inst0::INSTR')
            mock_requests.get.assert_called_once_with('http://192.168.1.127/')

    def test_read(self):
        fake_parameters = {'fake_parameter': {'value': 'not_relevant'}}
        fake_snapshot = {'parameters': fake_parameters}
        instrument_instance = Mock()
        instrument_instance.snapshot.return_value = fake_snapshot
        with patch('qilib.configuration_helper.adapters.keithley_dmm6500_adapter.requests'), \
             patch('qilib.configuration_helper.adapters.keithley_dmm6500_adapter.Keithley_6500',
                   return_value=instrument_instance):
            adapter = Keithley6500InstrumentAdapter('TCPIP0::192.168.1.127::inst0::INSTR')
            config = adapter.read()
            self.assertDictEqual(fake_parameters, config)
