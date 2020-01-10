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
from typing import List, Optional

from qilib.configuration_helper.instrument_adapter_factory import InstrumentAdapterFactory
from qilib.configuration_helper.exceptions import DuplicateTagError
from qilib.configuration_helper.visitor import Visitor
from qilib.utils.python_json_structure import PythonJsonStructure
from qilib.utils.storage.interface import StorageInterface


class InstrumentConfiguration:
    """ Associates a configuration with an InstrumentAdapter and allows it to be stored or retrieved from storage."""

    STORAGE_BASE_TAG = 'configuration'

    def __init__(self, adapter_class_name: str, address: str, storage: StorageInterface,
                 tag: Optional[List[str]] = None, configuration: Optional[PythonJsonStructure] = None,
                 instrument_name: Optional[str] = None) -> None:
        """ A set of instrument configurations

        Args
            instrument_adapter_class_name: Name of the InstrumentAdapter subclass
            address: Address of the physical instrument
            storage: Any storage that implements the StorageInterface
            tag: A unique identifier for a instrument configuration set
            configuration: The instrument configuration
            instrument_name: User defined name for the instrument
        """
        self._adapter_class_name = adapter_class_name
        self._address = address
        self._storage = storage
        self._instrument_name = instrument_name
        self._adapter = InstrumentAdapterFactory.get_instrument_adapter(adapter_class_name, address, instrument_name)
        self._configuration = PythonJsonStructure() if configuration is None else configuration
        self._tag = [self.STORAGE_BASE_TAG, adapter_class_name, StorageInterface.datetag_part()] if tag is None else tag

    def __repr__(self) -> str:
        repr_string = f'{self.__class__.__name__}({self._adapter_class_name!r}, {self._address!r}, {self._storage!r}, '\
            f'{self._tag!r}, {self._configuration!r}, {self._instrument_name!r})'
        return repr_string

    @property
    def tag(self) -> List[str]:
        """ A unique identifier for this instrument configuration set """
        return self._tag

    @property
    def storage(self) -> StorageInterface:
        """ The storage interface used """
        return self._storage

    @property
    def address(self) -> str:
        """ The address of the physical instrument """
        return self._address

    @property
    def configuration(self) -> PythonJsonStructure:
        """ The instrument configuration """
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
        instrument_name = document.get('instrument_name', None)
        configuration = document['configuration']
        return InstrumentConfiguration(adapter_class_name, address, storage, tag, configuration, instrument_name)

    def store(self) -> None:
        """ Saves object to storage.

         Raises:
             DuplicateTagError: If this object's tag is already in the database.

        """
        if self._storage.tag_in_storage(self._tag):
            raise DuplicateTagError(
                f"InstrumentConfiguration for {self._adapter_class_name} with tag '{self._tag}' already in storage")
        document = PythonJsonStructure(adapter_class_name=self._adapter_class_name,
                                       address=self._address,
                                       instrument_name=self._instrument_name,
                                       configuration=self._configuration)
        self._storage.save_data(document, self._tag)

    def apply(self) -> None:
        """ Uploads the configuration to the instrument."""
        self._adapter.apply(self._configuration)

    def apply_delta(self, update: bool = True) -> None:
        """ Compare configuration with instrument and apply configuration that differs.

        Args:
            update: If True, request all parameter values from instrument, else use latest set values.

        """
        instrument_config = self._adapter.read(update=update)
        delta = self._get_configuration_delta(instrument_config)
        self._adapter.apply(delta)

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
        instrument_config = self._adapter.read(update=True)
        delta = self._get_configuration_delta(instrument_config)
        if len(delta) > 0 or len(instrument_config) != len(self._configuration):
            self._configuration = instrument_config
            self._tag = [self.STORAGE_BASE_TAG, self._adapter_class_name, StorageInterface.datetag_part()]

    def accept(self, visitor: Visitor) -> None:
        """ Accept a visitor, run visit method with self as a parameter and propagate to instrument adapter.

        Args:
            visitor: An implementation of the Visitor interface.

        """
        visitor.visit(self)
        self._adapter.accept(visitor)
