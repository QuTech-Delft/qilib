import sys
import unittest

from qilib.configuration_helper import InstrumentAdapterFactory, InstrumentAdapter
from qilib.configuration_helper import adapters
from qilib.utils import PythonJsonStructure


class DummyInstrumentAdapter(InstrumentAdapter):
    def apply(self, config: PythonJsonStructure) -> None:
        pass

    def _filter_parameters(self, parameters: PythonJsonStructure) -> PythonJsonStructure:
        pass


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

    def test_external_adapters_add_not_called(self):
        from importlib import reload
        from qilib.configuration_helper import instrument_adapter_factory

        reload(instrument_adapter_factory)
        self.assertRaises(ValueError, InstrumentAdapterFactory.get_instrument_adapter, 'DummyInstrumentAdapter', '')

    def test_external_adapters_add_is_called___yolo(self):
        InstrumentAdapterFactory.add_instrument_adapters(sys.modules[__name__])

        adapter = InstrumentAdapterFactory.get_instrument_adapter('DummyInstrumentAdapter', '')
        self.assertIsInstance(adapter, DummyInstrumentAdapter)

        InstrumentAdapterFactory.instrument_adapters.pop(('DummyInstrumentAdapter', ''))
