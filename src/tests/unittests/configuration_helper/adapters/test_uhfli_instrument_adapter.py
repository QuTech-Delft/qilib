import unittest
from unittest.mock import MagicMock, patch
import sys
import numpy as np
if sys.version_info < (3, 10):    
    import zhinst

from qilib.configuration_helper import InstrumentAdapterFactory


class TestZIUHFLIInstrumentAdapter(unittest.TestCase):

    @unittest.skipIf(sys.version_info >= (3, 10), "zhinst not supported on python 3.10")
    def test_read_apply(self):
        with patch.object(zhinst.utils, 'create_api_session', return_value=3 * (MagicMock(),)):
            adapter = InstrumentAdapterFactory.get_instrument_adapter('ZIUHFLIInstrumentAdapter', 'dev4242')
            adapter.instrument.scope_trig_level(0.2)
            trigger_level = adapter.instrument.scope_trig_level.raw_value
            self.assertEqual(0.2, trigger_level)

            with self.assertLogs(level='ERROR') as log_grabber:
                config = adapter.read()

            expected_regex = "Parameter values of ZIUHFLIInstrumentAdapter_dev4242 are .*"
            self.assertRegex(log_grabber.records[0].message, expected_regex)
            self.assertTrue(all(['val_mapping' not in config[key] for key in config.keys()]))

            adapter.instrument.scope_trig_level(0.7)
            trigger_level = adapter.instrument.scope_trig_level.raw_value
            self.assertEqual(0.7, trigger_level)

            adapter.apply(config)
            trigger_level = adapter.instrument.scope_trig_level.raw_value
            self.assertEqual(0.2, trigger_level)

            parameter_name = 'scope_trig_level'
            config[parameter_name]['value'] = None
            error_message = f'The following parameter\(s\) of .* \[\'{parameter_name}\'\]\!'
            self.assertRaisesRegex(ValueError, error_message, adapter.apply, config)

        adapter.instrument.close()

    @unittest.skipIf(sys.version_info >= (3, 10), "zhinst not supported on python 3.10")
    def test_int64_convert_to_int(self):
        with patch.object(zhinst.utils, 'create_api_session', return_value=3 * (MagicMock(),)):
            adapter = InstrumentAdapterFactory.get_instrument_adapter('ZIUHFLIInstrumentAdapter', 'dev4142')

            adapter.instrument.scope_trig_level(np.int64(1))
            self.assertIsInstance(adapter.instrument.scope_trig_level.raw_value, np.int64)
            adapter.instrument.scope_trig_hystabsolute(np.int64(2))
            self.assertIsInstance(adapter.instrument.scope_trig_hystabsolute.raw_value, np.int64)

            with self.assertLogs(level='ERROR') as log_grabber:
                config = adapter.read()

            expected_regex = "Parameter values of ZIUHFLIInstrumentAdapter_dev4142 are .*"
            self.assertRegex(log_grabber.records[0].message, expected_regex)
            adapter.apply(config)

            for parameter in adapter.instrument.parameters.values():
                if hasattr(parameter, 'raw_value'):
                    self.assertNotIsInstance(parameter.raw_value, np.int64)

        adapter.instrument.close()

    @unittest.skipIf(sys.version_info >= (3, 10), "zhinst not supported on python 3.10")
    def test_filtered_parameters(self):
        with patch.object(zhinst.utils, 'create_api_session', return_value=3 * (MagicMock(),)):
            adapter = InstrumentAdapterFactory.get_instrument_adapter('ZIUHFLIInstrumentAdapter', 'dev4242')

            adapter.instrument.demod1_oscillator(1)

            adapter.instrument.value_mapping = 1
            with self.assertLogs(level='ERROR') as log_grabber:
                config = adapter.read()

            self.assertTrue(all(['val_mapping' not in config[key] for key in config.keys()]))
            self.assertTrue('IDN' not in config.keys())
