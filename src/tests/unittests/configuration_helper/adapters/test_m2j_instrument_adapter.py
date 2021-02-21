import copy
import unittest
from unittest.mock import patch, MagicMock

from qcodes_contrib_drivers.drivers.QuTech.M2j import M2j

from qilib.configuration_helper import (InstrumentAdapterFactory,
                                     SerialPortResolver)


class TestM2jInstrumentAdapter(unittest.TestCase):

    def setUp(self):
        InstrumentAdapterFactory.adapter_instances.clear()

        self.mock_config = {
            'name': 'M2jInstrumentAdapter_spirack1_module3',
            'gain': {
                'value': 35,
                'ts': '2019-01-03 16:09:19',
                'raw_value': 35,
                '__class__': 'qcodes.instrument.parameter.Parameter',
                'full_name': 'M2jInstrumentAdapterCOM6_MODULE1_gain',
                'instrument': 'qcodes_contrib_drivers.drivers.QuTech.M2j.M2j',
                'instrument_name': 'M2jInstrumentAdapterCOM6_MODULE1',
                'post_delay': 0,
                'inter_delay': 0,
                'unit': 'dB',
                'name': 'gain',
                'vals': '<Numbers 33<=v<=55>',
                'label': 'gain'
            },
            'RF_level': {
                'value': 4095,
                'ts': '2019-01-03 16:09:19',
                'raw_value': 4095,
                '__class__': 'qcodes.instrument.parameter.Parameter',
                'full_name': 'M2jInstrumentAdapterCOM6_MODULE1_RF_level',
                'instrument': 'qcodes_contrib_drivers.drivers.QuTech.M2j.M2j',
                'instrument_name': 'M2jInstrumentAdapterCOM6_MODULE1',
                'post_delay': 0,
                'inter_delay': 0,
                'unit': 'dBm',
                'name': 'RF_level',
                'label': 'RF level'
            }
        }

    def test_apply_config(self):
        with patch('qilib.configuration_helper.adapters.spi_rack_instrument_adapter.SPI_rack') as spi_mock, \
         patch('qcodes_contrib_drivers.drivers.QuTech.M2j.M2j_module') as m2j_module_mock:
            address = 'spirack1_module3'
            adapter_name = 'M2jInstrumentAdapter'
            instrument_name = '{0}_{1}'.format(adapter_name, address)
            SerialPortResolver.serial_port_identifiers = {'spirack1': 'COMnumber_test'}
            m2j_adapter = InstrumentAdapterFactory.get_instrument_adapter(adapter_name, address)

            spi_mock.assert_called()
            m2j_module_mock.assert_called()
            self.assertEqual(address, m2j_adapter.address)
            self.assertIsInstance(m2j_adapter.instrument, M2j)
            self.assertEqual(instrument_name, m2j_adapter.instrument.name)
            self.assertIsNone(m2j_adapter.instrument.gain())
            gain = 35
            ref_scale = 3325

            m2j_adapter.apply(self.mock_config)
            self.assertEqual(gain, m2j_adapter.instrument.gain())
            m2j_adapter.instrument.m2j.get_level.assert_not_called()
            m2j_adapter.instrument.m2j.set_gain.assert_called_once_with(ref_scale)

            parameter_name = 'gain'
            self.mock_config[parameter_name]['value'] = None
            error_message = f'The following parameter\(s\) of .* \[\'{parameter_name}\'\]\!'
            self.assertRaisesRegex(ValueError, error_message, m2j_adapter.apply, self.mock_config)

            m2j_adapter.instrument.close()

    def test_read_config(self):
        with patch('qilib.configuration_helper.adapters.spi_rack_instrument_adapter.SPI_rack') as spi_mock, \
         patch('qcodes_contrib_drivers.drivers.QuTech.M2j.M2j_module') as m2j_module_mock:
            address = 'spirack1_module3'
            SerialPortResolver.serial_port_identifiers = {'spirack1': 'COMnumber_test'}
            m2j_adapter = InstrumentAdapterFactory.get_instrument_adapter('M2jInstrumentAdapter', address)
            mock_config = copy.deepcopy(self.mock_config)

            spi_mock.assert_called()
            m2j_module_mock.assert_called()
            self.assertEqual(address, m2j_adapter.address)
            self.assertEqual(m2j_adapter.instrument.m2j, m2j_module_mock())

            identity = 'IDN'
            mock_config[identity] = 'version_test'
            mocked_snapshot = {'name': 'd5a', 'parameters': mock_config.copy()}
            m2j_adapter.instrument.snapshot = MagicMock(return_value=mocked_snapshot)

            config = m2j_adapter.read()
            mock_config.pop(identity)
            self.assertTrue(identity not in config.keys())
            self.assertDictEqual(mock_config, config)

            m2j_adapter.instrument.close()
