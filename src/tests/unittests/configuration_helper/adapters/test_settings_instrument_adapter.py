import sys
from unittest import TestCase
from unittest.mock import MagicMock, patch

sys.modules['qtt.instrument_drivers.settings'] = MagicMock()
from qilib.configuration_helper.adapters.settings_instrument_adapter import SettingsInstrumentAdapter


class TestSettingsInstrumentAdapter(TestCase):
    def test_read_returns_empty_pjs(self):
        with patch('qilib.configuration_helper.adapters.settings_instrument_adapter.SettingsInstrument'):
            adapter = SettingsInstrumentAdapter('some_address')
        config = adapter.read()
        self.assertDictEqual({}, config)
