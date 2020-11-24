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
from typing import Any, Optional, Type

from qcodes.instrument_drivers.american_magnetics.AMI430 import AMI430

from qilib.configuration_helper.adapters.read_only_configuration_instrument_adapter import \
    ReadOnlyConfigurationInstrumentAdapter
from qilib.utils.python_json_structure import PythonJsonStructure


class AMI430InstrumentAdapter(ReadOnlyConfigurationInstrumentAdapter):
    """ Adapter for the AMI430 QCoDeS driver."""

    def __init__(self, address: str, instrument_name: Optional[str] = None,
                 instrument_class: Optional[Type[AMI430]] = None) -> None:
        """ Instantiate a new AMI430 instrument adapter.

        Args:
            address: IP address and port number separated by a column, 'x.x.x.x:xxxx'
            instrument_name: An optional name for the underlying instrument.
        """
        super().__init__(address)
        ip_and_port = address.split(':')
        name = instrument_name if instrument_name is not None else self.name
        if instrument_class is None:
            instrument_class = AMI430
        self._instrument: AMI430 = instrument_class(name=name, address=ip_and_port[0], port=int(ip_and_port[1]))
        self.field_variation_tolerance = 0.01

    def apply(self, config: PythonJsonStructure) -> None:
        """ Does not apply config only  compares config to device settings.

        Configuration Parameter with setter commands are matched for equality, on mismatch
        error is raised

        Args:
            config: Containing the instrument configuration.
        """
        super().apply(config)

    def _filter_parameters(self, parameters: PythonJsonStructure) -> PythonJsonStructure:
        for values in parameters.values():
            if 'val_mapping' in values:
                values.pop('val_mapping')
        return parameters

    def _compare_config_values(self, config_value: Any, device_value: Any, parameter: Optional[str] = None) -> bool:
        if parameter == 'field':
            delta = math.fabs(config_value - device_value)
            return delta > self.field_variation_tolerance
        else:
            return bool(config_value != device_value)
