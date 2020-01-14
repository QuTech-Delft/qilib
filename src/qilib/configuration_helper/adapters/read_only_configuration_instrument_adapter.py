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
from typing import Any, Optional
from abc import ABC, abstractmethod

from qilib.configuration_helper.instrument_adapter import InstrumentAdapter
from qilib.utils.python_json_structure import PythonJsonStructure


class ConfigurationError(Exception):
    """ Error to raise if configuration does not match."""


class ReadOnlyConfigurationInstrumentAdapter(InstrumentAdapter, ABC):
    """ Common methods to verify value mismatch on config apply"""

    def apply(self, config: PythonJsonStructure) -> None:
        """ Does comparison for config values with set command.

        Args:
            config: The configuration with settings for the adapters instrument.

        Raises:
            ConfigurationError: If config does not match device configuration .
        """
        if self._instrument is not None:
            device_config = self.read(True)
            for parameter in config:
                if parameter in self._instrument.parameters and hasattr(self._instrument.parameters[parameter], 'set'):
                    result = self._compare_config_values(config[parameter]['value'],
                                                         device_config[parameter]['value'], parameter)
                    if result:
                        self._raise_configuration_error(config[parameter]['value'], device_config[parameter]['value'],
                                                        parameter)

    @abstractmethod
    def _compare_config_values(self, config_value: Any, device_value: Any, parameter: Optional[str] = None) -> bool:
        """ Comparison logic for  configuration parameter values.
        This function should be overwritten in the subclasses for each specific instrument.

        Args:
            config_value: Configuration value as supplied as argument to apply
            device_value: Configuration value as read from the device
            parameter: Name of the configuration parameter with setter command (Optional)

        Returns:
            True or False based on the comparison result
        """

    @staticmethod
    def _raise_configuration_error(config_value: Any, device_value: Any, parameter: str) -> None:
        raise ConfigurationError(
            "Configuration for {} does not match: '{}' != '{}'".format(parameter, config_value, device_value))
