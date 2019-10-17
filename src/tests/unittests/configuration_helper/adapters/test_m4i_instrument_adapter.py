import logging
from unittest import TestCase
from unittest.mock import MagicMock, call, patch

from qilib.configuration_helper import InstrumentAdapterFactory
from qilib.configuration_helper.adapters import M4iInstrumentAdapter
from tests.test_data.m4i_snapshot import snapshot
from qcodes.instrument_drivers.Spectrum.M4i import M4i


class TestM4iInstrumentAdapter(TestCase):

    def setUp(self):
        self.address = 'spcm1234'
        self.adapter_name = 'M4iInstrumentAdapter'
        self.instrument_name = f'{self.adapter_name}_{self.address}'
        InstrumentAdapterFactory.instrument_adapters.clear()

    def test_constructor(self):
        with patch('qilib.configuration_helper.adapters.m4i_instrument_adapter.M4i') as m4i_mock:
            adapter = InstrumentAdapterFactory.get_instrument_adapter(self.adapter_name, self.address)
            m4i_mock.assert_called_with(self.instrument_name, cardid=self.address)
            self.assertEqual(adapter.instrument, m4i_mock())

    def test_apply_config(self):
        with patch('qilib.configuration_helper.adapters.m4i_instrument_adapter.M4i') as m4i_mock:
            adapter = InstrumentAdapterFactory.get_instrument_adapter(self.adapter_name, self.address)
            adapter.instrument.parameters = {key: MagicMock() for key in snapshot.keys()}
            adapter.apply(snapshot)

            self.assertEqual(adapter.name, self.instrument_name)
            self.assertEqual(adapter.instrument, m4i_mock())

            calls = [call(key, parameter['value']) for key, parameter in snapshot.items()
                     if parameter['value'] is not None]
            adapter.instrument.set.assert_has_calls(calls, any_order=True)

    def test_read_config(self):
        with patch('qilib.configuration_helper.adapters.m4i_instrument_adapter.M4i') as m4i_mock:
            adapter = InstrumentAdapterFactory.get_instrument_adapter(self.adapter_name, self.address)
            adapter.instrument.snapshot.return_value = {'parameters': snapshot}

            self.assertEqual(adapter.instrument, m4i_mock())
            self.assertEqual(adapter.name, self.instrument_name)

            config = adapter.read()
            self.assertDictEqual(snapshot, config)
