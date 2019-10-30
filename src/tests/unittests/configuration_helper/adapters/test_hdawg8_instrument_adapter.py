import json
import os
import unittest
from unittest.mock import patch, MagicMock, call

import zhinst

import qilib
from qilib.configuration_helper import InstrumentAdapterFactory


class TestZIHDAWG8InstrumentAdapter(unittest.TestCase):
    def setUp(self):
        self._node_tree_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'test_data', 'node_tree.json')

        self.node_tree = {"/DEV8049/SYSTEM/AWG/CHANNELGROUPING": {
            "Node": "/DEV8049/SYSTEM/AWG/CHANNELGROUPING",
            "Description": "Sets the channel grouping mode of the device.",
            "Properties": "Read, Write, Setting",
            "Type": "Integer (enumerated)",
            "Unit": "None",
            "Options": {
                "0": "Use the outputs in groups of 2. One sequencer program controls 2 outputs ",
                "1": "Use the outputs in groups of 4. One sequencer program controls 4 outputs ",
                "2": "Use the outputs in groups of 8. One sequencer program controls 8 outputs "
            }
        }, "/DEV8049/SIGOUTS/0/ON": {
            "Node": "/DEV8049/SIGOUTS/0/ON",
            "Description": "Enabling/Disabling the Signal Output. Corresponds to the blue LED indicator",
            "Properties": "Read, Write, Setting",
            "Type": "Integer (64 bit)",
            "Unit": "None"
        }, "/DEV8049/SYSTEM/OWNER": {
            "Node": "/DEV8049/SYSTEM/OWNER",
            "Description": "Returns the current owner of the device (IP).",
            "Properties": "Read",
            "Type": "String",
            "Unit": "None"
        }, "/DEV8049/SINES/0/AMPLITUDES/0": {
            "Node": "/DEV8049/SINES/0/AMPLITUDES/0",
            "Description": "Sets the peak amplitude that the sine signal contributes to the signal output. Note that "
                           "the last index is either 0 or 1 and will map to the pair of outputs given by the first "
                           "index. (e.g. sines/3/amplitudes/0 corresponds to wave output 2)",
            "Properties": "Read, Write, Setting",
            "Type": "Double",
            "Unit": "None"
        }, "/DEV8049/AWGS/1/WAVEFORM/MEMORYUSAGE": {
            "Node": "/DEV8049/AWGS/1/WAVEFORM/MEMORYUSAGE",
            "Description": "Amount of the used waveform data relative to the device cache memory. The cache memory "
                           "provides space for 32 kSa of waveform data. Memory Usage over 100% means that waveforms "
                           "must be loaded from the main memory (128 MSa per channel) during playback, which can lead "
                           "to delays.",
            "Properties": "Read",
            "Type": "Double",
            "Unit": "%"
        }, "/DEV8049/AWGS/1/WAVEFORM/DATA": {
            "Node": "/DEV8049/AWGS/1/WAVEFORM/DATA",
            "Description": "Allows to write (using vectorWrite) or read (using getAsEvent) the selected waveform data "
                           "at the selected index.",
            "Properties": "Read, Write",
            "Type": "ZIVectorData",
            "Unit": "None"
        }, "/DEV8049/AWGS/1/WAVEFORM/INDEX": {
            "Node": "/DEV8049/AWGS/1/WAVEFORM/INDEX",
            "Description": "Allows to select the index of the waveform in the waveform list for subsequent writing and+"
                           " reading.",
            "Properties": "Read, Write",
            "Type": "Integer (64 bit)",
            "Unit": "None"
        }}

    def test_apply(self):
        with patch.object(zhinst.utils, 'create_api_session', return_value=3 * (MagicMock(),)) as daq, \
                patch.object(qilib.configuration_helper.adapters.hdawg8_instrument_adapter.ZIHDAWG8,
                             'download_device_node_tree', return_value=self.node_tree) as ddnt, \
                patch('qilib.configuration_helper.adapters.common_instrument_adapter.logging') as logger_mock:
            address = 'test_dev1'
            adapter_name = 'ZIHDAWG8InstrumentAdapter'
            instrument_name = "{0}_{1}".format(adapter_name, address)
            hdawg_adapter = InstrumentAdapterFactory.get_instrument_adapter(adapter_name, address)
            daq.assert_called()
            ddnt.assert_called()
            daq.return_value[1].getInt.return_value = 1
            daq.return_value[1].getDouble.return_value = 0.5
            daq.return_value[1].getString.return_value = "Test String"
            daq.return_value[1].getAsEvent.return_value = [0.1, 0.2, 0.3, 0.4]

            hdawg_adapter.instrument.set_channel_grouping(1)
            hdawg_adapter.instrument.enable_channel(0)
            hdawg_adapter.instrument.upload_waveform(1, [0.1, 0.2, 0.3, 0.4], 1)
            hdawg_adapter.instrument.set('sines_0_amplitudes_0', 0.5)

            self.assertEqual(instrument_name, hdawg_adapter.instrument.name)
            self.assertEqual(1, hdawg_adapter.instrument.system_awg_channelgrouping.raw_value)
            self.assertEqual(1, hdawg_adapter.instrument.sigouts_0_on.raw_value)
            self.assertEqual(1, hdawg_adapter.instrument.awgs_1_waveform_index.raw_value)
            self.assertListEqual([0.1, 0.2, 0.3, 0.4], hdawg_adapter.instrument.awgs_1_waveform_data.raw_value)
            self.assertEqual(0.5, hdawg_adapter.instrument.sines_0_amplitudes_0.raw_value)

            config = hdawg_adapter.read()

            hdawg_adapter.instrument.set_channel_grouping(0)
            hdawg_adapter.instrument.disable_channel(0)
            hdawg_adapter.instrument.upload_waveform(1, [0.3, 0.4, 0.5, 0.6], 0)
            hdawg_adapter.instrument.set('sines_0_amplitudes_0', 0.2)

            self.assertEqual(0, hdawg_adapter.instrument.system_awg_channelgrouping.raw_value)
            self.assertEqual(0, hdawg_adapter.instrument.sigouts_0_on.raw_value)
            self.assertEqual(0, hdawg_adapter.instrument.awgs_1_waveform_index.raw_value)
            self.assertListEqual([0.3, 0.4, 0.5, 0.6], hdawg_adapter.instrument.awgs_1_waveform_data.raw_value)
            self.assertEqual(0.2, hdawg_adapter.instrument.sines_0_amplitudes_0.raw_value)

            hdawg_adapter.apply(config)
            logger_mock.warning.assert_not_called()

            self.assertEqual(1, hdawg_adapter.instrument.system_awg_channelgrouping.raw_value)
            self.assertEqual(1, hdawg_adapter.instrument.sigouts_0_on.raw_value)
            self.assertEqual(1, hdawg_adapter.instrument.awgs_1_waveform_index.raw_value)
            self.assertListEqual([0.1, 0.2, 0.3, 0.4], hdawg_adapter.instrument.awgs_1_waveform_data.raw_value)
            self.assertEqual(0.5, hdawg_adapter.instrument.sines_0_amplitudes_0.raw_value)

            parameter_name = 'sigouts_0_on'
            config = hdawg_adapter.read()
            config[parameter_name]['value'] = None
            error_message = f'The following parameter\(s\) of .*'
            self.assertRaisesRegex(ValueError, error_message, hdawg_adapter.apply, config)

            hdawg_adapter.instrument.close()

    def test_full_node_tree(self):
        with patch.object(zhinst.utils, 'create_api_session', return_value=3 * (MagicMock(),)) as daq, \
                patch('qilib.configuration_helper.adapters.common_instrument_adapter.logging'), \
                open(self._node_tree_path) as node_tree, \
                patch.object(qilib.configuration_helper.adapters.hdawg8_instrument_adapter.ZIHDAWG8,
                             'download_device_node_tree', return_value=json.load(node_tree)) as ddnt:
            hdawg_adapter = InstrumentAdapterFactory.get_instrument_adapter('ZIHDAWG8InstrumentAdapter', 'test-dev2')
            ddnt.assert_called()
            daq.assert_called()

            daq.return_value[1].getInt.return_value = 1
            daq.return_value[1].getDouble.return_value = 0.5
            daq.return_value[1].getString.return_value = "Test String"
            daq.return_value[1].getAsEvent.return_value = [0.1, 0.2, 0.3, 0.4]
            expected_regex = f"Parameter values of {hdawg_adapter.name} are .*"
            with self.assertLogs(level='ERROR') as log_grabber:
                config_original = hdawg_adapter.read()

            self.assertRegex(log_grabber.records[0].message, expected_regex)

            daq.return_value[1].getInt.return_value = 0
            daq.return_value[1].getDouble.return_value = 0.7
            daq.return_value[1].getString.return_value = "New String"
            daq.return_value[1].getAsEvent.return_value = [0.5, 0.6, 0.7, 0.8]
            with self.assertLogs(level='ERROR') as log_grabber:
                config_new = hdawg_adapter.read()

            self.assertRegex(log_grabber.records[0].message, expected_regex)

            # Apply original config and assert parameters have been updated
            hdawg_adapter.apply(config_original)
            for parameter in config_original:
                if parameter in hdawg_adapter.instrument.parameters and hasattr(
                        hdawg_adapter.instrument.parameters[parameter], 'set'):
                    self.assertIn(hdawg_adapter.instrument.parameters[parameter].raw_value,
                                  [1, 0.5, "Test String", [0.1, 0.2, 0.3, 0.4]])

            # Apply new config and assert parameters are updated
            hdawg_adapter.apply(config_new)
            for parameter in config_new:
                if parameter in hdawg_adapter.instrument.parameters and hasattr(
                        hdawg_adapter.instrument.parameters[parameter], 'set'):
                    self.assertIn(hdawg_adapter.instrument.parameters[parameter].raw_value,
                                  [0, 0.7, "New String", [0.5, 0.6, 0.7, 0.8]])
                    self.assertNotIn(hdawg_adapter.instrument.parameters[
                                         parameter].raw_value,
                                     [1, 0.5, "Test String", [0.1, 0.2, 0.3, 0.4]])

            # Apply original config again and check if updated
            hdawg_adapter.apply(config_original)
            for parameter in config_original:
                if parameter in hdawg_adapter.instrument.parameters and hasattr(
                        hdawg_adapter.instrument.parameters[parameter], 'set'):
                    self.assertIn(hdawg_adapter.instrument.parameters[parameter].raw_value,
                                  [1, 0.5, "Test String", [0.1, 0.2, 0.3, 0.4]])
                    self.assertNotIn(hdawg_adapter.instrument.parameters[parameter].raw_value,
                                     [0, 0.7, "New String", [0.5, 0.6, 0.7, 0.8]])

            hdawg_adapter.instrument.close()

    def test_start(self):
        with patch('qilib.configuration_helper.adapters.hdawg8_instrument_adapter.ZIHDAWG8') as dawg:
            adapter_name = 'ZIHDAWG8InstrumentAdapter'
            hdawg_adapter = InstrumentAdapterFactory.get_instrument_adapter(adapter_name, 'dev42')
            hdawg_adapter.start(1)
            dawg.assert_has_calls([call().start_awg(1)])
            hdawg_adapter.instrument.close()

    def test_stop(self):
        with patch('qilib.configuration_helper.adapters.hdawg8_instrument_adapter.ZIHDAWG8') as dawg:
            adapter_name = 'ZIHDAWG8InstrumentAdapter'
            hdawg_adapter = InstrumentAdapterFactory.get_instrument_adapter(adapter_name, 'dev41')
            hdawg_adapter.stop(1)
            dawg.assert_has_calls([call().stop_awg(1)])
            hdawg_adapter.instrument.close()

    def test_close_instrument(self):
        dawg_instance = MagicMock()
        with patch('qilib.configuration_helper.adapters.hdawg8_instrument_adapter.ZIHDAWG8',
                   return_value=dawg_instance):
            adapter_name = 'ZIHDAWG8InstrumentAdapter'
            hdawg_adapter = InstrumentAdapterFactory.get_instrument_adapter(adapter_name, 'dev43')
        hdawg_adapter.close_instrument()
        dawg_instance.close.assert_called_once_with()

    def test_upload(self):
        with patch('qilib.configuration_helper.adapters.hdawg8_instrument_adapter.ZIHDAWG8') as dawg:
            adapter_name = 'ZIHDAWG8InstrumentAdapter'
            hdawg_adapter = InstrumentAdapterFactory.get_instrument_adapter(adapter_name, 'dev40')
            hdawg_adapter.upload('program', 1)
            dawg.assert_has_calls([call().upload_sequence_program(1, 'program')])
            hdawg_adapter.instrument.close()

    def test_read_should_filter_nics(self):
        with patch.object(zhinst.utils, 'create_api_session', return_value=3 * (MagicMock(),)) as daq, \
                open(self._node_tree_path) as node_tree, \
                patch.object(qilib.configuration_helper.adapters.hdawg8_instrument_adapter.ZIHDAWG8,
                             'download_device_node_tree', return_value=json.load(node_tree)) as ddnt:
            hdawg_adapter = InstrumentAdapterFactory.get_instrument_adapter('ZIHDAWG8InstrumentAdapter', 'test-dev3')
            ddnt.assert_called()
            daq.assert_called()
            daq.return_value[1].getInt.return_value = 1
            daq.return_value[1].getDouble.return_value = 0.5
            daq.return_value[1].getString.return_value = "Test String"
            daq.return_value[1].getAsEvent.return_value = [0.1, 0.2, 0.3, 0.4]

            expected_regex = f"Parameter values of {hdawg_adapter.name} are .*"
            with self.assertLogs(level='ERROR') as log_grabber:
                config = hdawg_adapter.read()

        self.assertRegex(log_grabber.records[0].message, expected_regex)
        self.assertNotIn('system_nics_0_defaultip4', config)
        self.assertNotIn('system_nics_0_defaultmask', config)
        self.assertNotIn('system_nics_0_defaultgateway', config)
        self.assertNotIn('system_nics_0_static', config)
        self.assertNotIn('system_nics_0_mac', config)
        self.assertNotIn('system_nics_0_ip4', config)
        self.assertNotIn('system_nics_0_mask', config)
        self.assertNotIn('system_nics_0_gateway', config)
        hdawg_adapter.instrument.close()
