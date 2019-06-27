import sys
import unittest
from importlib import reload
from unittest.mock import MagicMock, patch

import zhinst
import qilib

from qilib.configuration_helper import InstrumentAdapterFactory
from qilib.utils import PythonJsonStructure

sys.modules['qtt.instrument_drivers.virtualAwg.virtual_awg'] = MagicMock()
sys.modules['qtt.instrument_drivers.virtualAwg.settings'] = MagicMock()
from qilib.configuration_helper import adapters

reload(adapters)

from qilib.configuration_helper.adapters.virtual_awg_instrument_adapter import VirtualAwgInstrumentAdapter


class TestVirtualAwgInstrumentAdapter(unittest.TestCase):
    def test_read(self):
        with patch.object(zhinst.utils, 'create_api_session',
                          return_value=(MagicMock(), MagicMock(), MagicMock())), \
             patch.object(qilib.configuration_helper.adapters.hdawg8_instrument_adapter.ZIHDAWG8,
                          'download_device_node_tree', return_value={}):
            adapter = VirtualAwgInstrumentAdapter('')
            adapter.add_instrument('ZIHDAWG8InstrumentAdapter', 'DEV8048')
            adapter.add_settings({'P1': (0, 4)}, {'m4i_mk': (0, 4, 0)})

            config = adapter.read()

            self.assertIn('instruments', config)
            self.assertEqual(len(config['instruments']), 1)
            name, instrument_config = config['instruments'].popitem()
            self.assertEqual(name, 'ZIHDAWG8InstrumentAdapter_DEV8048')
            self.assertIn('adapter_class_name', instrument_config)
            self.assertIn('address', instrument_config)

            self.assertIn('settings', config)
            self.assertIn('awg_map', config['settings'])

            adapter.close_instrument()

    def test_apply(self):
        with patch.object(zhinst.utils, 'create_api_session',
                          return_value=(MagicMock(), MagicMock(), MagicMock())), \
             patch.object(qilib.configuration_helper.adapters.hdawg8_instrument_adapter.ZIHDAWG8,
                          'download_device_node_tree', return_value={}):
            config = PythonJsonStructure()
            config['instruments'] = PythonJsonStructure()
            config['instruments']['ZIHDAWG8InstrumentAdapter_DEV8048'] = PythonJsonStructure({
                'adapter_class_name': 'ZIHDAWG8InstrumentAdapter',
                'address': 'DEV8048',
                'config': {}
            })
            config['settings'] = PythonJsonStructure({
                'awg_map': {
                    'P1': (0, 1),
                    'P2': (0, 2),
                    'dig_mk': (0, 1, 1)
                },
                'config': {}
            })

            adapter = VirtualAwgInstrumentAdapter('')

            self.assertEqual(adapter.instrument.add_instruments.call_count, 0)
            adapter.apply(config)

            self.assertEqual(adapter.instrument.add_instruments.call_count, 1)
            self.assertEqual(adapter.instrument.settings.awg_map, {'P1': (0, 1),
                                                                   'P2': (0, 2),
                                                                   'dig_mk': (0, 1, 1)
                                                                   })

            adapter.close_instrument()
