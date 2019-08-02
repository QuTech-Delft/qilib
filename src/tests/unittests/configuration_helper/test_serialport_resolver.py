from unittest import TestCase
from unittest.mock import MagicMock, patch

from qilib.configuration_helper import adapters, SerialPortResolver, InstrumentAdapterFactory


class TestSerialPortResolver(TestCase):

    def setUp(self):
        InstrumentAdapterFactory.instrument_adapters.clear()

    def test_get_serialport_adapter_invalid_key(self):
        adapters.InstrumentAdapter = MagicMock()
        SerialPortResolver.serial_port_identifiers = {'spirack1': 'COMnumber_test'}

        invalid_identifier = 'spirack2'
        error_text = "No such identifier {0} in SerialPortResolver".format(invalid_identifier)
        self.assertRaisesRegex(ValueError, error_text, SerialPortResolver.get_serial_port_adapter,
                               'InstrumentAdapter', invalid_identifier)

    def test_get_serialport_adapter_valid_key(self):
        with patch('qilib.configuration_helper.adapters.spi_rack_instrument_adapter.SPI_rack') as spi_mock:
            SerialPortResolver.serial_port_identifiers = {'spirack1': 'COMnumber_test'}

            identifier = 'spirack1'
            adapter = SerialPortResolver.get_serial_port_adapter('SpiRackInstrumentAdapter', identifier)
            spi_mock.assert_called_once_with('COMnumber_test', baud='115200', timeout=1)
            self.assertIsInstance(adapter.instrument, MagicMock)
