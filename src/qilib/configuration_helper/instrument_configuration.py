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
from typing import List, Union

from qilib.configuration_helper import InstrumentAdapterFactory
from qilib.utils import PythonJsonStructure
from qilib.utils.storage.interface import StorageInterface


class DuplicateTagError(Exception):
    """ Raised if tag already in storage."""


class InstrumentConfiguration:
    """ Associates a configuration with an InstrumentAdapter and allows it to be stored or retrieved from storage."""

    def __init__(self, adapter_class_name: str, address: str, storage: StorageInterface,
                 tag: Union[None, List[str]] = None,
                 configuration: Union[None, PythonJsonStructure] = None) -> None:
        self._adapter_class_name = adapter_class_name
        self._address = address
        self._storage = storage
        self._instrument = InstrumentAdapterFactory.get_instrument_adapter(adapter_class_name, address)
        self._configuration = PythonJsonStructure() if configuration is None else configuration
        self._tag = [StorageInterface.datetag_part()] if tag is None else tag

    @property
    def tag(self) -> List[str]:
        return self._tag

    @property
    def address(self) -> str:
        return self._address

    @property
    def configuration(self) -> PythonJsonStructure:
        return self._configuration

    @staticmethod
    def load(tag: List[str], storage: StorageInterface) -> 'InstrumentConfiguration':
        """ A factory that creates a new InstrumentConfiguration by loading from database.

        Args:
            tag: A unique identifier for a instrument configuration.
            storage: Default mongo database, but can optionally be any storage that implements the StorageInterface.

        Returns:
            A new InstrumentConfiguration loaded from database.

        """
        document = storage.load_data(tag)
        adapter_class_name = document['adapter_class_name']
        address = document['address']
        configuration = document['configuration']
        return InstrumentConfiguration(adapter_class_name, address, storage, tag, configuration)

    def store(self) -> None:
        """ Saves object to storage.

         Raises:
             DuplicateTagError: If this object's tag is already in the database.

        """
        if self._storage.tag_in_storage(self._tag):
            raise DuplicateTagError("InstrumentConfiguration with tag '{}' already in storage".format(self._tag))
        document = PythonJsonStructure(adapter_class_name=self._adapter_class_name,
                                       address=self._address,
                                       configuration=self._configuration)
        self._storage.save_data(document, self._tag)

    def apply(self) -> None:
        """ Uploads the configuration to the instrument."""
        self._instrument.apply(self._configuration)

    def apply_delta(self, update: bool = True) -> None:
        """ Compare configuration with instrument and apply configuration that differs.

        Args:
            update: If True, request all parameter values from instrument, else use latest set values.

        """
        instrument_config = self._instrument.read(update=update)
        delta = self._get_configuration_delta(instrument_config)
        self._instrument.apply(delta)

    def _get_configuration_delta(self, instrument_config: PythonJsonStructure) -> PythonJsonStructure:
        delta = PythonJsonStructure()
        for parameter, configuration in self._configuration.items():
            if 'value' in configuration and configuration['value'] != instrument_config[parameter]['value']:
                delta[parameter] = configuration
        return delta

    def apply_delta_lazy(self) -> None:
        """ Compare configuration with instrument driver last known settings and apply configuration that differs."""
        self.apply_delta(update=False)

    def refresh(self) -> None:
        """ Read the settings from the instrument and updated configuration.

        If the settings read from the instrument differs from the configuration the tag is also updated.
        """
        instrument_config = self._instrument.read(update=True)
        delta = self._get_configuration_delta(instrument_config)
        if len(delta) > 0 or len(instrument_config) != len(self._configuration):
            self._configuration = instrument_config
            self._tag = [StorageInterface.datetag_part()]
