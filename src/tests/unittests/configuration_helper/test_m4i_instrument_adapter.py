from unittest import TestCase
from unittest.mock import MagicMock, patch, call

from qilib.configuration_helper import InstrumentAdapterFactory
from qilib.configuration_helper.adapters import M4iInstrumentAdapter
from tests.test_data.m4i_snapshot import snapshot


class TestD5aInstrumentAdapter(TestCase):

    def setUp(self):
        InstrumentAdapterFactory.instrument_adapters.clear()

    def test_apply(self):
        address = 'spcm0'
        with patch('qilib.configuration_helper.adapters.m4i_instrument_adapter.Spectrum') as spectrum_mock:
            adapter = M4iInstrumentAdapter(address=address)
            adapter.apply(snapshot)

        spectrum_mock.M4i.assert_called_with(f'M4iInstrumentAdapter_{address}', cardid=address)
