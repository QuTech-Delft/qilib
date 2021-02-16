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
from typing import Optional, Type

from qcodes_contrib_drivers.drivers.QuTech.M2j import M2j

from qilib.configuration_helper.adapters.spi_rack_instrument_adapter import SpiRackInstrumentAdapter
from qilib.configuration_helper.adapters.spi_module_instrument_adapter import SpiModuleInstrumentAdapter


class M2jInstrumentAdapter(SpiModuleInstrumentAdapter):

    def __init__(self, address: str, instrument_name: Optional[str] = None,
                 instrument_class: Optional[Type[M2j]] = None,
                 spi_rack_instrument_adapter_class: Optional[Type[SpiRackInstrumentAdapter]] = None) -> None:
        super().__init__(address, instrument_name, spi_rack_instrument_adapter_class)
        if instrument_class is None:
            instrument_class = M2j
        self._instrument: M2j = instrument_class(self._instrument_name, self._spi_rack, self._module_number)
