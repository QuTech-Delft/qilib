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

from collections.abc import Sequence
from datetime import datetime
from typing import Any, Union, Tuple, List, Dict, Optional

from qilib.data_set.data_array import DataArray
from qilib.data_set.type_aliases import DataArrays
from qilib.utils.python_json_structure import PythonJsonStructure


class DataSet:
    """ A DataSet is an object that encompasses DataArrays.

    A DataArray can have another DataArray (or multiple) as setpoint(s).
    A DataSet can have multiple measurement arrays sharing the same setpoints.
    It is an error to have multiple measurement arrays with different setpoints.
    """

    def __init__(self, storage_writer: Any = None, storage_reader: Any = None, name: str = '',
                 time_stamp: Optional[datetime] = None, user_data: Optional[PythonJsonStructure] = None,
                 data_arrays: Optional[DataArrays] = None, set_arrays: Optional[List[DataArray]] = None) -> None:
        """
        Args:
            storage_writer: Object providing a storage backend.
            name: Name for the DataSet.
            time_stamp: Time of the measurement. datetime.now is used if not provided.
            user_data: User meta-data. E.g. instrument snapshot.
            data_arrays: DataArrays used in the experiment/
            set_arrays: None or more setpoint arrays.

        Raises:
            TypeError: If data_arrays are not of type DataArray.
            ValueError: If setpoints are provided and don't match those of the data_arrays or if multiple data_arrays
                are provided with various set_arrays.
        """
        self._finalized = False
        self._storage_writer = storage_writer if storage_writer is not None else []
        if not isinstance(self._storage_writer, Sequence):
            self._storage_writer = [self._storage_writer]
        self._storage_reader = storage_reader
        self._name = name
        self._time_stamp = datetime.now() if time_stamp is None else time_stamp
        self._user_data = user_data
        self._data_arrays: Dict[str, DataArray] = {}
        self._default_array_name = ""
        self._set_arrays: Dict[str, DataArray] = {}
        if set_arrays is not None:
            self._add_set_arrays(set_arrays)
        if data_arrays is not None:
            self._add_data_arrays(data_arrays)
        if self._storage_reader is not None:
            self._storage_reader.bind_data_set(self)

    def __repr__(self) -> str:
        return "DataSet(id=%r, name=%r, storage_writer=%r, storage_reader=%r, time_stamp=%r, user_data=%r, " \
               "data_arrays=%r, set_arrays=%r)" % (
                   id(self), self._name, self._storage_writer, self._storage_reader, self._time_stamp, self._user_data,
                   self._data_arrays, self._set_arrays)

    def __str__(self) -> str:
        heading = "{}: {}".format(self.__class__.__name__, self._name)
        table = [['name', 'label', 'unit', 'shape', 'setpoint']]
        for name, array in self._data_arrays.items():
            table.append([name, array.label, array.unit, str(array.shape), str(array.is_setpoint)])
        for array in self._set_arrays.values():
            table.append([array.name, array.label, array.unit, str(array.shape), str(array.is_setpoint)])
        return heading + self._format_str(table)

    def add_array(self, array: DataArray) -> None:
        """
        Args:
            array (DataArray): Array to be added to the experiment.

        Raises:
            ValueError: If an array with the same name has already been added.
            ValueError: If setpoints of the array do not match already added setpoints.
            SyntaxError: If array name is not a valid identifier.
        """

        self._verify_array_name(array.name)
        if len(self._set_arrays) == 0:
            self._add_set_arrays(array.set_arrays)
        else:
            self._verify_set_points(array.set_arrays)
        self._data_arrays[array.name] = array
        setattr(self, array.name, array)
        self._default_array_name = self._default_array_name or array.name
        for storage in self._storage_writer:
            storage.sync_add_data_array_to_storage(array)

    def add_data(self, index_or_slice: Union[Tuple[int, ...], int], data: Dict[str, Union[List[Any], Any]]) -> None:
        """ Update an underlying DataArray.

        Args:
            index_or_slice: Setpoints, can be an int or tuple of integers.
            data: Key is the name of the array and the dict value is the data.
        """

        for array_name, data_value in data.items():
            if array_name in self._data_arrays:
                self._data_arrays[array_name][index_or_slice] = data_value
            elif array_name in self._set_arrays:
                self._set_arrays[array_name][index_or_slice] = data_value
            else:
                raise LookupError(f'No such array with name \'{array_name}\' in data set')

        for storage in self._storage_writer:
            storage.sync_data_to_storage(index_or_slice, data)

    def sync_from_storage(self, timeout: int) -> None:
        """ Poll the DataSetIO for changes and apply any to the in-memory representation.
            Timeout can be:
                -1 (blocking),
                 0 (non-blocking)
                >0 (wait at most that many seconds)

        Args:
            timeout: Time to wait in seconds.

        Raises:
            TimeoutError: If storage is empty when timeout has passed.

        """
        if self._storage_reader is not None:
            self._storage_reader.sync_from_storage(timeout)

    def save_to_storage(self) -> None:
        """ Save DataSet to underlying storage."""
        for metadata in ['name', 'time_stamp', 'user_data', 'default_array_name', '_finalized']:
            self._add_metadata_to_storage(metadata, getattr(self, metadata))
        for array in self._set_arrays.values():
            self._add_array_to_storage(array)
        for array in self._data_arrays.values():
            self._add_array_to_storage(array)

    def finalize(self) -> None:
        """ Indicates to DataSetIOWriters that no more data will be written."""
        self._finalized = True
        self.save_to_storage()
        for storage in self._storage_writer:
            storage.finalize()

    def add_storage_writer(self, storage_writer: Any) -> None:
        """ Add a new DataSetIOStorageWriter to the DataSet

        Args:
            storage_writer: A new initialized storage writer.

        """
        if self._storage_reader is not None:
            raise ValueError("It is not allowed to have both storage_reader and storage_writer.")
        self._storage_writer.append(storage_writer)
        self.save_to_storage()

    @property
    def is_finalized(self) -> bool:
        return self._finalized

    @property
    def storage(self) -> Any:
        return self._storage_writer or self._storage_reader

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        self._add_metadata_to_storage('name', name)
        self._name = name

    @property
    def data_arrays(self) -> Dict[str, 'DataArray']:
        return self._data_arrays

    @property
    def set_arrays(self) -> Dict[str, 'DataArray']:
        return self._set_arrays

    @property
    def time_stamp(self) -> datetime:
        return self._time_stamp

    @time_stamp.setter
    def time_stamp(self, time_stamp: datetime) -> None:
        self._time_stamp = time_stamp
        self._add_metadata_to_storage('time_stamp', time_stamp)

    @property
    def user_data(self) -> Union[None, PythonJsonStructure]:
        return self._user_data

    @user_data.setter
    def user_data(self, user_data: PythonJsonStructure) -> None:
        self._user_data = user_data
        self._add_metadata_to_storage('user_data', user_data)

    @property
    def default_array_name(self) -> str:
        return self._default_array_name

    @default_array_name.setter
    def default_array_name(self, default_array_name: str) -> None:
        self._default_array_name = default_array_name
        self._add_metadata_to_storage('default_array_name', default_array_name)

    def _verify_set_points(self, set_arrays: DataArrays) -> None:
        if list(self._set_arrays.values()) != list(set_arrays):
            raise ValueError('Set point arrays do not match.')

    def _add_set_arrays(self, set_arrays: DataArrays) -> None:
        if isinstance(set_arrays, DataArray):
            set_arrays = [set_arrays]
        elif not isinstance(set_arrays, Sequence):
            raise TypeError("'set_arrays' have to be of type 'DataArray', not {}".format(type(set_arrays)))

        for array in set_arrays:
            self._verify_array_name(array.name)
            self._set_arrays[array.name] = array
            setattr(self, array.name, array)
            for storage in self._storage_writer:
                storage.sync_add_data_array_to_storage(array)

    def _verify_array_name(self, name: str) -> None:
        if not isinstance(name, str):
            raise ValueError("Array name has to be string, not {}".format(type(name)))
        if not name.isidentifier():
            raise SyntaxError("'{}' is an invalid name for an identifier.".format(name))
        if hasattr(self, name):
            raise ValueError("DataSet already contains an array with the name '{}'".format(name))

    def _add_data_arrays(self, data_arrays: DataArrays) -> None:
        if isinstance(data_arrays, Sequence):
            for array in data_arrays:
                self._add_data_arrays(array)
        elif isinstance(data_arrays, DataArray):
            self.add_array(data_arrays)
        else:
            raise TypeError("'data_arrays' have to be of type 'DataArray', not {}".format(type(data_arrays)))

    @staticmethod
    def _format_str(table: List[List[str]]) -> str:
        row_template = '\n  {info[0]:{lens[0]}} | {info[1]:{lens[1]}} | {info[2]:{lens[2]}} | {info[3]:{lens[3]}} | ' \
                       '{info[4]}'
        formatted_string = ''
        column_lengths = []
        for i in range(4):
            column_lengths.append(len(max(table, key=lambda t: len(t[i]))[i]))
        for row in table:
            formatted_string += row_template.format(info=row, lens=column_lengths)
        return formatted_string

    def _add_metadata_to_storage(self, field_name: str, value: Any) -> None:
        for storage in self._storage_writer:
            storage.sync_metadata_to_storage(field_name, value)

    def _add_array_to_storage(self, array: DataArray) -> None:
        for storage in self._storage_writer:
            storage.sync_add_data_array_to_storage(array)
