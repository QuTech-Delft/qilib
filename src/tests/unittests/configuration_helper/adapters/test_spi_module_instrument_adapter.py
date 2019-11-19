from unittest import TestCase
from unittest.mock import patch, call

from qilib.configuration_helper import InstrumentAdapterFactory, SerialPortResolver
from qilib.configuration_helper.adapters import SpiModuleInstrumentAdapter


class TestSpiModuleInstrumentAdapter(TestCase):

    def setUp(self):
        InstrumentAdapterFactory.adapter_instances = {}

    def test_create_has_invalid_address(self):
        invalid_address = 'ItIsInvalid'
        error_text = "Invalid address format. ({} != <spi_name>:module<module_number>) ".format(invalid_address)
        with self.assertRaises(ValueError, msg=error_text):
            _ = SpiModuleInstrumentAdapter(invalid_address)

    def test_spi_module_factory_creates_single_instance(self):
        with patch('qilib.configuration_helper.adapters.spi_rack_instrument_adapter.SPI_rack') as spi_mock:
            get_adapter = InstrumentAdapterFactory.get_instrument_adapter
            SerialPortResolver.serial_port_identifiers = {'spirack1': 'COM_1'}

            adapter_1 = get_adapter('SpiModuleInstrumentAdapter', 'spirack1_module1')
            adapter_2 = get_adapter('SpiModuleInstrumentAdapter', 'spirack1_module1')
            self.assertEqual(adapter_1, adapter_2)

            spi_mock.assert_called_with('COM_1', baud='115200', timeout=1)

    def test_spi_module_factory_new_spirack(self):
        with patch('qilib.configuration_helper.adapters.spi_rack_instrument_adapter.SPI_rack') as spi_mock:
            get_adapter = InstrumentAdapterFactory.get_instrument_adapter
            SerialPortResolver.serial_port_identifiers = {'spirack1': 'COM_1', 'spirack2': 'COM_2'}

            adapter_1 = get_adapter('SpiModuleInstrumentAdapter', 'spirack1_module1')
            adapter_2 = get_adapter('SpiModuleInstrumentAdapter', 'spirack2_module1')
            self.assertNotEqual(adapter_1, adapter_2)

            calls = [call('COM_1', baud='115200', timeout=1), call('COM_2', baud='115200', timeout=1)]
            spi_mock.assert_has_calls(calls)

            adapter_3 = get_adapter('SpiModuleInstrumentAdapter', 'spirack1_module1')
            self.assertEqual(adapter_1, adapter_3)

    def test_spi_module_factory_new_module(self):
        with patch('qilib.configuration_helper.adapters.spi_rack_instrument_adapter.SPI_rack') as spi_mock:
            get_adapter = InstrumentAdapterFactory.get_instrument_adapter
            SerialPortResolver.serial_port_identifiers = {'spirack1': 'COM_1'}

            adapter_1 = get_adapter('SpiModuleInstrumentAdapter', 'spirack1_module1')
            adapter_2 = get_adapter('SpiModuleInstrumentAdapter', 'spirack1_module2')
            self.assertNotEqual(adapter_1, adapter_2)

            spi_mock.assert_called_with('COM_1', baud='115200', timeout=1)

            adapter_3 = get_adapter('SpiModuleInstrumentAdapter', 'spirack1_module1')
            self.assertEqual(adapter_1, adapter_3)
