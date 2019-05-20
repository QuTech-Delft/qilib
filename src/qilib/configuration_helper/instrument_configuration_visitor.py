from typing import Union

from qilib.configuration_helper import InstrumentAdapter, InstrumentConfiguration
from qilib.configuration_helper.visitor import Visitor


class InstrumentConfigurationVisitor(Visitor):
    def __init__(self) -> None:
        self.instruments = []

    def visit(self, element: Union[InstrumentAdapter, InstrumentConfiguration]) -> None:
        if isinstance(element, InstrumentAdapter):
            self._visit_instrument_adapter(element)
        elif isinstance(element, InstrumentConfiguration):
            pass

    def _visit_instrument_adapter(self, instrument_adapter):
        self.instruments.append(instrument_adapter.instrument)
