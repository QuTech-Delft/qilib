import logging
from unittest import TestCase
from unittest.mock import MagicMock, call, patch

from qilib.configuration_helper import InstrumentAdapterFactory
from qilib.configuration_helper.adapters import M4iInstrumentAdapter
from tests.test_data.m4i_snapshot import snapshot


class TestM4iInstrumentAdapter(TestCase):

    def setUp(self):
        self.address = 'spcm1234'
        self.adapter_name = 'M4iInstrumentAdapter'
        self.instrument_name = f'{self.adapter_name}_{self.address}'
        InstrumentAdapterFactory.instrument_adapters.clear()

    def test_constructor(self):
        with patch('qilib.configuration_helper.adapters.m4i_instrument_adapter.qcodes') as qcodes_mock:
            m4i_mock = qcodes_mock.instrument_drivers.Spectrum.M4i.M4i
            adapter = InstrumentAdapterFactory.get_instrument_adapter(self.adapter_name, self.address)
            m4i_mock.assert_called_with(self.instrument_name, cardid=self.address)
            self.assertEqual(adapter.instrument, m4i_mock())

    def test_apply_config(self):
        with patch('qilib.configuration_helper.adapters.m4i_instrument_adapter.qcodes') as qcodes_mock, \
          patch('qilib.configuration_helper.adapters.common_instrument_adapter.logging') as logging_mock:
            m4i_mock = qcodes_mock.instrument_drivers.Spectrum.M4i.M4i
            adapter = InstrumentAdapterFactory.get_instrument_adapter(self.adapter_name, self.address)
            adapter.instrument.parameters = {key: MagicMock() for key in snapshot.keys()}
            adapter.apply(snapshot)

            self.assertEqual(adapter.name, self.instrument_name)
            self.assertEqual(adapter.instrument, m4i_mock())

            calls = [call(key, parameter['value']) for key, parameter in snapshot.items()
                     if parameter['value'] is not None]
            adapter.instrument.set.assert_has_calls(calls, any_order=True)

            logging_call = logging_mock.method_calls[0][1][0]
            self.assertRegex(logging_call, "Some parameter values of *")

    def test_read_config(self):
        with patch('qilib.configuration_helper.adapters.m4i_instrument_adapter.qcodes') as qcodes_mock:
            m4i_mock = qcodes_mock.instrument_drivers.Spectrum.M4i.M4i

            adapter = InstrumentAdapterFactory.get_instrument_adapter(self.adapter_name, self.address)
            adapter.instrument.snapshot.return_value = {'parameters': snapshot.copy()}

            self.assertEqual(adapter.instrument, m4i_mock())
            self.assertEqual(adapter.name, self.instrument_name)
            config = adapter.read()

            expected_config = snapshot.copy()
            expected_config.pop('IDN')
            expected_config.pop('box_averages')
            self.assertDictEqual(expected_config, config)
