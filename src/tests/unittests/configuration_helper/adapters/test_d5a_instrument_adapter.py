import unittest
from unittest.mock import patch, MagicMock

from qilib.configuration_helper import InstrumentAdapterFactory, SerialPortResolver
from qilib.configuration_helper.adapters import D5aInstrumentAdapter
from qilib.configuration_helper.adapters.d5a_instrument_adapter import SpanValueError


class TestD5aInstrumentAdapter(unittest.TestCase):

    def setUp(self):
        InstrumentAdapterFactory.instrument_adapters = {}
        self.mock_config = {
            'dac1': {
                'value': 39.97802734375, 'ts': '2019-01-03 16:06:36',
                'raw_value': 39.97802734375, '__class__': 'qcodes.instrument.parameter.Parameter',
                'full_name': 'D5aInstrumentAdapterD5a_COM3_MODULE4_dac1', 'inter_delay': 0.05,
                'vals': '<Numbers -4000.0<=v<=4000.0>', 'label': 'DAC 1',
                'name': 'dac1', 'instrument': 'qcodes.instrument_drivers.QuTech.D5a.D5a',
                'instrument_name': 'D5aInstrumentAdapterD5a_COM3_MODULE4', 'step': 20,
                'post_delay': 0, 'unit': 'V'
            },
            'stepsize1': {
                'value': 3.0517578125e-05, 'ts': '2019-01-03 16:06:36',
                'raw_value': 3.0517578125e-05, '__class__': 'qcodes.instrument.parameter.Parameter',
                'full_name': 'D5aInstrumentAdapterD5a_COM3_MODULE4_stepsize1', 'inter_delay': 0,
                'label': 'stepsize1', 'name': 'stepsize1', 'instrument': 'qcodes.instrument_drivers.QuTech.D5a.D5a',
                'instrument_name': 'D5aInstrumentAdapterD5a_COM3_MODULE4', 'post_delay': 0, 'unit': 'V'
            },
            'span1': {
                'value': '4v bi', 'ts': '2019-01-03 16:06:36', 'raw_value': '4v bi',
                '__class__': 'qcodes.instrument.parameter.Parameter',
                'full_name': 'D5aInstrumentAdapterD5a_COM3_MODULE4_span1', 'inter_delay': 0,
                'vals': "<Enum: {'4v uni', '4v bi', '2v bi'}>", 'label': 'span1', 'name': 'span1',
                'instrument': 'qcodes.instrument_drivers.QuTech.D5a.D5a', 'instrument_name':
                'D5aInstrumentAdapterD5a_COM3_MODULE4', 'post_delay': 0, 'unit': ''
            }
        }

    def test_apply_config(self):
        with patch('qilib.configuration_helper.adapters.spi_rack_instrument_adapter.SPI_rack') as spi_mock, \
         patch('qilib.configuration_helper.adapters.common_instrument_adapter.logging') as logger_mock, \
         patch('qcodes.instrument_drivers.QuTech.D5a.D5a_module') as d5a_module_mock:
            range_4volt_bi = 2
            dac_value = 0.03997802734375
            d5a_module_mock.range_4V_bi = range_4volt_bi
            d5a_module_mock().span.__getitem__.return_value = range_4volt_bi
            d5a_module_mock().voltages.__getitem__.return_value = dac_value

            address = 'spirack1_module3'
            adapter_name = 'D5aInstrumentAdapter'
            instrument_name = '{0}_{1}'.format(adapter_name, address)
            SerialPortResolver.serial_port_identifiers = {'spirack1': 'COMnumber_test'}
            d5a_adapter = InstrumentAdapterFactory.get_instrument_adapter(adapter_name, address)

            spi_mock.assert_called()
            d5a_module_mock.assert_called()
            self.assertEqual(address, d5a_adapter.address)
            self.assertEqual(d5a_module_mock(), d5a_adapter.instrument.d5a)
            self.assertEqual(instrument_name, d5a_adapter.instrument.name)

            d5a_adapter.apply(self.mock_config)
            logger_mock.assert_not_called()
            d5a_adapter.instrument.d5a.set_voltage.assert_called_with(0, dac_value)
            d5a_adapter.instrument.d5a.change_span_update.assert_called_with(0, 2)
            d5a_adapter.instrument.d5a.get_stepsize.assert_not_called()
            self.assertEqual(d5a_adapter.instrument.parameters['dac1'].step, 20)
            self.assertEqual(d5a_adapter.instrument.parameters['dac1'].inter_delay, 0.05)
            self.assertEqual(d5a_adapter.instrument.parameters['dac1'].unit, 'V')

            self.mock_config['dac1']['value'] = None
            d5a_adapter.apply(self.mock_config)
            warning_text = 'Some parameter values of {} are None and will not be set!'.format(instrument_name)
            logger_mock.warning.assert_called_once_with(warning_text)

            d5a_adapter.instrument.close()

    def test_incorrect_span_raises_error(self):
        SerialPortResolver.serial_port_identifiers = {'spirack1': 'COMnumber_test'}
        with patch('qilib.configuration_helper.adapters.spi_rack_instrument_adapter.SPI_rack'), \
         patch('qilib.configuration_helper.adapters.d5a_instrument_adapter.D5a') as d5a_mock:
            d5a_mock.span3.return_value = '4v uni'
            error_msg = 'D5a instrument has span unequal to "4v bi"'
            self.assertRaisesRegex(SpanValueError,error_msg, D5aInstrumentAdapter, 'spirack1_module3')

    def test_read_config(self):
        with patch('qilib.configuration_helper.adapters.spi_rack_instrument_adapter.SPI_rack') as spi_mock, \
         patch('qcodes.instrument_drivers.QuTech.D5a.D5a_module') as d5a_module_mock:
            range_4volt_bi = 2
            d5a_module_mock.range_4V_bi = range_4volt_bi
            d5a_module_mock().span.__getitem__.return_value = range_4volt_bi

            address = 'spirack1_module3'
            SerialPortResolver.serial_port_identifiers = {'spirack1': 'COMnumber_test'}
            d5a_adapter = InstrumentAdapterFactory.get_instrument_adapter('D5aInstrumentAdapter', address)

            spi_mock.assert_called()
            d5a_module_mock.assert_called()
            self.assertEqual(address, d5a_adapter.address)
            self.assertEqual(d5a_adapter.instrument.d5a, d5a_module_mock())

            identity = 'IDN'
            self.mock_config[identity] = 'version_test'
            mocked_snapshot = {'parameters': self.mock_config}
            d5a_adapter.instrument.snapshot = MagicMock(return_value=mocked_snapshot)

            config = d5a_adapter.read()
            self.assertTrue(identity not in config.keys())
            self.assertDictEqual(self.mock_config, config)
            d5a_adapter.instrument.close()
