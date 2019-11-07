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
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from qcodes import Instrument

from qilib.configuration_helper.visitor import Visitor
from qilib.utils import PythonJsonStructure


class InstrumentAdapter(ABC):

    def __init__(self, address: str, instrument_name: Optional[str] = None) -> None:
        """ A template for an adapter to the QCoDeS instrument interface.

        Args:
            address: The address/ID of the QCoDeS instrument.
        """
        self._name = f'{self.__class__.__name__}_{address}'
        self._address = address
        self._instrument: Instrument = None
        self._instrument_name = instrument_name if instrument_name is not None else self.name

    @property
    def name(self) -> str:
        return self._name

    @property
    def instrument(self) -> Instrument:
        return self._instrument

    @property
    def address(self) -> str:
        return self._address

    @abstractmethod
    def apply(self, config: PythonJsonStructure) -> None:
        """ An abstract method that should be implemented in subclasses.

        Writes a full set of configuration to the adapters instrument.

        Args:
            config: Containing the instrument configuration.
        """

    def read(self, update: bool = False) -> PythonJsonStructure:
        """ Obtains a full set of settings from the instrument.

        Returns:
            Part of the instrument snapshot, i.e., parameter values, without the instrument's
            parameters which are explicitly filtered out, and the instrument name.
        """
        configuration = PythonJsonStructure()
        if self._instrument is not None:
            snapshot = self._instrument.snapshot(update)
            parameters = self.__notify_and_remove_none_values(snapshot)
            configuration.update(self._filter_parameters(parameters))

        return configuration

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

    def close_instrument(self) -> None:
        """ Close the wrapped QCoDeS instrument."""
        if self._instrument is not None:
            self._instrument.close()

    def accept(self, visitor: Visitor) -> None:
        """ Accept a visitor and run visit method with self as a parameter.

        Args:
            visitor: An implementation of the Visitor interface.
        """
        visitor.visit(self)

    def __notify_and_remove_none_values(self, snapshot: PythonJsonStructure) -> PythonJsonStructure:
        """ Return parameters from the QCoDeS snapshot which are not None.

            Takes the parameters of the QCoDeS instrument snapshot. Removes all parameters
            which have a value of None. Returns the parameter settings which have a value.
            All parameters with None value will be listed in the log as an error.

        Args:
            snapshot: A QCoDeS instrument snapshot.

        Returns:
            PythonJsonStructure: Contains the instrument snapshot parameters without the
                                 instrument parameters which a none value.
        """
        parameters = PythonJsonStructure()
        non_value_parameters = PythonJsonStructure()
        for parameter_name, settings in snapshot['parameters'].items():
            if 'value' in settings and settings['value'] is None:
                non_value_parameters[parameter_name] = settings
            else:
                parameters[parameter_name] = settings

        if non_value_parameters:
            parameter_names = list(non_value_parameters.keys())
            error_message = f'Parameter values of {self._instrument_name} are None. Please set: {parameter_names}.'
            logging.error(error_message)

        return parameters

    def __str__(self) -> str:
        """ Returns string representation for the InstrumentAdapter.

        Returns:
            String representation for the InstrumentAdapter.
        """
        return f'InstrumentAdapter: {self.name}'
