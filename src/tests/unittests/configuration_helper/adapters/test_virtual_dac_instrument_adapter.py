import sys
import unittest
from unittest.mock import MagicMock, patch

from qilib.configuration_helper import InstrumentAdapterFactory, SerialPortResolver
from qilib.utils import PythonJsonStructure

sys.modules['qtt.instrument_drivers.gates'] = MagicMock()
import qilib
from qilib.configuration_helper.adapters.virtual_dac_instrument_adapter import VirtualDACInstrumentAdapter
from tests.test_data.dummy_instrument_adapter import DummyInstrumentAdapter
from tests.test_data.virtual_dac_snapshot import snapshot


class TestVirtualDACInstrumentAdapter(unittest.TestCase):
    def setUp(self):
        SerialPortResolver.serial_port_identifiers['spirack3'] = 'COM3'

    def test_apply(self):
        qilib.configuration_helper.adapters.DummyInstrumentAdapter = DummyInstrumentAdapter
        dummy_adapter = InstrumentAdapterFactory.get_instrument_adapter('DummyInstrumentAdapter', 'some_address')
        dummy_adapter.instrument.amplitude(1)
        dummy_adapter.instrument.frequency(1)
        dummy_adapter.instrument.enable_output(False)
        mock_virtual_dac_instance = MagicMock()
        with patch('qilib.configuration_helper.adapters.virtual_dac_instrument_adapter.VirtualDAC') as mock_virtual_dac:
            mock_virtual_dac.return_value = mock_virtual_dac_instance
            adapter = VirtualDACInstrumentAdapter('spirack3_module3')
            mock_virtual_dac.assert_called()
        config = PythonJsonStructure()
        config['config'] = snapshot['parameters']
        config['boundaries'] = {'P1': (-10, 10)}
        config['gate_map'] = {'P1': (0, 1)}
        config['instruments'] = {dummy_adapter.name: {'address': 'some_address',
                                                      'adapter_class_name': 'DummyInstrumentAdapter',
                                                      'config': {'amplitude': {'value': 1e-3},
                                                                 'frequency': {'value': 130e6},
                                                                 'enable_output': {'value': True}}}}
        adapter.apply(config)

        mock_virtual_dac_instance.set_boundaries.assert_called_with({'P1': (-10, 10)})
        mock_virtual_dac_instance.add_instruments.assert_called_with([dummy_adapter.instrument])
        self.assertDictEqual({'P1': (0, 1)}, mock_virtual_dac_instance.gate_map)
        self.assertEqual(1e-3, dummy_adapter.instrument.amplitude())
        self.assertEqual(130e6, dummy_adapter.instrument.frequency())
        self.assertTrue(dummy_adapter.instrument.enable_output())

        dummy_adapter.close_instrument()

    def test_read(self):
        qilib.configuration_helper.adapters.DummyInstrumentAdapter = DummyInstrumentAdapter
        dummy_adapter = InstrumentAdapterFactory.get_instrument_adapter('DummyInstrumentAdapter', 'other_address')
        dummy_adapter.instrument.amplitude(42)
        dummy_adapter.instrument.frequency(5)
        dummy_adapter.instrument.enable_output(True)
        mock_virtual_dac_instance = MagicMock()
        mock_virtual_dac_instance.get_boundaries.return_value = {'C1': (-4000, 4000)}
        mock_virtual_dac_instance.snapshot.return_value = snapshot

        bootstrap_config = PythonJsonStructure(boundaries={}, gate_map={'C1': (0, 2)}, config={})
        bootstrap_config['instruments'] = {
            'DummyInstrumentAdapter_other_address': {
                'address': 'other_address',
                'adapter_class_name': 'DummyInstrumentAdapter',
                'config': {}}}

        with patch('qilib.configuration_helper.adapters.virtual_dac_instrument_adapter.VirtualDAC') as mock_virtual_dac:
            mock_virtual_dac.return_value = mock_virtual_dac_instance
            adapter = VirtualDACInstrumentAdapter('spirack3_module3')
            adapter.apply(bootstrap_config)
        config = adapter.read()
        self.assertIn('C1', config['config'])
        self.assertIn('C2', config['config'])
        self.assertIn('C3', config['config'])
        self.assertIn('rc_times', config['config'])
        self.assertDictEqual(config['boundaries'], {'C1': (-4000, 4000)})
        self.assertDictEqual(config['gate_map'], {'C1': (0, 2)})
        self.assertEqual(config['instruments'][dummy_adapter.name]['address'], 'other_address')
        self.assertEqual(config['instruments'][dummy_adapter.name]['adapter_class_name'], 'DummyInstrumentAdapter')
        self.assertEqual(dummy_adapter.instrument.amplitude(),
                         config['instruments'][dummy_adapter.name]['config']['amplitude']['value'])
        self.assertEqual(dummy_adapter.instrument.frequency(),
                         config['instruments'][dummy_adapter.name]['config']['frequency']['value'])
        self.assertEqual(dummy_adapter.instrument.enable_output(),
                         config['instruments'][dummy_adapter.name]['config']['enable_output']['value'])

        dummy_adapter.close_instrument()
