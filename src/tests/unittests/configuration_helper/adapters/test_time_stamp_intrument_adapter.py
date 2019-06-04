import unittest
import sys
from unittest.mock import MagicMock, patch

sys.modules['qtt.instrument_drivers.TimeStamp'] = MagicMock()
from qilib.configuration_helper.adapters.time_stamp_instrument_adapter import TimeStampInstrumentAdapter


class TestTimeStampInstrumentAdapter(unittest.TestCase):
    def test_read_returns_empty_pjs(self):
        with patch('qilib.configuration_helper.adapters.time_stamp_instrument_adapter.TimeStampInstrument'):
            adapter = TimeStampInstrumentAdapter('some_address')
        config = adapter.read()
        self.assertDictEqual({}, config)
