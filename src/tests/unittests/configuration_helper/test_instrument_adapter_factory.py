import unittest

from qilib.configuration_helper import InstrumentAdapterFactory, InstrumentAdapter
from qilib.configuration_helper import adapters
from qilib.utils import PythonJsonStructure


class TestInstrumentAdapterFactory(unittest.TestCase):
    class DummyAdapter(InstrumentAdapter):
        def _filter_parameters(self, parameters: PythonJsonStructure) -> PythonJsonStructure:
            pass

        def apply(self, config: PythonJsonStructure) -> None:
            pass

    def setUp(self):
        adapters.InstrumentAdapter = TestInstrumentAdapterFactory.DummyAdapter

    def test_factory_creates_single_instance(self):
        dummy_adapter1 = InstrumentAdapterFactory.get_instrument_adapter('InstrumentAdapter', 'dev1')
        dummy_adapter2 = InstrumentAdapterFactory.get_instrument_adapter('InstrumentAdapter', 'dev1')
        self.assertIs(dummy_adapter1, dummy_adapter2)

    def test_factory_new_instance(self):
        dummy_adapter1 = InstrumentAdapterFactory.get_instrument_adapter('InstrumentAdapter', 'dev1')
        dummy_adapter2 = InstrumentAdapterFactory.get_instrument_adapter('InstrumentAdapter', 'dev2')
        self.assertIsNot(dummy_adapter1, dummy_adapter2)
        dummy_adapter3 = InstrumentAdapterFactory.get_instrument_adapter('InstrumentAdapter', 'dev1')
        self.assertIs(dummy_adapter1, dummy_adapter3)

    def test_raise_value_error(self):
        with self.assertRaises(ValueError):
            InstrumentAdapterFactory.get_instrument_adapter('SomeAdapter', 'dev42')
