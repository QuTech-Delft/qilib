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
from copy import deepcopy
from typing import Any, Union, Dict, Tuple

from qilib.data_set.data_array import DataArray
from qilib.data_set.data_set_io_writer import DataSetIOWriter
from qilib.utils.memory_storage_queue import MemoryStorageQueue


class MemoryDataSetIOWriter(DataSetIOWriter):
    """ Allow a DataSet to write changes to an in-memory data storage queue."""

    def __init__(self, storage_queue: MemoryStorageQueue) -> None:
        """ Construct a new instance of MemoryDataSetIOWriter.
            This should not be called directly but a Reader/Writer pair should be created with
            the MemoryDataSetIOFactory.

        Args:
            storage_queue: Fifo shared with a MemoryDataSetIOWriter.
        """
        super().__init__()
        self._storage_queue = storage_queue

    def sync_metadata_to_storage(self, field_name: str, value: Any) -> None:
        self._storage_queue.add_meta_data(field_name, value)

    def sync_data_to_storage(self, index_or_slice: Union[int, Tuple[int]], data: Dict[str, Any]) -> None:
        self._storage_queue.add_data(index_or_slice, data)

    def sync_add_data_array_to_storage(self, data_array: DataArray) -> None:
        self._storage_queue.add_array(deepcopy(data_array))

    def finalize(self) -> None:
        raise NotImplementedError('The finalize function cannot be used with the MemoryDataSetIOWriter!')
