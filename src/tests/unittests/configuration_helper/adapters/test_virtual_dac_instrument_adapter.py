import sys
import unittest
from unittest.mock import MagicMock, patch

from qilib.configuration_helper import InstrumentAdapterFactory

sys.modules['qtt.instrument_drivers.gates'] = MagicMock()
import qilib
from qilib.configuration_helper.adapters.virtual_dac_instrument_adapter import VirtualDACInstrumentAdapter
from tests.test_data.dummy_instrument_adapter import DummyInstrumentAdapter
from tests.test_data.virtual_dac_snapshot import snapshot


class TestVirtualDACInstrumentAdapter(unittest.TestCase):
    def test_apply(self):
        qilib.configuration_helper.adapters.DummyInstrumentAdapter = DummyInstrumentAdapter
        dummy_adapter = InstrumentAdapterFactory.get_instrument_adapter('DummyInstrumentAdapter', 'some_name')
        mock_virtual_dac_instance = MagicMock()
        with patch('qilib.configuration_helper.adapters.virtual_dac_instrument_adapter.VirtualDAC') as mock_virtual_dac:
            mock_virtual_dac.return_value = mock_virtual_dac_instance
            adapter = VirtualDACInstrumentAdapter('address')
            mock_virtual_dac.assert_called()
        config = snapshot['parameters']
        config['boundaries'] = {'P1': (-10, 10)}
        config['gate_map'] = {'P1': (0, 1)}
        config['instruments'] = [('DummyInstrumentAdapter', 'some_name')]
        adapter.apply(config)

        mock_virtual_dac_instance.set_boundaries.assert_called_with({'P1': (-10, 10)})
        mock_virtual_dac_instance.add_instruments.assert_called_with([dummy_adapter.instrument])
        self.assertDictEqual({'P1': (0, 1)}, mock_virtual_dac_instance.gate_map)
