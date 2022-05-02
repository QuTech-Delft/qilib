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
from queue import Queue, Empty
from threading import Thread, ThreadError
from typing import Optional, Any, Dict, List

from pymongo.change_stream import CollectionChangeStream
from pymongo.errors import InvalidOperation, OperationFailure

from qilib.data_set.data_set import DataSet
from qilib.data_set.data_array import DataArray
from qilib.data_set.mongo_data_set_io import MongoDataSetIO
from qilib.data_set.data_set_io_reader import DataSetIOReader

watchers = []


class MongoDataSetIOReader(DataSetIOReader):
    """ Allows a DataSet to subscribe to changes, and updates, in a mongodb."""

    THREAD_ERROR = 'thread_error'

    def __init__(self, name: Optional[str] = None, document_id: Optional[str] = None,
                 database: str = MongoDataSetIO.DEFAULT_DATABASE_NAME,
                 collection: str = MongoDataSetIO.DEFAULT_COLLECTION_NAME) -> None:
        """ DataSetIOReader implementation for a mongodb.

        Note:
            The finalize method has to be called to close database connection and join the watcher thread.

        Args:
            name: Name of data set in the underlying mongodb.
            document_id: Name of data set in the underlying mongodb.
            database: Name of the database.
            collection: Name of the collections.
        Raises:
            DocumentNotFoundError: If no data set with document_id or name found in database.

        """

        super().__init__()
        self._name = name
        self._id = document_id
        self._mongo_data_set_io = MongoDataSetIO(name, document_id, create_if_not_found=False, database=database,
                                                 collection=collection)
        self._set_arrays: Dict[str, DataArray] = {}
        self._watcher = self._mongo_data_set_io.watch()
        watchers.append(self._watcher)
        self._update_queue = Queue()  # type: ignore
        self._update_thread = Thread(target=self._update_worker, args=(self._update_queue, self._watcher))
        self._update_thread.daemon = True
        self._update_thread.start()
        self._data_set: Any = None

    def __del__(self) -> None:
        self._watcher.close()
        watchers.remove(self._watcher)
        self._update_thread.join(1)

    def sync_from_storage(self, timeout: float) -> None:
        """ Poll the Mongo database for changes and apply any to the bound data_set.

        Args:
            timeout: Stop syncing if collecting an item takes longer than the timeout time.
                The timeout can be -1 (blocking), 0 (non-blocking), or >0 (wait at most that many seconds).

        Raises:
            TimeoutError: If timeout is reached while the storage queue is still empty

        """
        blocking = timeout != 0
        empty_queue = self._update_queue.empty() if timeout == 0 else False
        while not empty_queue:
            try:
                document = self._update_queue.get(blocking, timeout if timeout > 0 else None)
            except Empty as e:
                raise TimeoutError from e
            if MongoDataSetIOReader.THREAD_ERROR in document:
                raise ThreadError('Watcher thread has stopped unexpectedly.') from document[
                    MongoDataSetIOReader.THREAD_ERROR]
            updated_fields = document['updateDescription']['updatedFields']
            adjusted_updates = self._convert_dot_notation_to_dict(updated_fields)
            self._update_data_set(adjusted_updates)
            empty_queue = self._update_queue.empty()

    def _convert_dot_notation_to_dict(self, updated_fields: Dict[str, Any]) -> Dict[str, Any]:
        """ If a nested field is updated in the mongo database, the nested document is replace with a dot notation that
            does not match the data set that is to be updated.
            For example:
                {data_arrays.array_name: {<data>}}
            Needs to be converted to:
                {data_arrays: {array_name: {<data>}}

        Args:
            updated_fields: An update event from the mongo database change stream.

        Returns:
            An updated dictionary without the dot notation.

        """
        adjusted_updates: Dict[str, Any] = {}
        for update in updated_fields.keys():
            key = update.split('.')
            if len(key) > 1 and key[1].isnumeric():
                # {array_updates.index: [<index>, <data>] -> {array_updates: [[<index>, <data>]]
                adjusted_updates[key[0]] = [updated_fields[update]]
            elif len(key) > 1 and (key[0] == self.DATA_ARRAYS or key[0] == self.METADATA):
                # {data_arrays.array_name: {<data>}} -> {data_arrays: {array_name: {<data>}}
                adjusted_updates[key[0]] = {key[1]: updated_fields[update]}
            else:
                adjusted_updates[key[0]] = updated_fields[update]
        return adjusted_updates

    def bind_data_set(self, data_set: DataSet) -> None:
        """ Binds the DataSet to the DataSetIOReader.

        Args:
            data_set: The object that encompasses DataArrays.

        """
        self._data_set = data_set
        document = self._mongo_data_set_io.get_document()
        self._data_set.name = document.get('name')
        self._update_data_set(document)

    def _update_data_set(self, document: Any) -> None:

        if self.METADATA in document:
            for field, value in document.get(self.METADATA).items():
                setattr(self._data_set, field, value)
        if self.DATA_ARRAYS in document:
            set_arrays = list(filter(lambda a: a['is_setpoint'], document.get(self.DATA_ARRAYS).values()))
            self._update_set_arrays(set_arrays)
            data_arrays = list(filter(lambda a: not a['is_setpoint'], document.get(self.DATA_ARRAYS).values()))
            for array in data_arrays:
                if hasattr(self._data_set, array['name']):
                    self._update_data_array(array)
                else:
                    self._data_set.add_array(self._construct_data_array(array))
        if self.ARRAY_UPDATES in document:
            for array_update in document.get(self.ARRAY_UPDATES):
                index_or_slice = tuple(array_update[0]) if isinstance(array_update[0], list) else array_update[0]
                data = array_update[1]
                self._data_set.add_data(index_or_slice, data)

    @staticmethod
    def load(name: Optional[str] = None, document_id: Optional[str] = None,
             database: str = MongoDataSetIO.DEFAULT_DATABASE_NAME,
             collection: str = MongoDataSetIO.DEFAULT_COLLECTION_NAME) -> DataSet:
        """ Load an existing data set from the mongodb.

        Args:
            name: Name of the data set.
            document_id: _id of the data set.
            database: Name of the database.
            collection: Name of the collections.

        Returns:
            A new instance of the underlying data set.

        Raises:
            DocumentNotFoundError: If document_id or name do not match any data set in database.

        """
        reader = MongoDataSetIOReader(name, document_id, database=database, collection=collection)
        return DataSet(storage_reader=reader)

    def _update_set_arrays(self, arrays: List[Dict[str, Any]]) -> None:
        for array in arrays:
            if array['name'] not in self._set_arrays:
                self._set_arrays[array['name']] = self._construct_data_array(array)

    def _construct_data_array(self, array: Dict[str, Any]) -> DataArray:
        set_arrays = [self._set_arrays[name] for name in array['set_arrays']]
        data_array = DataArray(name=array['name'],
                               label=array['label'],
                               unit=array['unit'],
                               is_setpoint=array['is_setpoint'],
                               preset_data=MongoDataSetIO.decode_numpy_array(array['preset_data']),
                               set_arrays=set_arrays)
        return data_array

    def _update_data_array(self, array: Dict[str, Any]) -> None:
        np_array = MongoDataSetIO.decode_numpy_array(array['preset_data'])
        self._data_set.data_arrays[array['name']].label = array['label']
        self._data_set.data_arrays[array['name']].unit = array['unit']

        for i in range(len(np_array)):
            self._data_set.data_arrays[array['name']][i] = np_array[i]

    @staticmethod
    def _update_worker(queue: Any, watcher: CollectionChangeStream[Any]) -> None:
        try:
            while True:
                document = watcher.next()
                queue.put(document)
        except (StopIteration, InvalidOperation, OperationFailure) as e:
            queue.put({MongoDataSetIOReader.THREAD_ERROR: e})
