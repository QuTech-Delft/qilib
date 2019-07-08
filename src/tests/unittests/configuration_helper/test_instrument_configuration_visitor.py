import unittest
from unittest.mock import patch, Mock

from qilib.configuration_helper import InstrumentConfiguration, InstrumentConfigurationSet
from qilib.configuration_helper.adapters import CommonInstrumentAdapter
from qilib.configuration_helper.instrument_configuration_visitor import InstrumentConfigurationVisitor
from qilib.utils import PythonJsonStructure


class DummyAdapter(CommonInstrumentAdapter):

    def __init__(self, address: str):
        super().__init__(address)
        self._instrument = Mock()

    def _filter_parameters(self, parameters: PythonJsonStructure) -> PythonJsonStructure:
        return parameters


class TestInstrumentConfigurationVisitor(unittest.TestCase):

    def test_visit(self):
        adapter = DummyAdapter('fake')
        with patch('qilib.configuration_helper.instrument_configuration.InstrumentAdapterFactory') as mock_factory:
            mock_factory.get_instrument_adapter.return_value = adapter
            instrument_1 = InstrumentConfiguration('DummyClass', 'fake-address-1', Mock(), tag=['instrument_1'])
        instrument_configuration_set = InstrumentConfigurationSet(Mock(), instruments=[instrument_1])
        visitor = InstrumentConfigurationVisitor()
        instrument_configuration_set.accept(visitor)
        self.assertIs(visitor.instruments[0], adapter.instrument)

    def test_get_instrument(self):
        instrument_class_name = 'DummyClass'
        instrument_address = 'fake-address-1'
        instrument_adapter_address = f'{instrument_class_name}_{instrument_address}'
        adapter = DummyAdapter('fake')
        adapter._instrument.name = instrument_adapter_address
        with patch('qilib.configuration_helper.instrument_configuration.InstrumentAdapterFactory') as mock_factory:
            mock_factory.get_instrument_adapter.return_value = adapter
            instrument_1 = InstrumentConfiguration(instrument_class_name, instrument_address, Mock(), tag=['instrument_1'])
        instrument_configuration_set = InstrumentConfigurationSet(Mock(), instruments=[instrument_1])
        visitor = InstrumentConfigurationVisitor()
        instrument_configuration_set.accept(visitor)

        self.assertEqual(visitor.get_instrument(instrument_adapter_address), adapter.instrument)

        wrong_address = 'DummyClass_fake_address-2'
        self.assertRaisesRegex(ValueError, 'No adapter with identifier', visitor.get_instrument, wrong_address)
