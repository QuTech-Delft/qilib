from unittest import TestCase
from unittest.mock import patch, MagicMock

from qilib.configuration_helper import InstrumentAdapterFactory
from qilib.utils import PythonJsonStructure


class TestSpiRackInstrumentAdapter(TestCase):

    def setUp(self):
        InstrumentAdapterFactory.adapter_instances = {}
        self.serial_port_settings = PythonJsonStructure(MagicMock(spec=dict()))
        self.mock_config = PythonJsonStructure({
            'version': 1.23,
            'temperature': 293.4,
            'battery': 'OK',
            'serialport': self.serial_port_settings
        })

    def test_apply_config(self):
        with patch('qilib.configuration_helper.adapters.spi_rack_instrument_adapter.SPI_rack') as spi_mock:
            address = 'COM_testport_apply'
            spi_adapter = InstrumentAdapterFactory.get_instrument_adapter('SpiRackInstrumentAdapter', address)

            self.assertIsInstance(spi_adapter.instrument, MagicMock)
            spi_mock.assert_called_once_with(address, baud='115200', timeout=1)

            spi_adapter.apply(self.mock_config)
            spi_adapter.instrument.apply_settings.assert_called_once_with(self.serial_port_settings)

    def test_read_config(self):
        with patch('qilib.configuration_helper.adapters.spi_rack_instrument_adapter.SPI_rack') as spi_mock:
            address = 'COM_testport_read'
            spi_adapter = InstrumentAdapterFactory.get_instrument_adapter('SpiRackInstrumentAdapter', address)

            spi_mock.assert_called()
            self.assertIsInstance(spi_adapter.instrument, MagicMock)
            spi_mock.assert_called_once_with(address, baud='115200', timeout=1)

            spi_adapter.instrument.get_firmware_version.return_value = self.mock_config['version']
            spi_adapter.instrument.get_temperature.return_value = self.mock_config['temperature']
            spi_adapter.instrument.get_battery.return_value = self.mock_config['battery']
            spi_adapter.instrument.get_settings.return_value = self.serial_port_settings

            config = spi_adapter.read()
            self.assertDictEqual(self.mock_config, config)

    def test_filter_parameters(self):
        with patch('qilib.configuration_helper.adapters.spi_rack_instrument_adapter.SPI_rack') as spi_mock:
            address = 'COM_testport_read'
            spi_adapter = InstrumentAdapterFactory.get_instrument_adapter('SpiRackInstrumentAdapter', address)
            parameters = MagicMock()
            reply = spi_adapter._filter_parameters(parameters)
            self.assertEqual(parameters, reply)

    def test_close_instrument(self):
        with patch('qilib.configuration_helper.adapters.spi_rack_instrument_adapter.SPI_rack') as spi_mock:
            address = 'COM_testport_apply'
            spi_adapter = InstrumentAdapterFactory.get_instrument_adapter('SpiRackInstrumentAdapter', address)

            self.assertIsInstance(spi_adapter.instrument, MagicMock)
            spi_mock.assert_called_once_with(address, baud='115200', timeout=1)

            spi_adapter.close_instrument()
            spi_adapter.instrument.close.assert_called_once()
