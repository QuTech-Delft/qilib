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
from typing import Union, List, Optional

from qilib.configuration_helper.instrument_configuration import InstrumentConfiguration
from qilib.configuration_helper.visitor import Visitor
from qilib.configuration_helper.exceptions import DuplicateTagError
from qilib.utils.storage.interface import StorageInterface


class InstrumentConfigurationSet:
    """ The complete set of configurations for all instruments in the system. """

    STORAGE_BASE_TAG = 'configuration_set'

    def __init__(self, storage: StorageInterface, tag: Optional[List[str]] = None,
                 instrument_configurations: Optional[List[InstrumentConfiguration]] = None) -> None:
        """ A set of instrument configurations

        Args
            storage: Any storage that implements the StorageInterface
            tag: A unique identifier for a instrument configuration set
            instrument_configurations: A list of instrument configurations
        """

        self._storage = storage
        self._tag = [self.STORAGE_BASE_TAG, StorageInterface.datetag_part()] if tag is None else tag
        if instrument_configurations is None:
            instrument_configurations = []
        self._instrument_configurations = instrument_configurations

    def __repr__(self) -> str:
        repr_string = f'{self.__class__.__name__}({self._storage!r}, {self._tag!r}, ' \
            f'{self._instrument_configurations!r})'
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
    def instrument_configurations(self) -> List[InstrumentConfiguration]:
        """ The instrument configurations in this set """

        return self._instrument_configurations

    @staticmethod
    def load(tag: List[str], storage: StorageInterface) -> 'InstrumentConfigurationSet':
        """ A factory that creates a new InstrumentConfigurationSet by loading from database

        Args:
            tag: A unique identifier for a instrument configuration set
            storage: Any storage that implements the StorageInterface

        Returns:
            A new InstrumentConfigurationSet loaded from the storage
        """

        # load the document as a list of instruments tags
        tags = storage.load_data(tag)
        instrument_configurations = [InstrumentConfiguration.load(instrument_tag, storage) for instrument_tag in tags]

        return InstrumentConfigurationSet(storage, tag, instrument_configurations)

    def store(self) -> None:
        """ Saves object to storage

         Raises:
             DuplicateTagError: If this object's tag is already in the database.
        """

        if self._storage.tag_in_storage(self._tag):
            raise DuplicateTagError(f'InstrumentConfiguration with tag \'{self._tag}\' already in storage')

        instrument_configuration_tags = []
        for instrument_configuration in self.instrument_configurations:
            try:
                instrument_configuration.store()
            except DuplicateTagError:
                pass
            finally:
                instrument_configuration_tags.append(instrument_configuration.tag)

        # save the document as a list of instruments tags
        self._storage.save_data(instrument_configuration_tags, self._tag)

    def snapshot(self, tag: Union[None, List[str]] = None) -> None:
        """ Updates the configuration set by overwriting the tag and refreshing all underlying instruments """

        self._tag = [self.STORAGE_BASE_TAG, StorageInterface.datetag_part()] if tag is None else tag

        for instrument_configuration in self._instrument_configurations:
            instrument_configuration.refresh()

    def apply(self) -> None:
        """ Uploads the configurations to the instruments """

        for instrument_configuration in self.instrument_configurations:
            instrument_configuration.apply()

    def apply_delta(self) -> None:
        """ Compare configurations with instruments and apply configurations that differs """

        for instrument_configuration in self.instrument_configurations:
            instrument_configuration.apply_delta()

    def apply_delta_lazy(self) -> None:
        """ Compare configurations with instrument drivers last known settings and apply configurations that differs """

        for instrument_configuration in self.instrument_configurations:
            instrument_configuration.apply_delta_lazy()

    def accept(self, visitor: Visitor) -> None:
        """ Accepts a visitor and propagates to instrument configurations.

        Args:
            visitor: An implementation of the Visitor interface.

        """
        for instrument_configuration in self.instrument_configurations:
            instrument_configuration.accept(visitor)
