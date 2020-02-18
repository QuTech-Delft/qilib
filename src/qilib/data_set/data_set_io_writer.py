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
from typing import Any, Union, Dict, Tuple

from qilib.data_set.data_array import DataArray


class DataSetIOWriter(ABC):
    """ Abstract base class for data set io writers."""

    def __init__(self) -> None:
        self._finalized = False

    @abstractmethod
    def sync_metadata_to_storage(self, field_name: str, value: Any) -> None:
        """ Registers a change to a metadata field.

        This function creates a new field if the field name does not exists.

        Args:
            field_name: The metadata field name.
            value: The metadata value to change.
        """

    @abstractmethod
    def sync_data_to_storage(self, index_or_slice: Union[int, Tuple[int]], data: Dict[str, Any]) -> None:
        """ Registers a DataArray update to the DataSetIO.

        Args:
            index_or_slice: The indices of the DataArray to update.
            data: Name of the DataArray to be updated and the new value.
        """

    @abstractmethod
    def sync_add_data_array_to_storage(self, data_array: DataArray) -> None:
        """ Registers a new DataArray event.

        Args:
            data_array: A container for measurement data and setpoint arrays.
        """

    @abstractmethod
    def finalize(self) -> None:
        """ Sets the data IO to read-only.

            No more data will be written after applying this function and triggers the closing
            of file handles, or optimizes event streams.
        """

    def _is_finalized(self) -> None:
        if self._finalized:
            raise ValueError('Operation on closed IO writer.')
