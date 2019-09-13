import sys
import unittest

import tests
from qilib.configuration_helper import InstrumentAdapterFactory
from tests.test_data.dummy_instrument_adapter import DummyInstrumentAdapter


class TestInstrumentAdapterFactory(unittest.TestCase):

    def setUp(self):
        InstrumentAdapterFactory.add_instrument_adapters(tests.test_data.dummy_instrument_adapter)

    def test_factory_creates_single_instance(self):
        dummy_adapter1 = InstrumentAdapterFactory.get_instrument_adapter('DummyInstrumentAdapter', 'dev1')
        dummy_adapter2 = InstrumentAdapterFactory.get_instrument_adapter('DummyInstrumentAdapter', 'dev1')
        self.assertIs(dummy_adapter1, dummy_adapter2)
        dummy_adapter1.close_instrument()

    def test_factory_new_instance(self):
        dummy_adapter1 = InstrumentAdapterFactory.get_instrument_adapter('DummyInstrumentAdapter', 'dev1')
        dummy_adapter2 = InstrumentAdapterFactory.get_instrument_adapter('DummyInstrumentAdapter', 'dev2')
        self.assertIsNot(dummy_adapter1, dummy_adapter2)
        dummy_adapter3 = InstrumentAdapterFactory.get_instrument_adapter('DummyInstrumentAdapter', 'dev1')
        self.assertIs(dummy_adapter1, dummy_adapter3)

        dummy_adapter1.close_instrument()
        dummy_adapter2.close_instrument()

    def test_raise_value_error(self):
        with self.assertRaises(ValueError):
            InstrumentAdapterFactory.get_instrument_adapter('SomeAdapter', 'dev42')

    def test_external_adapters_add_not_called(self):
        from importlib import reload
        from qilib.configuration_helper import instrument_adapter_factory

        reload(instrument_adapter_factory)
        self.assertRaises(ValueError, InstrumentAdapterFactory.get_instrument_adapter, 'DummyInstrumentAdapter', '')

    def test_external_adapters_add_is_called(self):
        InstrumentAdapterFactory.add_instrument_adapters(sys.modules[__name__])

        dummy_adapter = InstrumentAdapterFactory.get_instrument_adapter('DummyInstrumentAdapter', '')
        self.assertIsInstance(dummy_adapter, DummyInstrumentAdapter)

        InstrumentAdapterFactory.instrument_adapters.pop(('DummyInstrumentAdapter', ''))
        dummy_adapter.close_instrument()

    def test_different_instrument_name_raises_error(self):
        dummy_adapter = InstrumentAdapterFactory.get_instrument_adapter('DummyInstrumentAdapter', 'dev12', 'some_name')
        self.assertEqual('some_name', dummy_adapter.instrument.name)
        error_msg = 'An adapter exist with different instrument name \'some_name\' != \'other_name\''
        self.assertRaisesRegex(ValueError, error_msg, InstrumentAdapterFactory.get_instrument_adapter,
                               'DummyInstrumentAdapter', 'dev12', 'other_name')
        dummy_adapter.close_instrument()
