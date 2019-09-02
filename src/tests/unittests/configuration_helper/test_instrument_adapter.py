import unittest
from unittest.mock import MagicMock

from qilib.configuration_helper import InstrumentAdapter
from qilib.utils import PythonJsonStructure


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

        adapter = TestAdapter('fake')
        adapter.close_instrument()
        instrument.close.assert_called_once_with()

    def test_instrument_representation(self):
        instrument = MagicMock()

        class TestAdapter(InstrumentAdapter):
            def __init__(self, address: str):
                super().__init__(address)

            def apply(self, config: PythonJsonStructure) -> None:
                pass

            def _filter_parameters(self, parameters: PythonJsonStructure) -> PythonJsonStructure:
                pass

        address = 'fake'
        adapter = TestAdapter(address)
        self.assertEqual(f'{adapter.__class__.__name__}_{address}', adapter.__str__())
