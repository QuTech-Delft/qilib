import unittest
from unittest.mock import patch, MagicMock

from qilib.configuration_helper.adapters.ami430_instrument_adapter import AMI430InstrumentAdapter, ConfigurationError
from tests.test_data.ami430_snapshot import snapshot, bad_config


class TestAMI430InstrumentAdapter(unittest.TestCase):
    def test_constructor(self):
        with patch('qilib.configuration_helper.adapters.ami430_instrument_adapter.AMI430') as mock_instrument:
            address = '192.168.1.128:7180'
            AMI430InstrumentAdapter(address)
            expected_name = 'AMI430InstrumentAdapter_192.168.1.128:7180'
            mock_instrument.assert_called_with(name=expected_name, address='192.168.1.128', port=7180)

    def test_apply(self):
        mock_ami430 = MagicMock()
        mock_ami430.snapshot.return_value = snapshot
        with patch('qilib.configuration_helper.adapters.ami430_instrument_adapter.AMI430', return_value=mock_ami430):
            address = '192.168.1.128:7180'
            adapter = AMI430InstrumentAdapter(address)
        adapter.apply(snapshot['parameters'])
        mock_ami430.snapshot.assert_called_once_with(True)

    def test_apply_raises_error(self):
        mock_ami430 = MagicMock()
        mock_ami430.snapshot.return_value = snapshot
        with patch('qilib.configuration_helper.adapters.ami430_instrument_adapter.AMI430', return_value=mock_ami430):
            address = '192.168.1.128:7180'
            adapter = AMI430InstrumentAdapter(address)
        error_msg = "Configuration for field_ramp_limit does not match: '20' != '0.1497888'"
        self.assertRaisesRegex(ConfigurationError, error_msg, adapter.apply, bad_config)

    def test_field_difference_raises_error(self):
        mock_ami430 = MagicMock()
        mock_ami430.snapshot.return_value = {'parameters': {'field': {'value': -0.0001205}}}
        with patch('qilib.configuration_helper.adapters.ami430_instrument_adapter.AMI430', return_value=mock_ami430):
            address = '192.168.1.128:7180'
            adapter = AMI430InstrumentAdapter(address)

        error_msg = "Target value for field does not match device value: 0.0098796T != -0.0001205T"
        config = {'field': {'value': 0.0098796}}
        self.assertRaisesRegex(ConfigurationError, error_msg, adapter.apply, config)

        error_msg = "Target value for field does not match device value: -0.0101206T != -0.0001205T"
        config = {'field': {'value': -0.0101206}}
        self.assertRaisesRegex(ConfigurationError, error_msg, adapter.apply, config)

        mock_ami430.snapshot.return_value = {'parameters': {'field': {'value': 0.0001205}}}
        error_msg = "Target value for field does not match device value: -0.0098796T != 0.0001205T"
        config = {'field': {'value': -0.0098796}}
        self.assertRaisesRegex(ConfigurationError, error_msg, adapter.apply, config)
