import unittest
from unittest.mock import patch, MagicMock

import numpy as np
import zhinst

from qilib.configuration_helper import InstrumentAdapterFactory


class TestZIUHFLIInstrumentAdapter(unittest.TestCase):
    def test_read_apply(self):
        with patch.object(zhinst.utils, 'create_api_session', return_value=3 * (MagicMock(),)), \
             patch('qilib.configuration_helper.adapters.common_instrument_adapter.logging') as logger_mock:
            adapter = InstrumentAdapterFactory.get_instrument_adapter('ZIUHFLIInstrumentAdapter', 'dev4242')
            adapter.instrument.scope_trig_level(0.2)
            trigger_level = adapter.instrument.scope_trig_level.raw_value
            self.assertEqual(0.2, trigger_level)
            config = adapter.read()

            self.assertTrue(all(['val_mapping' not in config[key] for key in config.keys()]))

            adapter.instrument.scope_trig_level(0.7)
            trigger_level = adapter.instrument.scope_trig_level.raw_value
            self.assertEqual(0.7, trigger_level)

            adapter.apply(config)
            trigger_level = adapter.instrument.scope_trig_level.raw_value
            self.assertEqual(0.2, trigger_level)

            logger_mock.warning.assert_called_with('Some parameter values of ZIUHFLIInstrumentAdapter_dev4242 are'
                                                   ' None and will not be set!')

        adapter.instrument.close()

    def test_int64_convert_to_int(self):
        with patch.object(zhinst.utils, 'create_api_session', return_value=3 * (MagicMock(),)), \
             patch('qilib.configuration_helper.adapters.common_instrument_adapter.logging') as logger_mock:
            adapter = InstrumentAdapterFactory.get_instrument_adapter('ZIUHFLIInstrumentAdapter', 'dev4142')

            adapter.instrument.scope_trig_level(np.int64(1))
            self.assertIsInstance(adapter.instrument.scope_trig_level.raw_value, np.int64)
            adapter.instrument.scope_trig_hystabsolute(np.int64(2))
            self.assertIsInstance(adapter.instrument.scope_trig_hystabsolute.raw_value, np.int64)

            config = adapter.read()
            adapter.apply(config)

            for parameter in adapter.instrument.parameters.values():
                if hasattr(parameter, 'raw_value'):
                    self.assertNotIsInstance(parameter.raw_value, np.int64)
            logger_mock.warning.assert_called_with('Some parameter values of ZIUHFLIInstrumentAdapter_dev4142 are'
                                                   ' None and will not be set!')
            adapter.instrument.close()
