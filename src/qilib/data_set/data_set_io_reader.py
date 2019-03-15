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

from qilib.data_set import DataSet


class DataSetIOReader(ABC):

    @abstractmethod
    def bind_data_set(self, data_set: DataSet) -> None:
        """ Binds the DataSet to the DataSetIOReader.

        Args:
            data_set: The object that encompasses DataArrays.
        """

    @abstractmethod
    def sync_from_storage(self, timeout: float) -> None:
        """ Reads changes from the underlying storage backend and applies them to the bound DataSet.

        Args:
            timeout: Stop syncing after certain amount of time.
        """

    @staticmethod
    @abstractmethod
    def load() -> DataSet:
        """ Opens an existing DataSet from the underlying storage."""
