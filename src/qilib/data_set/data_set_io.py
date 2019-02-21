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

from abc import ABC, abstractmethod, abstractstaticmethod


class DataSetIO(ABC):

    @abstractmethod
    def bind_data_set(self, data_set):
        """ Binds the DataSet to the DataSetIO. Binding can be done only once on the same DataSetIO.

        Args:
            data_set (DataSet): A dataset with data.
        """

    @abstractmethod
    def sync_from_storage(self, timeout):
        """ Reads changes from the underlying storage backend and applies them to the bound DataSet.

        Args:
            timeout (float): Stop syncing after certain amount of time.
        """

    @abstractmethod
    def sync_metadata_to_storage(self, field_name, value):
        """ Registers a change to a metadata field.

        This function creates a new field if the field name does not exists.

        Args:
            field_name (string): The metadata field name.
            value (Any): The metadata value to change.
        """

    @abstractmethod
    def sync_data_to_storage(self, data_array, index_spec):
        """ Registers a data array update to the DataSetIO.

            data_array (DataArray): An data array with data.
            index_spec (int, tuple[int]): The indices of the dataset to update.
        """

    @abstractmethod
    def sync_add_data_array_to_storage(self, data_array):
        """ Registers a new data array event.

        Args:
            data_array (DataArray): An data array with data.
        """

    @abstractstaticmethod
    def load():
        """ Opens an existing DataSet from the underlying storage."""

    @abstractmethod
    def finalize(self):
        """ Sets the data IO to read-only.

            No more data will be written after applying this function and triggers the closing
            of file handles, or optimizes event streams.
        """
