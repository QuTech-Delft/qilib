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
from typing import Tuple

from qilib.data_set.memory_data_set_io_reader import MemoryDataSetIOReader
from qilib.data_set.memory_data_set_io_writer import MemoryDataSetIOWriter
from qilib.utils.memory_storage_queue import MemoryStorageQueue


class MemoryDataSetIOFactory:
    """ Provides MemoryDataSetIO Reader/Writer pairs sharing one storage queue."""

    @staticmethod
    def get_reader_writer_pair() -> Tuple[MemoryDataSetIOReader, MemoryDataSetIOWriter]:
        """ Instantiate a new memory IO pair.

        Returns:
            Memory data set IO reader and writer pair sharing one storage queue.

        """
        storage_queue = MemoryStorageQueue()
        memory_io_reader = MemoryDataSetIOReader(storage_queue)
        memory_io_writer = MemoryDataSetIOWriter(storage_queue)

        return memory_io_reader, memory_io_writer
