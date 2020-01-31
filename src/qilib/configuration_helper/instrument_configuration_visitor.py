"""Quantum Inspire library

Copyright 2019 QuTech Delft

qilib is available under the [MIT open-source license](https://opensource.org/licenses/MIT):

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
from typing import Union, List

from qcodes.instrument.base import Instrument

from qilib.configuration_helper.instrument_adapter import InstrumentAdapter
from qilib.configuration_helper.instrument_configuration import InstrumentConfiguration
from qilib.configuration_helper.visitor import Visitor


class InstrumentConfigurationVisitor(Visitor):
    """ Implementation of Visitor interface to visit InstrumentConfiguration."""
    def __init__(self) -> None:
        """ Instantiate a new visitor."""
        self.instruments: List[Instrument] = []

    def visit(self, element: Union[InstrumentAdapter, InstrumentConfiguration]) -> None:
        """ Visit InstrumentConfiguration and/or InstrumentAdapter.

        Args:
            element: An instance of InstrumentAdapter or InstrumentConfiguration that has been visited.

        """
        if isinstance(element, InstrumentAdapter):
            self._visit_instrument_adapter(element)
        elif isinstance(element, InstrumentConfiguration):
            pass

    def _visit_instrument_adapter(self, instrument_adapter: InstrumentAdapter) -> None:
        if instrument_adapter.instrument is not None:
            self.instruments.append(instrument_adapter.instrument)

    def get_instrument(self, adapter_identifier: str) -> Instrument:
        """ Returns a specific instrument given the adapter name, address combination.

        Args:
            adapter_identifier: The adapter name and address
                                combination (e.g. ZIHDAWG8InstrumentAdapter_DEV8049).

        Raises:
            ValueError: If an adapter identifier is given which is not in the loaded adapters.

        Returns:
            The qcodes instrument which belongs to the adapter identifier.
        """
        instrument = next((i for i in self.instruments if i.name == adapter_identifier), None)
        if instrument is None:
            raise ValueError(f'No adapter with identifier {adapter_identifier} found!')
        return instrument
