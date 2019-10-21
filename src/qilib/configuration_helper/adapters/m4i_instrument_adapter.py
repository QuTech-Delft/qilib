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
from typing import Optional

from qilib.configuration_helper.adapters import CommonInstrumentAdapter
from qilib.utils import PythonJsonStructure


class M4iInstrumentAdapter(CommonInstrumentAdapter):
    """ Adapter for the Spectrum M4i digitizer."""

    def __init__(self, address: str, instrument_name: Optional[str] = None) -> None:
        super().__init__(address, instrument_name)
        from qcodes.instrument_drivers.Spectrum.M4i import M4i
        self._instrument = M4i(self._instrument_name, cardid=address)

    def _filter_parameters(self, parameters: PythonJsonStructure) -> PythonJsonStructure:
        if parameters['box_averages']['value'] == 1:
            parameters.pop('box_averages')

        parameters.pop('IDN')
        return parameters