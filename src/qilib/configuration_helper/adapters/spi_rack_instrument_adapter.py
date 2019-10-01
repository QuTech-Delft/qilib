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
from spirack import SPI_rack

from qilib.configuration_helper import InstrumentAdapter
from qilib.utils import PythonJsonStructure


class SpiRackInstrumentAdapter(InstrumentAdapter):

    def __init__(self, address: str) -> None:
        super().__init__(address)
        self._instrument: SPI_rack = SPI_rack(address, baud='115200', timeout=1)

    def apply(self, config: PythonJsonStructure) -> None:
        self._instrument.apply_settings(config['serialport'])

    def read(self, update: bool = True) -> PythonJsonStructure:
        parameters = {
            'version': self._instrument.get_firmware_version(),
            'temperature': self._instrument.get_temperature(),
            'battery': self._instrument.get_battery(),
            'serialport': self._instrument.get_settings()
        }
        return PythonJsonStructure(parameters)

    def _filter_parameters(self, parameters: PythonJsonStructure) -> PythonJsonStructure:
        return parameters
