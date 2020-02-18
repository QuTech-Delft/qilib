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
from queue import Queue
from typing import Union, Dict, Any, Tuple

from qilib.data_set.data_array import DataArray
from qilib.data_set.data_set_io_reader import DataSetIOReader


class MemoryStorageQueue(Queue):  # type: ignore
    """ A simple fifo storage queue shared between the MemoryDataSetIO Reader and Writer."""

    def add_data(self, index_or_slice: Union[int, Tuple[int]], data: Dict[str, Any]) -> None:
        self.put((DataSetIOReader.DATA, (index_or_slice, data)))

    def add_meta_data(self, *meta_data: Any) -> None:
        self.put((DataSetIOReader.METADATA, meta_data))

    def add_array(self, array: DataArray) -> None:
        self.put((DataSetIOReader.DATA_ARRAY, array))
