import unittest
from unittest.mock import patch, Mock
from typing import Any

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

    def _compare_config_values(self, config_value: Any, device_value: Any, parameter: str) -> bool:
        pass


class TestInstrumentConfigurationVisitor(unittest.TestCase):

    def __create_visitor_with_instrument(self, adapter, instrument_class_name, instrument_address):
        with patch('qilib.configuration_helper.instrument_configuration.InstrumentAdapterFactory') as mock_factory:
            mock_factory.get_instrument_adapter.return_value = adapter
            instrument_1 = InstrumentConfiguration(instrument_class_name, instrument_address, Mock(), tag=['instrument_1'])
        instrument_configuration_set = InstrumentConfigurationSet(Mock(), instruments=[instrument_1])
        visitor = InstrumentConfigurationVisitor()
        instrument_configuration_set.accept(visitor)
        return visitor

    def test_visit(self):
        adapter = DummyAdapter('fake0')
        instrument_class_name = 'DummyClass0'
        instrument_address = 'fake-address-0'

        visitor = self.__create_visitor_with_instrument(adapter, instrument_class_name, instrument_address)
        self.assertIs(visitor.instruments[0], adapter.instrument)

    def test_get_instrument(self):
        adapter = DummyAdapter('fake1')
        instrument_class_name = 'DummyClass1'
        instrument_address = 'fake-address-1'
        instrument_adapter_address = f'{instrument_class_name}_{instrument_address}'
        adapter._instrument.name = instrument_adapter_address

        visitor = self.__create_visitor_with_instrument(adapter, instrument_class_name, instrument_address)
        self.assertEqual(visitor.get_instrument(instrument_adapter_address), adapter.instrument)

    def test_get_instrument_invalid_name_raises_error(self):
        adapter = DummyAdapter('fake2')
        instrument_class_name = 'DummyClass2'
        instrument_address = 'fake-address-2'
        adapter._instrument.name = f'{instrument_class_name}_{instrument_address}'
        visitor = self.__create_visitor_with_instrument(adapter, instrument_class_name, instrument_address)

        wrong_address = 'DummyClass_fake_address-2'
        self.assertRaisesRegex(ValueError, 'No adapter with identifier', visitor.get_instrument, wrong_address)
