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
from abc import ABC, abstractmethod
from typing import List

from qilib.configuration_helper.instrument_adapter import InstrumentAdapter
from qilib.utils.python_json_structure import PythonJsonStructure


class CommonInstrumentAdapter(InstrumentAdapter, ABC):

    def apply(self, config: PythonJsonStructure) -> None:
        """ Applies the given instrument configuration settings onto the adapters instrument.

        Only the setter commands will be updated.
        Note that setter only parameters which have not been set yield a None when reading the configuration from the
        instrument adapter. The apply method will raise a ValueError if any of the configuration parameter values are
        None. The None value parameters are listed in the raised ValueError.

        Args:
            config: The configuration with settings for the adapters instrument.
        """
        if self._instrument is not None:
            parameters = []
            for parameter in config:
                if parameter in self._instrument.parameters and hasattr(self._instrument.parameters[parameter], 'set'):
                    parameters.append(parameter)

            self.__raise_none_value_parameters(config, parameters)
            for parameter in parameters:
                self._instrument.set(parameter, config[parameter]['value'])

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

    def __raise_none_value_parameters(self, config: PythonJsonStructure, parameters: List[PythonJsonStructure]) -> None:
        """ Raises a ValueError when one or more parameters in the configuration have value None.

        Args:
            config: A configuration with settings for the instrument adapter.
            parameters: A list with settable instrument parameters.
        """
        if self._instrument is not None:
            none_value_parameters = list(filter(lambda parameter: config[parameter]['value'] is None, parameters))
            if none_value_parameters:
                error_message = f'The following parameter(s) of {self._instrument.name} have value ' \
                                f'None and cannot be set: {none_value_parameters}!'
                raise ValueError(error_message)
