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
from typing import cast, Optional, Tuple, List, Union, Any, Set, Dict

import numpy
import numpy as np

from qilib.utils.type_aliases import NumpyNdarrayType


class DataArray:
    """ A container for measurement data and setpoint arrays.

    All attributes/methods not defined in the DataArray are delegated to an underlying numpy array.

    The DataArray makes sure that the dimensions of the set arrays are correct with regards to the data array and vice
    versa (e.g., trying to set a 1D array of 10 elements as the data array with a 1D setpoint array of 8 elements will
    raise an error).
    """

    def __init__(self, name: str, label: str, unit: str = '', is_setpoint: bool = False,
                 preset_data: Optional[NumpyNdarrayType] = None,
                 set_arrays: Optional[Union[List['DataArray'], Tuple['DataArray', ...]]] = None,
                 shape: Optional[Tuple[int, ...]] = None) -> None:
        """
        Args:
            name:  Name for the data array
            label: Label, e.g. x-axis if it is a setpoint.
            unit: Unit for the measurement, or setpoint data.
            is_setpoint: If the DataArray is a setpoint.
            preset_data: Initialize the DataArray with predefined data. Note that a copy of the numpy
                array is stored in data, not the actual array.
            set_arrays: a list of setpoint arrays.
            shape: Initialize with a shape rather than predefined data.
        """

        self._name: str = name
        self._label: str = label
        self._unit: str = unit
        self._is_setpoint: bool = is_setpoint
        self._data: NumpyNdarrayType
        if preset_data is not None:
            self._data = np.array(preset_data).copy()
        elif shape is not None:
            self._data = np.ndarray(shape) * np.NAN
        else:
            raise TypeError("Required arguments 'shape' or 'preset_data' not found")
        self._set_arrays = set_arrays if set_arrays is not None else []
        if len(self._set_arrays) > 0:
            self._verify_array_dimensions()

    def __add__(self, other: Union[float, int, 'DataArray', NumpyNdarrayType]) -> NumpyNdarrayType:
        return self._data.__add__(other)

    def __mul__(self, other: Union[float, int, 'DataArray', NumpyNdarrayType]) -> NumpyNdarrayType:
        return self._data.__mul__(other)

    def __matmul__(self, other: Union[List[Union[float, int]], 'DataArray', NumpyNdarrayType]) -> numpy.int64:
        return cast(numpy.int64, self._data.__matmul__(other))

    def __pow__(self, other: Union[float, int]) -> NumpyNdarrayType:
        return self._data.__pow__(other)

    def __sub__(self, other: Union[float, int, 'DataArray', NumpyNdarrayType]) -> NumpyNdarrayType:
        return self._data.__sub__(other)

    def __mod__(self, other: Union[float, int, 'DataArray', NumpyNdarrayType]) -> NumpyNdarrayType:
        return self._data.__mod__(other)

    def __floordiv__(self, other: Union[float, int, 'DataArray', NumpyNdarrayType]) -> NumpyNdarrayType:
        return self._data.__floordiv__(other)

    def __lshift__(self, other: Union[int, 'DataArray', NumpyNdarrayType]) -> NumpyNdarrayType:
        return self._data.__lshift__(other)

    def __rshift__(self, other: Union[int, 'DataArray', NumpyNdarrayType]) -> NumpyNdarrayType:
        return self._data.__rshift__(other)

    def __and__(self, other: Union[bool, int, 'DataArray', NumpyNdarrayType]) -> NumpyNdarrayType:
        return self._data.__and__(other)

    def __or__(self, other: Union[bool, int, 'DataArray', NumpyNdarrayType]) -> NumpyNdarrayType:
        return self._data.__or__(other)

    def __xor__(self, other: Union[bool, int, 'DataArray', NumpyNdarrayType]) -> NumpyNdarrayType:
        return self._data.__xor__(other)

    def __truediv__(self, other: Union[float, int, 'DataArray', NumpyNdarrayType]) -> NumpyNdarrayType:
        return self._data.__truediv__(other)

    def __getattr__(self, name: str) -> Any:
        if hasattr(np.ndarray, name):
            return getattr(self._data, name)
        raise AttributeError("DataArray has no attribute '{}'".format(name))

    def __dir__(self) -> Set[str]:
        data_dir = dir(self._data)
        data_array_dir = list(super(DataArray, self).__dir__())
        return set(data_dir + data_array_dir)

    def __str__(self) -> str:
        array_names = [array.name for array in self.set_arrays] if self.set_arrays is not None else []
        print_string = "{} {}: {}\ndata: {}\nset_arrays:{}".format(self.__class__.__name__, self.shape, self.name,
                                                                   self._data, array_names)
        return print_string

    def __repr__(self) -> str:
        return "DataArray(id=%r, name=%r, label=%r, unit=%r, is_setpoint=%r, data=%r, set_arrays=%r)" % (
            id(self), self._name, self._label, self._unit, self._is_setpoint, self._data, self._set_arrays)

    def __getitem__(self, index: Union[Tuple[int, ...], int]) -> Any:
        return self._data[index]

    def __setitem__(self, index: Union[Tuple[int, ...], int], data: Any) -> None:
        self._data[index] = data

    def __copy__(self) -> 'DataArray':
        data_array_copy = type(self)(name=self._name, label=self._label, shape=self.shape)
        data_array_copy.__dict__.update(self.__dict__)
        return data_array_copy

    def __deepcopy__(self, memo: Dict[int, Any]) -> 'DataArray':
        data_array_copy = type(self)(name=self._name, label=self._label, shape=self.shape)
        data_array_copy.__dict__.update(self.__dict__)
        data_array_copy._data = deepcopy(self._data, memo)
        data_array_copy._set_arrays = deepcopy(self._set_arrays, memo)

        return data_array_copy

    def __len__(self) -> int:
        return len(self._data)

    def _verify_array_dimensions(self) -> None:
        shapes = [array.shape for array in self._set_arrays]
        shapes.sort(key=lambda s: len(s))
        if self.is_setpoint:
            shapes.append(self._data.shape)
        else:
            if shapes[-1] != self.shape:
                raise ValueError("Dimensions of 'set_arrays' and 'data' do not match.")
        DataArray._check_dimensions(shapes)

    @staticmethod
    def _check_dimensions(shapes: List[Tuple[int]]) -> None:
        for i in range(len(shapes)):
            dim = shapes.pop(0)
            if not all(shape[i] == dim[i] for shape in shapes):
                raise ValueError("Dimensions of 'set_arrays' do not match.")

    @property
    def data(self) -> NumpyNdarrayType:
        return self._data

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        self._name = name

    @property
    def unit(self) -> str:
        return self._unit

    @unit.setter
    def unit(self, unit: str) -> None:
        self._unit = unit

    @property
    def label(self) -> str:
        return self._label

    @label.setter
    def label(self, label: str) -> None:
        self._label = label

    @property
    def is_setpoint(self) -> bool:
        return self._is_setpoint

    @property
    def set_arrays(self) -> Union[List['DataArray'], Tuple['DataArray', ...]]:
        return self._set_arrays
