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
from queue import Empty

from qilib.data_set.data_set import DataSet
from qilib.data_set.data_set_io_reader import DataSetIOReader
from qilib.utils.memory_storage_queue import MemoryStorageQueue


class MemoryDataSetIOReader(DataSetIOReader):
    """ Allows a DataSet to subscribe to changes, and updates, in an in-memory data storage."""

    def __init__(self, storage_queue: MemoryStorageQueue) -> None:
        """ Construct a new instance of MemoryDataSetIOReader.
            This should not be called directly but a Reader/Writer pair should be created with
            the MemoryDataSetIOFactory.

        Args:
            storage_queue: Fifo shared with a MemoryDataSetIOWriter.
        """
        super().__init__()
        self._storage_queue = storage_queue

    def sync_from_storage(self, timeout: float) -> None:
        """ Poll the MemoryStorageQueue for changes and apply any to the bound data_set.

          Args:
              timeout: Stop syncing if collecting an item takes more then a the timeout time.
                       The timeout can be -1 (blocking), 0 (non-blocking), or >0 (wait at most that many seconds).

          Raises:
                TimeoutError: If timeout is reached while the storage queue is still empty
        """

        blocking = timeout != 0
        empty_queue = self._storage_queue.empty() if timeout == 0 else False
        while not empty_queue:
            try:
                data_type, storage_data = self._storage_queue.get(blocking, timeout if timeout > 0 else None)
            except Empty as e:
                raise TimeoutError from e

            if data_type == self.DATA_ARRAY:
                self._data_set.add_array(storage_data)
            elif data_type == self.DATA:
                self._data_set.add_data(*storage_data)
            elif data_type == self.METADATA:
                setattr(self._data_set, *storage_data)

            empty_queue = self._storage_queue.empty()

    @staticmethod
    def load() -> DataSet:
        """ MemoryDataSetReader has only a fifo storage queue and can therefor not load a
            DataSet from storage.
        """
        raise NotImplementedError('The load function cannot be used with the MemoryDataSetIOReader!')
