import unittest
from unittest.mock import patch, MagicMock

from qilib.configuration_helper import InstrumentAdapterFactory, SerialPortResolver


class TestD5aInstrumentAdapter(unittest.TestCase):

    def setUp(self):
        InstrumentAdapterFactory.instrument_adapters = {}
        self.mock_config = {
            'remote_settings': {
                'value': 64,
                'ts': '2019-01-03 16:08:34',
                'raw_value': 64,
                '__class__': 'qcodes.instrument.parameter.Parameter',
                'full_name': 'F1dInstrumentAdapterCOM6_MODULE1_remote_settings',
                'unit': '',
                'name': 'remote_settings',
                'post_delay': 0,
                'instrument': 'qcodes.instrument_drivers.QuTech.F1d.F1d',
                'instrument_name': 'F1dInstrumentAdapterCOM6_MODULE1',
                'label': 'Remote settings', 'inter_delay': 0
            },
            'IQ_filter': {
                'value': 3,
                'ts': '2019-01-03 16:08:34',
                'raw_value': 3,
                '__class__': 'qcodes.instrument.parameter.Parameter',
                'full_name': 'F1dInstrumentAdapterCOM6_MODULE1_IQ_filter',
                'unit': 'MHz',
                'name': 'IQ_filter',
                'post_delay': 0,
                'instrument': 'qcodes.instrument_drivers.QuTech.F1d.F1d',
                'instrument_name': 'F1dInstrumentAdapterCOM6_MODULE1',
                'label': 'IQ filter',
                'inter_delay': 0,
                'vals': '<Enum: {1, 10, 3}>'
            },
            'I_gain': {
                'value': 'low',
                'ts': '2019-01-03 16:08:34',
                'raw_value': 'low',
                '__class__': 'qcodes.instrument.parameter.Parameter',
                'full_name': 'F1dInstrumentAdapterCOM6_MODULE1_I_gain',
                'unit': '', 'name': 'I_gain',
                'post_delay': 0,
                'instrument': 'qcodes.instrument_drivers.QuTech.F1d.F1d',
                'instrument_name': 'F1dInstrumentAdapterCOM6_MODULE1',
                'label': 'I gain',
                'inter_delay': 0,
                'vals': "<Enum: {'high', 'low', 'mid'}>"
            },
            'Q_gain': {
                'value': 'high',
                'ts': '2019-01-03 16:08:34',
                'raw_value': 'high',
                '__class__': 'qcodes.instrument.parameter.Parameter',
                'full_name': 'F1dInstrumentAdapterCOM6_MODULE1_Q_gain',
                'unit': '',
                'name': 'Q_gain',
                'post_delay': 0,
                'instrument': 'qcodes.instrument_drivers.QuTech.F1d.F1d',
                'instrument_name': 'F1dInstrumentAdapterCOM6_MODULE1',
                'label': 'Q gain',
                'inter_delay': 0,
                'vals': "<Enum: {'high', 'low', 'mid'}>"
            },
            'RF_level': {
                'value': 9.589131159667502,
                'ts': '2019-01-03 16:08:34',
                'raw_value': 9.589131159667502,
                '__class__': 'qcodes.instrument.parameter.Parameter',
                'full_name': 'F1dInstrumentAdapterCOM6_MODULE1_RF_level',
                'unit': 'dBm',
                'name': 'RF_level',
                'post_delay': 0,
                'instrument': 'qcodes.instrument_drivers.QuTech.F1d.F1d',
                'instrument_name': 'F1dInstrumentAdapterCOM6_MODULE1',
                'label': 'RF level',
                'inter_delay': 0
            },
            'LO_level': {
                'value': 19.589131159667502,
                'ts': '2019-01-03 16:08:34',
                'raw_value': 19.589131159667502,
                '__class__': 'qcodes.instrument.parameter.Parameter',
                'full_name': 'F1dInstrumentAdapterCOM6_MODULE1_LO_level',
                'unit': 'dBm',
                'name': 'LO_level',
                'post_delay': 0,
                'instrument': 'qcodes.instrument_drivers.QuTech.F1d.F1d',
                'instrument_name': 'F1dInstrumentAdapterCOM6_MODULE1',
                'label': 'LO level',
                'inter_delay': 0
            },
            'enable_remote': {
                'value': True,
                'ts': '2019-01-03 16:08:34',
                'raw_value': True,
                '__class__': 'qcodes.instrument.parameter.Parameter',
                'full_name': 'F1dInstrumentAdapterCOM6_MODULE1_enable_remote',
                'unit': '',
                'name': 'enable_remote',
                'post_delay': 0,
                'instrument': 'qcodes.instrument_drivers.QuTech.F1d.F1d',
                'instrument_name': 'F1dInstrumentAdapterCOM6_MODULE1',
                'label': 'Enable remote',
                'inter_delay': 0
            }
        }

    def test_apply_config(self):
        with patch('qilib.configuration_helper.adapters.spi_rack_instrument_adapter.SPI_rack') as spi_mock, \
         patch('qilib.configuration_helper.adapters.common_instrument_adapter.logging') as logger_mock, \
         patch('qcodes.instrument_drivers.QuTech.F1d.F1d_module') as f1d_module_mock:
            address = 'spirack1_module3'
            adapter_name = 'F1dInstrumentAdapter'
            instrument_name = '{0}_{1}'.format(adapter_name, address)
            SerialPortResolver.serial_port_identifiers = {'spirack1': 'COMnumber_test'}
            f1d_adapter = InstrumentAdapterFactory.get_instrument_adapter(adapter_name, address)

            spi_mock.assert_called()
            f1d_module_mock.assert_called()
            self.assertEqual(address, f1d_adapter.address)
            self.assertEqual(f1d_module_mock(), f1d_adapter.instrument.f1d)
            self.assertEqual(instrument_name, f1d_adapter.instrument.name)

            f1d_adapter.apply(self.mock_config)
            logger_mock.assert_not_called()
            f1d_adapter.instrument.f1d.set_IQ_filter.assert_called_with(3)
            f1d_adapter.instrument.f1d.set_I_gain.assert_called_with('low')
            f1d_adapter.instrument.f1d.set_Q_gain.assert_called_with('high')
            f1d_adapter.instrument.f1d.enable_remote.assert_called_with(True)

            self.mock_config['Q_gain']['value'] = None
            f1d_adapter.apply(self.mock_config)
            warning_text = 'Some parameter values of {} are None and will not be set!'.format(instrument_name)
            logger_mock.warning.assert_called_once_with(warning_text)

            f1d_adapter.instrument.close()

    def test_read_config(self):
        with patch('qilib.configuration_helper.adapters.spi_rack_instrument_adapter.SPI_rack') as spi_mock, \
         patch('qcodes.instrument_drivers.QuTech.F1d.F1d_module') as f1d_module_mock:
            address = 'spirack1_module3'
            SerialPortResolver.serial_port_identifiers = {'spirack1': 'COMnumber_test'}
            f1d_adapter = InstrumentAdapterFactory.get_instrument_adapter('F1dInstrumentAdapter', address)

            spi_mock.assert_called()
            f1d_module_mock.assert_called()
            self.assertEqual(address, f1d_adapter.address)
            self.assertEqual(f1d_adapter.instrument.f1d, f1d_module_mock())

            identity = 'IDN'
            self.mock_config[identity] = 'version_test'
            mocked_snapshot = {'parameters': self.mock_config}
            f1d_adapter.instrument.snapshot = MagicMock(return_value=mocked_snapshot)

            config = f1d_adapter.read()
            self.assertTrue(identity not in config.keys())
            self.assertDictEqual(self.mock_config, config)
            f1d_adapter.instrument.close()
