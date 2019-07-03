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
from typing import Any

from qcodes.instrument_drivers.american_magnetics.AMI430 import AMI430

from qilib.configuration_helper import InstrumentAdapter
from qilib.utils import PythonJsonStructure


class ConfigurationError(Exception):
    """ Error to raise if configuration does not match."""


class AMI430InstrumentAdapter(InstrumentAdapter):
    """ Adapter for the AMI430 QCoDeS driver."""

    def __init__(self, address: str) -> None:
        """ Instantiate a new AMI430 instrument adapter.

        Args:
            address: IP address and port number separated by a column, 'x.x.x.x:xxxx'

        """
        super().__init__(address)
        ip_and_port = address.split(':')
        self._instrument = AMI430(name=self.name, address=ip_and_port[0], port=int(ip_and_port[1]))
        self.field_variation_tolerance = 0.01

    def apply(self, config: PythonJsonStructure) -> None:
        """ Does not apply config to device, but compares config to device settings.

        Args:
            config: Containing the instrument configuration.

        Raises:
            ConfigurationError: If config does not match device configuration or difference in field value is greater
                than the field_variation_tolerance.

        """
        device_config = self.read(True)
        parameters = [parameter for parameter in config if hasattr(self._instrument.parameters[parameter], 'set')]
        for parameter in parameters:
            if parameter == 'field':
                self._check_field_value(config[parameter]['value'], device_config[parameter]['value'])
            elif 'value' in config[parameter]:
                self._assert_value_matches(config[parameter]['value'], device_config[parameter]['value'], parameter)

    def _filter_parameters(self, parameters: PythonJsonStructure) -> PythonJsonStructure:
        for values in parameters.values():
            if 'val_mapping' in values:
                values.pop('val_mapping')
        return parameters

    def _check_field_value(self, config_value: float, device_value: float) -> None:
        delta = math.fabs(config_value - device_value)
        if delta > self.field_variation_tolerance:
            raise ConfigurationError(
                "Target value for field does not match device value: {}T != {}T".format(config_value, device_value))

    @staticmethod
    def _assert_value_matches(config_value: Any, device_value: Any, parameter: str) -> None:
        if config_value != device_value:
            raise ConfigurationError(
                "Configuration for {} does not match: '{}' != '{}'".format(parameter, config_value, device_value))
