import copy
import unittest
from unittest.mock import patch, MagicMock

from qilib.configuration_helper import InstrumentAdapterFactory, SerialPortResolver


class TestS5iInstrumentAdapter(unittest.TestCase):

    def setUp(self):
        InstrumentAdapterFactory.adapter_instances.clear()

        self.mock_config = {
            'name': 'S5iInstrumentAdapter_spirack1_module3',
            'output_enabled': {
                'value': True,
                'ts': '2019-01-03 16:08:02',
                'raw_value': True,
                '__class__': 'qcodes.instrument.parameter.Parameter',
                'full_name': 'S5iInstrumentAdapterCOM6_MODULE1_output_enabled',
                'name': 'output_enabled',
                'instrument': 'qcodes.instrument_drivers.QuTech.S5i.S5i',
                'instrument_name': 'S5iInstrumentAdapterCOM6_MODULE1',
                'inter_delay': 0,
                'label': 'RF output enabled',
                'post_delay': 0,
                'unit': '',
                'vals': '<Boolean>'
            },
            'frequency_stepsize': {
                'value': 1000000.0,
                'ts': '2019-01-03 16:08:02',
                'raw_value': 1000000.0,
                '__class__': 'qcodes.instrument.parameter.Parameter',
                'full_name': 'S5iInstrumentAdapterCOM6_MODULE1_frequency_stepsize',
                'name': 'frequency_stepsize',
                'instrument': 'qcodes.instrument_drivers.QuTech.S5i.S5i',
                'instrument_name': 'S5iInstrumentAdapterCOM6_MODULE1',
                'inter_delay': 0,
                'label': 'Frequency stepsize',
                'post_delay': 0,
                'unit': 'Hz',
                'vals': '<Numbers>'
            },
            'frequency': {
                'value': 41000000.0,
                'ts': '2019-01-03 16:08:02',
                'raw_value': 41000000.0,
                '__class__': 'qcodes.instrument.parameter.Parameter',
                'full_name': 'S5iInstrumentAdapterCOM6_MODULE1_frequency',
                'name': 'frequency',
                'instrument': 'qcodes.instrument_drivers.QuTech.S5i.S5i',
                'instrument_name': 'S5iInstrumentAdapterCOM6_MODULE1',
                'inter_delay': 0,
                'label': 'Frequency',
                'post_delay': 0,
                'unit': 'Hz',
                'vals': '<Numbers 40000000.0<=v<=4000000000.0>'
            },
            'power': {
                'value': 10,
                'ts': '2019-01-03 16:08:02',
                'raw_value': 10,
                '__class__': 'qcodes.instrument.parameter.Parameter',
                'full_name': 'S5iInstrumentAdapterCOM6_MODULE1_power',
                'name': 'power',
                'instrument': 'qcodes.instrument_drivers.QuTech.S5i.S5i',
                'instrument_name': 'S5iInstrumentAdapterCOM6_MODULE1',
                'inter_delay': 0,
                'label': 'Output Power',
                'post_delay': 0,
                'unit': 'dBm',
                'vals': '<Numbers -14<=v<=20>'
            }
        }

    def __check_qcodes_parameter(self, adapter, name, config):
        parameter = getattr(adapter.instrument, name)
        self.assertEqual(parameter(), config[name]['value'])
        self.assertEqual(parameter.raw_value, config[name]['raw_value'])
        self.assertEqual(parameter.unit, config[name]['unit'])
        self.assertEqual(parameter.label, config[name]['label'])
        if 'vals' in config[name]:
            self.assertEqual(str(parameter.vals), config[name]['vals'])

    def test_apply_config(self):
        with patch('qilib.configuration_helper.adapters.spi_rack_instrument_adapter.SPI_rack') as spi_mock, \
                patch('qcodes_contrib_drivers.drivers.QuTech.S5i.S5i_module') as s5i_module_mock:
            address = 'spirack1_module3'
            adapter_name = 'S5iInstrumentAdapter'
            instrument_name = '{0}_{1}'.format(adapter_name, address)
            SerialPortResolver.serial_port_identifiers = {'spirack1': 'COMnumber_test'}
            s5i_adapter = InstrumentAdapterFactory.get_instrument_adapter(adapter_name, address)

            spi_mock.assert_called()
            s5i_module_mock.assert_called()
            self.assertEqual(address, s5i_adapter.address)
            self.assertEqual(s5i_module_mock(), s5i_adapter.instrument.s5i)
            self.assertEqual(instrument_name, s5i_adapter.instrument.name)

            s5i_adapter.apply(self.mock_config)
            s5i_adapter.instrument.s5i.enable_output_soft.assert_called_with(True)
            s5i_adapter.instrument.s5i.set_stepsize.assert_called_with(1000000.0)
            s5i_adapter.instrument.s5i.set_frequency.assert_called_with(41000000.0)
            s5i_adapter.instrument.s5i.set_output_power.assert_called_with(10)

            parameter_name = 'frequency'
            self.mock_config[parameter_name]['value'] = None
            error_message = f'The following parameter\(s\) of .* \[\'{parameter_name}\'\]\!'
            self.assertRaisesRegex(ValueError, error_message, s5i_adapter.apply, self.mock_config)

            s5i_adapter.instrument.close()

    def test_read_config(self):
        with patch('qilib.configuration_helper.adapters.spi_rack_instrument_adapter.SPI_rack') as spi_mock, \
                patch('qcodes_contrib_drivers.drivers.QuTech.S5i.S5i_module') as s5i_module_mock:
            address = 'spirack1_module3'
            SerialPortResolver.serial_port_identifiers = {'spirack1': 'COMnumber_test'}
            s5i_adapter = InstrumentAdapterFactory.get_instrument_adapter('S5iInstrumentAdapter', address)
            mock_config = copy.deepcopy(self.mock_config)

            spi_mock.assert_called()
            s5i_module_mock.assert_called()
            self.assertEqual(address, s5i_adapter.address)
            self.assertEqual(s5i_adapter.instrument.s5i, s5i_module_mock())

            identity = 'IDN'
            mock_config[identity] = 'version_test'
            mocked_snapshot = {'name': 'some_s5i', 'parameters': mock_config.copy()}
            s5i_adapter.instrument.snapshot = MagicMock(return_value=mocked_snapshot)

            config = s5i_adapter.read()
            mock_config.pop(identity)
            self.assertTrue(identity not in config.keys())
            self.assertDictEqual(self.mock_config, config)

            s5i_adapter.instrument.close()
