import unittest
from unittest.mock import MagicMock
from typing import Any

from qilib.configuration_helper import InstrumentAdapter
from qilib.utils import PythonJsonStructure
from tests.test_data.dummy_instrument_adapter import DummyInstrumentAdapter


class TestInstrumentAdapter(unittest.TestCase):

    def test_instantiate_abstract_class_should_fail(self):
        with self.assertRaises(TypeError):
            InstrumentAdapter('-test')

    def test_close_instrument(self):
        instrument = MagicMock()

        class TestAdapter(InstrumentAdapter):
            def __init__(self, address: str):
                super().__init__(address)
                self._instrument = instrument

            def apply(self, config: PythonJsonStructure) -> None:
                pass

            def _filter_parameters(self, parameters: PythonJsonStructure) -> PythonJsonStructure:
                pass

            def _compare_config_values(self, config_value: Any, device_value: Any, parameter: str) -> bool:
                pass

        adapter = TestAdapter('fake')
        adapter.close_instrument()
        instrument.close.assert_called_once_with()

    def test_instrument_string_representation(self):
        adapter = DummyInstrumentAdapter('some_address', 'some_dummy')
        adapter_str = str(adapter)
        self.assertEqual('InstrumentAdapter: DummyInstrumentAdapter_some_address', adapter_str)
        adapter.close_instrument()

