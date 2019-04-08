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
from qcodes.instrument_drivers.ZI.ZIHDAWG8 import ZIHDAWG8

from qilib.configuration_helper.adapters import CommonInstrumentAdapter
from qilib.utils import PythonJsonStructure


class ZIHDAWG8InstrumentAdapter(CommonInstrumentAdapter):
    def __init__(self, address: str) -> None:
        super().__init__(address)
        self._instrument: ZIHDAWG8 = ZIHDAWG8(self.name, address)

    def read(self, update: bool = True) -> PythonJsonStructure:
        return PythonJsonStructure(super().read(update))

    def _filter_parameters(self, parameters: PythonJsonStructure) -> PythonJsonStructure:
        filtered = {parameter: value for (parameter, value) in parameters.items() if 'system_nics_' not in parameter}
        return PythonJsonStructure(filtered)

    def start(self, awg_number: int) -> None:
        self._instrument.start_awg(awg_number)

    def stop(self, awg_number: int) -> None:
        self._instrument.stop_awg(awg_number)

    def upload(self, sequence_program: str, awg_number: int) -> None:
        self._instrument.upload_sequence_program(awg_number, sequence_program)
