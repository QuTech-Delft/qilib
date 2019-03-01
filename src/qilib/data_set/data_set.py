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

import collections
from datetime import datetime

from qilib.data_set import DataArray


class DataSet:
    """ A DataSet is an object that encompasses DataArrays.

    A DataArray can have another DataArray (or multiple) as setpoint(s).
    A DataSet can have multiple measurement arrays sharing the same setpoints.
    It is an error to have multiple measurement arrays with different setpoints.
    """

    def __init__(self, storage=None, name='', time_stamp=None, user_data=None, data_arrays=None, set_arrays=None):
        """
        Args:
            storage (DataSetIO): Object providing a storage backend.
            name (str): Name for the DataSet.
            time_stamp (DateTime): Time of the measurement. datetime.now is used if not provided.
            user_data (PythonJsonStructure): User meta-data. E.g. instrument snapshot.
            data_arrays (dict): DataArrays used in the experiment/
            set_arrays (DataArray): None or more setpoint arrays.

        Raises:
            TypeError: If data_arrays are not of type DataArray.
            ValueError: If setpoints are provided and don't match those of the data_arrays or if multiple data_arrays
                are provided with various set_arrays.
        """

        self._storage = storage
        self._name = name
        self._time_stamp = datetime.now() if time_stamp is None else time_stamp
        self._user_data = user_data
        self._add_set_arrays(set_arrays)
        self._data_arrays = {}
        self._default_array_name = ""
        if data_arrays is not None:
            self._add_data_arrays(data_arrays)

    def __repr__(self):
        return "DataSet(id=%r, name=%r, storage=%r, time_stamp=%r, user_data=%r, data_arrays=%r, set_arrays=%r)" % (
            id(self), self._name, self._storage, self._time_stamp, self._user_data, self._data_arrays, self._set_arrays)

    def __str__(self):
        heading = "{}: {}".format(self.__class__.__name__, self._name)
        table = [['name', 'label', 'unit', 'shape', 'setpoint']]
        for name, array in self._data_arrays.items():
            table.append([name, array.label, array.unit, str(array.shape), str(array.is_setpoint)])
        for array in self._set_arrays:
            table.append([array.name, array.label, array.unit, str(array.shape), str(array.is_setpoint)])
        return heading + self._format_str(table)

    def add_array(self, array):
        """
        Args:
            array (DataArray): Array to be added to the experiment.

        Raises:
            ValueError: If an array with the same name has already been added.
            ValueError: If setpoints of the array do not match already added setpoints.
            SyntaxError: If array name is not a valid identifier.
        """

        self._verify_array_name(array.name)
        self._verify_set_points(array.set_arrays)
        self._data_arrays[array.name] = array
        setattr(self, array.name, array)
        self._default_array_name = self._default_array_name or array.name

    def add_data(self, index_or_slice, data):
        """ Update an underlying DataArray.

        Args:
            index_or_slice (int, tuple[int]): Setpoints, can be an int or tuple of integers.
            data (dict): Key is the name of the array and the dict value is the data.
        """

        for array_name, data_value in data.items():
            self._data_arrays[array_name][index_or_slice] = data_value

    def sync_from_storage(self):
        """ Not implemented yet. """
        raise NotImplementedError("sync_from_storage has not been implemented.")

    def save_to_storage(self):
        """ Not implemented yet. """
        raise NotImplementedError("save_to_storage has not been implemented.")

    def finalize(self):
        """ Not implemented yet. """
        raise NotImplementedError("finalize has not been implemented.")

    @property
    def storage(self):
        return self._storage

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def data_arrays(self):
        return self._data_arrays

    @property
    def time_stamp(self):
        return self._time_stamp

    @time_stamp.setter
    def time_stamp(self, time_stamp):
        self._time_stamp = time_stamp

    @property
    def user_data(self):
        return self._user_data

    @user_data.setter
    def user_data(self, user_data):
        self._user_data = user_data

    @property
    def default_array_name(self):
        return self._default_array_name

    @default_array_name.setter
    def default_array_name(self, default_array_name):
        self._default_array_name = default_array_name

    def _verify_set_points(self, set_arrays):
        self._set_arrays = self._set_arrays or set_arrays
        if self._set_arrays != set_arrays:
            raise ValueError('Set point arrays do not match.')

    def _verify_array_name(self, name):
        if not isinstance(name, str):
            raise ValueError("Array name has to be string, not {}".format(type(name)))
        if not name.isidentifier():
            raise SyntaxError("'{}' is an invalid name for an identifier.".format(name))
        if hasattr(self, name):
            raise ValueError("DataSet already contains an array with the name '{}'".format(name))

    def _add_data_arrays(self, data_arrays):
        if isinstance(data_arrays, collections.Sequence):
            for array in data_arrays:
                self._add_data_arrays(array)
        elif isinstance(data_arrays, DataArray):
            self.add_array(data_arrays)
        else:
            raise TypeError("'data_arrays' have to be of type 'DataArray', not {}".format(type(data_arrays)))

    def _add_set_arrays(self, set_arrays):
        if isinstance(set_arrays, collections.Sequence):
            self._set_arrays = set_arrays
        elif set_arrays is None:
            self._set_arrays = []
        else:
            self._set_arrays = [set_arrays]

    @staticmethod
    def _format_str(table):
        row_template = '\n  {info[0]:{lens[0]}} | {info[1]:{lens[1]}} | {info[2]:{lens[2]}} | {info[3]:{lens[3]}} | ' \
                       '{info[4]}'
        formatted_string = ''
        column_lengths = []
        for i in range(4):
            column_lengths.append(len(max(table, key=lambda t: len(t[i]))[i]))
        for row in table:
            formatted_string += row_template.format(info=row, lens=column_lengths)
        return formatted_string
