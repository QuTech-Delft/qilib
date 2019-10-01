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
import logging
from typing import Any
from abc import ABC, abstractmethod

from qilib.configuration_helper import InstrumentAdapter
from qilib.utils import PythonJsonStructure


class ConfigurationError(Exception):
    """ Error to raise if configuration does not match."""


class CommonInstrumentAdapter(InstrumentAdapter, ABC):

    def apply(self, config: PythonJsonStructure) -> None:
        """ Applies the given instrument configuration settings onto the adapters instrument.

        Only the setter commands will be updated.
        Note that setter only parameters which have not been set yield a None when reading the configuration from the
        instrument adapter. These None parameter values in the configuration will not be set. A warning will be
        given if any of the configuration parameter values are None.

        Args:
            config: The configuration with settings for the adapters instrument.

        """
        parameters = []
        for parameter in config:
            if parameter in self._instrument.parameters and hasattr(self._instrument.parameters[parameter], 'set'):
                parameters.append(parameter)

        if any(config[parameter]['value'] is None for parameter in parameters):
            error_message = 'Some parameter values of {0} are None and will not be set!'.format(self._instrument.name)
            logging.warning(error_message)
        for parameter in parameters:
            if 'value' in config[parameter] and config[parameter]['value'] is not None:
                self._instrument.set(parameter, config[parameter]['value'])

    def _config_with_setter_command_mismatch_raises_error(self, config: PythonJsonStructure) -> None:
        """ Does comparison for config values with set command.

        Args:
            config: The configuration with settings for the adapters instrument.

        Raises:
            ConfigurationError: If config does not match device configuration .

        """
        device_config = self.read(True)

        for parameter in config:
            if parameter in self._instrument.parameters and hasattr(self._instrument.parameters[parameter], 'set'):
                result = self._compare_config_values(config[parameter]['value'],
                                                              device_config[parameter]['value'], parameter)
                if (result is not None and result):
                    self._raise_configuration_error(config[parameter]['value'], device_config[parameter]['value'],
                                                    parameter)

    @abstractmethod
    def _filter_parameters(self, parameters: PythonJsonStructure) -> PythonJsonStructure:
        """ Filters out parameters that are not used for instrument configuration storage.

        This function should be overwritten in the subclasses for each specific instrument,
        if needed when reading the configuration.

        Args:
            parameters: A complete snapshot from an instrument.

        Returns:
            PythonJsonStructure: Contains the instrument snapshot without the instrument
                                 parameters which are filtered out by this function.
        """

    @abstractmethod
    def _compare_config_values(self, config_value: Any, device_value: Any, parameter: str) -> bool:
        """ Comparison logic for  configuration parameter values.

        This function should be overwritten in the subclasses for each specific instrument.
        In case for an instrument the configuration can not be applied this method should define the comparison

        Args:
            config_value: Configuration value as supplied as argument to apply
            device_value: Configuration value as read from the device
            parameter: Name of the configuration parameter with setter command

        Returns:
            True or False based on the comparison result
            None in case when there is no specific behavior needs to be implemented
        """

    @staticmethod
    def _raise_configuration_error(config_value: Any, device_value: Any, parameter: str) -> None:
            raise ConfigurationError(
                "Configuration for {} does not match: '{}' != '{}'".format(parameter, config_value, device_value))
