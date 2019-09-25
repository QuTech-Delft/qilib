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
import math
from typing import Any, Optional

from qcodes.instrument_drivers.american_magnetics.AMI430 import AMI430

from qilib.configuration_helper.adapters.common_instrument_adapter import CommonInstrumentAdapter
from qilib.utils import PythonJsonStructure


class AMI430InstrumentAdapter(CommonInstrumentAdapter):
    """ Adapter for the AMI430 QCoDeS driver."""

    def __init__(self, address: str, instrument_name: Optional[str] = None) -> None:
        """ Instantiate a new AMI430 instrument adapter.

        Args:
            address: IP address and port number separated by a column, 'x.x.x.x:xxxx'
            instrument_name: An optional name for the underlying instrument.

        """
        super().__init__(address)
        ip_and_port = address.split(':')
        name = instrument_name if instrument_name is not None else self.name
        self._instrument = AMI430(name=name, address=ip_and_port[0], port=int(ip_and_port[1]))
        self.field_variation_tolerance = 0.01

    def apply(self, config: PythonJsonStructure) -> None:
        """ Does not apply config only  compares config to device settings.

        Args:
            config: Containing the instrument configuration.

        """
        parameter_argument= {'field': self.field_variation_tolerance}
        super().compare_config_on_apply(config, parameter_argument)

    def _filter_parameters(self, parameters: PythonJsonStructure) -> PythonJsonStructure:
        for values in parameters.values():
            if 'val_mapping' in values:
                values.pop('val_mapping')
        return parameters
