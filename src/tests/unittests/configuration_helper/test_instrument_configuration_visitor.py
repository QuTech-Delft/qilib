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
