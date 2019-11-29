import copy
import sys
from unittest import TestCase
from unittest.mock import MagicMock, call, patch

from qilib.configuration_helper import InstrumentAdapterFactory
from tests.test_data.m4i_snapshot import snapshot

sys.modules['pyspcm'] = MagicMock()
from qcodes_contrib_drivers.drivers.Spectrum.M4i import M4i
del sys.modules['pyspcm']


class TestM4iInstrumentAdapter(TestCase):

    def setUp(self):
        self.address = 'spcm1234'
        self.snapshot = copy.deepcopy(snapshot)
        self.adapter_name = 'M4iInstrumentAdapter'
        self.instrument_name = f'{self.adapter_name}_{self.address}'
        InstrumentAdapterFactory.adapter_instances.clear()

    def test_constructor(self):
        with patch('qcodes_contrib_drivers.drivers.Spectrum.M4i.M4i') as m4i_mock:
            adapter = InstrumentAdapterFactory.get_instrument_adapter(self.adapter_name, self.address)
            m4i_mock.assert_called_with(self.instrument_name, cardid=self.address)
            m4i_mock.return_value.initialize_channels.assert_called_once()
            self.assertEqual(adapter.instrument, m4i_mock())

    def test_apply_config_parameters_called(self):
        with patch('qcodes_contrib_drivers.drivers.Spectrum.M4i.M4i') as m4i_mock:
            adapter = InstrumentAdapterFactory.get_instrument_adapter(self.adapter_name, self.address)
            adapter.instrument.parameters = {key: MagicMock() for key in self.snapshot.keys()}
            adapter.apply(self.snapshot)

            self.assertEqual(adapter.name, self.instrument_name)
            self.assertEqual(adapter.instrument, m4i_mock())

            calls = [call(key, parameter['value']) for key, parameter in snapshot.items()
                     if parameter['value'] is not None]
            adapter.instrument.set.assert_has_calls(calls, any_order=True)

    def test_apply_config_none_value_raises(self):
        with patch('qcodes_contrib_drivers.drivers.Spectrum.M4i.M4i') as m4i_mock:
            adapter = InstrumentAdapterFactory.get_instrument_adapter(self.adapter_name, self.address)
            adapter.instrument.parameters = {key: MagicMock() for key in self.snapshot.keys()}

            parameter_name = 'channel_1'
            self.snapshot[parameter_name]['value'] = None

            error_message = f'The following parameter\(s\) of .* \[\'{parameter_name}\'\]\!'
            self.assertRaisesRegex(ValueError, error_message, adapter.apply, self.snapshot)

    def test_read_config(self):
        with patch('qcodes_contrib_drivers.drivers.Spectrum.M4i.M4i') as m4i_mock:
            adapter = InstrumentAdapterFactory.get_instrument_adapter(self.adapter_name, self.address)
            adapter.instrument.snapshot.return_value = {'parameters': copy.deepcopy(self.snapshot)}

            self.assertEqual(adapter.instrument, m4i_mock())
            self.assertEqual(adapter.name, self.instrument_name)
            config = adapter.read()

            expected_config = self.snapshot.copy()
            expected_config.pop('IDN')
            expected_config.pop('box_averages')
            expected_config.pop('card_available_length')
            self.assertDictEqual(expected_config, config)
