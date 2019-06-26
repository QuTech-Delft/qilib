import unittest
from importlib import reload
from types import ModuleType
from unittest.mock import MagicMock

from qilib.utils import PythonJsonStructure

from qilib.configuration_helper import adapters
from qilib.configuration_helper import InstrumentAdapterFactory, InstrumentAdapter


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

    def test_import_error_as_value_error(self):
        import builtins
        import sys
        import importlib
        importlib.invalidate_caches()

        current_modules = sys.modules.copy()
        original_import = builtins.__import__

        def fake_import(name, *args, **kwargs):
            if name.startswith('qtt'):
                raise ImportError()
            else:
                return original_import(name, *args, **kwargs)

        builtins.__import__ = fake_import

        modules = {'TimeStampInstrumentAdapter': 'qilib.configuration_helper.adapters.time_stamp_instrument_adapter',
                   'SettingsInstrumentAdapter': 'qilib.configuration_helper.adapters.settings_instrument_adapter'}
        for path in modules.values():
            del sys.modules[path]

        reload(adapters)

        for adapter in modules.keys():
            error_msg = f'Failed to load {adapter}'
            get_adapter = InstrumentAdapterFactory.get_instrument_adapter
            self.assertRaisesRegex(ValueError, error_msg, get_adapter, adapter, 'address')

        builtins.__import__ = original_import
        sys.modules = current_modules.copy()
