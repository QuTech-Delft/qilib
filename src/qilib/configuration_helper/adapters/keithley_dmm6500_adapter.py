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

import requests
from qcodes.instrument_drivers.tektronix.Keithley_6500 import Keithley_6500

from qilib.configuration_helper.adapters.common_instrument_adapter import CommonInstrumentAdapter
from qilib.utils.python_json_structure import PythonJsonStructure


class Keithley6500InstrumentAdapter(CommonInstrumentAdapter):
    def __init__(self, address: str, instrument_name: Optional[str] = None,
                 instrument_class: Optional[Type[Keithley_6500]] = None) -> None:
        super().__init__(address, instrument_name)
        if address[0:5] == 'TCPIP':
            # Perform a http request to the instrument's IP address before opening the device to make sure any
            # stuck state is unstuck.
            self._send_request_to_instrument(address)
        if instrument_class is None:
            instrument_class = Keithley_6500
        self._instrument: Keithley_6500 = instrument_class(self._instrument_name, address)

    def _filter_parameters(self, parameters: PythonJsonStructure) -> PythonJsonStructure:
        return parameters

    @staticmethod
    def _send_request_to_instrument(address: str) -> None:
        ip_address = address.split('::')[1]
        requests.get("http://{}/".format(ip_address))
