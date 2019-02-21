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

import queue

from qilib.data_set import DataSetIO


class MemoryDataSetIO(DataSetIO):

    def __init__(self):
        """ Allows synchronization between different instances of a DataSet in the same thread."""
        self.__user_data_storage = queue.Queue()
        self.__data_array_storage = queue.Queue()
        self._data_set = None
        self._is_finalized = False

    def bind_data_set(self, data_set):
        """ Binds the DataSet to the MemoryDataSetIO.

            You can bind a dataset only once to an DataSetIO instance.

        Args:
            data_set (DataSet): A data set instance with data.
        """
        if self._data_set:
            raise AttributeError('Dataset already bound!')
        self._data_set = data_set

    def __is_bounded(self):
        if not self._data_set:
            raise ValueError('No dataset bound to MemoryDataSetIO!')

    @property
    def data_set(self):
        self.__is_bounded()
        return self._data_set

    def sync_from_storage(self, timeout):
        """ Poll the MemoryDataSetIO for changes and apply any to the in-memory DataSet representation.

        Args:
            timeout (float): Stop syncing if collecting an item takes more then a the timeout time.
                             The timeout can be -1 (blocking), 0 (non-blocking), or >0 (wait at most that many seconds).
        """
        self.__is_bounded()
        if timeout < 0:
            self.__sync_storage(blocking=True, timeout=None)
            return
        if timeout == 0:
            self.__sync_storage(blocking=False, timeout=None)
            return
        self.__sync_storage(blocking=False, timeout=timeout)

    def __sync_storage(self, blocking=True, timeout=None):
        while not self.__user_data_storage.empty():
            try:
                field_name, value = self.__user_data_storage.get(blocking, timeout)
                self._data_set.user_data[field_name] = value
            except queue.Empty:
                return

        while not self.__data_array_storage.empty():
            try:
                data_array = self.__data_array_storage.get(blocking, timeout)
                self._data_set.add_array(data_array)
            except queue.Empty:
                return

    def sync_data_to_storage(self, data_array, index_spec):
        """ Registers a data array update.

        Args:
            data_array (DataArrray): An data array with data.
            index_spec (int, tuple[int]): The indices of the dataset to update.

        Raises:
            ValueError: When the data array with specific name is not added to the storage.
        """
        self.__is_bounded()
        self.__is_not_finalized()
        data_arrays_storage = list(self.__data_array_storage.queue)
        length_storage = len(data_arrays_storage)

        index = next((i for i in range(length_storage) if data_arrays_storage[i].name == data_array.name), None)
        if index is None:
            raise ValueError('The data array name if not present and cannot be updated!')

        data_arrays_storage[index][index_spec] = data_array[index_spec]
        self.__data_array_storage.deque = queue.deque(data_arrays_storage)

    def sync_metadata_to_storage(self, field_name, value):
        """ Registers a change to the user metadata field.

        Args:
            field_name (str): The name of the meta data field.
            value (Any): The value of the field.
        """
        self.__is_bounded()
        self.__is_not_finalized()
        self.__user_data_storage.put((field_name, value))

    def sync_add_data_array_to_storage(self, data_array):
        """ Registers a new data array event for syncing to the different dataset instance.

        Args:
            data_array (DataArray): An data array with data.
        """
        self.__is_bounded()
        self.__is_not_finalized()
        self.__data_array_storage.put(data_array)

    @staticmethod
    def load():
        """ A MemoryDataSetIO is used for syncronisation between data sets, and cannot be loaded in."""
        raise NotImplementedError('The load function cannot be used with the MemoryDataSetIO!')

    def finalize(self):
        """ Sets the MemoryDatasetIO to read-only."""
        self.__is_bounded()
        self.__is_not_finalized()
        self._is_finalized = True

    def __is_not_finalized(self):
        if self._is_finalized:
            raise AttributeError('MemoryDataSetIO already finalized!')
