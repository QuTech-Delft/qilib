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
from typing import List, Any, Optional

from qilib.configuration_helper.instrument_configuration_set import InstrumentConfigurationSet
from qilib.utils.storage.interface import StorageInterface


class ConfigurationHelper:
    """  Provides access to the instrument configuration database and maintains two InstrumentConfigurationSets."""

    def __init__(self, storage: StorageInterface,
                 active_configuration: Optional[InstrumentConfigurationSet] = None,
                 inactive_configuration: Optional[InstrumentConfigurationSet] = None) -> None:
        """ Instantiate a new ConfigurationHelper.

        Args:
            storage: A StorageInterface that stores configurations.
            active_configuration: An optional instrument configuration set.
            inactive_configuration: An optional inactive instrument configuration set.
        """
        if active_configuration is not None:
            self._active_configuration = active_configuration
        else:
            self._active_configuration = InstrumentConfigurationSet(storage)
        if inactive_configuration is not None:
            self._inactive_configuration = inactive_configuration
        else:
            self._inactive_configuration = InstrumentConfigurationSet(storage)
        self._storage = storage

    def __repr__(self) -> str:
        repr_string = f'{self.__class__.__name__}({self._storage!r}, {self._active_configuration!r}, ' \
            f'{self._inactive_configuration!r})'
        return repr_string

    def snapshot(self, tag: Optional[List[str]] = None) -> None:
        """ Refresh the active configuration set so it reflects thee actual settings of the devices.

        Args:
            tag: Unique identifier for an InstrumentConfigurationSet. If no tag is provided it will be generated based
                on current time and date.

        """
        self._active_configuration.snapshot(tag)

    @property
    def active_configuration(self) -> InstrumentConfigurationSet:
        """ The configuration set that is currently active."""
        return self._active_configuration

    @property
    def inactive_configuration(self) -> InstrumentConfigurationSet:
        """ The configuration set that is to be applied."""
        return self._inactive_configuration

    def retrieve_inactive_configuration_from_storage(self, tag: List[str]) -> None:
        """ Load configuration set from storage and set as inactive.

        Args:
            tag: Unique identifier for an InstrumentConfigurationSet.

        """
        self._inactive_configuration = InstrumentConfigurationSet.load(tag, self._storage)

    def write_active_configuration_to_storage(self) -> None:
        """ Write the active configuration set to storage."""
        self._active_configuration.store()

    def write_inactive_configuration_to_storage(self) -> None:
        """ Write the inactive configuration set to storage."""
        self._inactive_configuration.store()

    def apply_inactive(self) -> None:
        """ Apply inactive configuration and set as active."""
        self._inactive_configuration.apply()
        self._active_configuration = self._inactive_configuration

    def apply_inactive_delta(self) -> None:
        """ Call apply_delta on inactive configuration set and set it as active."""
        self._inactive_configuration.apply_delta()
        self._active_configuration = self._inactive_configuration

    def apply_inactive_delta_lazy(self) -> None:
        """ Call apply_delta_lazy on inactive configuration set and set it as active."""
        self._inactive_configuration.apply_delta_lazy()
        self._active_configuration = self._inactive_configuration

    def get_tag_by_label(self, label: str) -> Any:
        """ Retrieve tag from storage that has been assigned the given label.

        Args:
            label: A known configuration, e.g., 'online'.

        """
        return self._storage.load_data(['labels', label])

    def label_tag(self, label: str, tag: List[str]) -> None:
        """ Label a tag in storage with a given label.

        Args:
            label: A known configuration, e.g., 'online'.
            tag: The tag to label.

        """
        self._storage.save_data(tag, ['labels', label])
