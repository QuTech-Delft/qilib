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

try:
    from qtt.instrument_drivers.virtualAwg.settings import SettingsInstrument
except ImportError as e:
    raise ImportError(
        "Quantum Technology Toolbox, qtt, not installed. Please do 'pip install qtt' or install from source.") from e

from qilib.configuration_helper import InstrumentAdapter
from qilib.utils import PythonJsonStructure


class SettingsInstrumentAdapter(InstrumentAdapter):
    def __init__(self, address: str) -> None:
        super().__init__(address)
        self._instrument = SettingsInstrument(self._name)

    def apply(self, config: PythonJsonStructure) -> None:
        """ As there is no configuration to apply, this method is a NOP. """

    def read(self, update: bool = False) -> PythonJsonStructure:
        """ Override default read mechanism as this adapter has no real configuration.

        Returns:
            Empty python-json structure.
        """

        return super().read(update)

    def _filter_parameters(self, parameters: PythonJsonStructure) -> PythonJsonStructure:
        """ As there is no configuration to read, this method is a NOP. """
        return parameters
