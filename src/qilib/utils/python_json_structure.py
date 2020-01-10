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
from typing import Dict, Any, Optional, cast

import numpy as np

from qilib.utils.type_aliases import PJSValues


class PythonJsonStructure(dict):  # type: ignore
    __serializable_key_types = (str, int)
    __serializable_python_types = (bool, int, float, complex, str, bytes)
    __serializable_numpy_types = (np.float32, np.float64, np.int32, np.int64, np.cfloat)
    __serializable_value_types = (*__serializable_python_types, *__serializable_numpy_types)

    def __init__(self, *args: Dict[str, PJSValues], **kwargs: Any) -> None:
        """ A python container which can hold data objects and can be serialized
            into JSON. Currently the following data types can be added to the
            container object: bool, bytes, int, float, list, tuple, dict
            PythonJsonStructure and numpy arrays. The PythonJsonStructure is a
            dictionary with similar calling methods, but with some
            limitations/restrictions.

        Args:
            *args: A serializable dictionary with key value pair data.
            **kwargs: Arbitrary keyword arguments with serializable values.
        """
        super().__init__()
        self.update(*args, **kwargs)

    def __setitem__(self, key: str, value: PJSValues) -> None:
        """ Appends or changes an item of the container.

        Args:
            key: The key of the container item.
            value: The value of the updated item.
        """

        value = self.__validate_key_value_pair(key, value)
        super().__setitem__(key, value)

    def update(self, *args: Any, **kwargs: Any) -> None:
        """ Update the PythonJsonStructure with the key/value pairs from other
            dict/PythonJsonStructure, overwriting existing keys."""
        if args:
            args_data = args[0]
            for key, value in args_data.items():
                self[key] = value
        if kwargs:
            kwargs_items = kwargs.items()
            for key, value in kwargs_items:
                self[key] = value

    def setdefault(self, key: str, default: Optional[PJSValues] = None) -> PJSValues:
        """ If key is in the dictionary, return its value. If not, insert key
            with a value of default and return default.

        Args:
            key: The key of the container item.
            default: The default value of the updated item.
        """
        default = self.__validate_key_value_pair(key, default)
        return cast(PJSValues, super().setdefault(key, default))

    def __validate_key_value_pair(self, key: str, value: Optional[PJSValues] = None) -> PJSValues:
        if isinstance(value, dict):
            value = PythonJsonStructure(value)
        PythonJsonStructure.__assert_correct_key_type(key)
        self.__check_serializability(value)
        return value

    def __check_serializability(self, data: Any) -> None:
        if isinstance(data, (list, tuple)):
            for item in data:
                self.__check_serializability(item)

        elif isinstance(data, dict):
            for key, item in data.items():
                PythonJsonStructure.__assert_correct_key_type(key)
                self.__check_serializability(item)

        elif data is not None:
            PythonJsonStructure.__is_valid_type(data)

    @staticmethod
    def __assert_correct_key_type(key: Any) -> None:
        if not isinstance(key, PythonJsonStructure.__serializable_key_types):
            raise TypeError('Invalid key! (key={})'.format(key))

    @staticmethod
    def __is_valid_type(data: Any) -> None:
        if isinstance(data, np.ndarray):
            valid = data.dtype in PythonJsonStructure.__serializable_numpy_types
            data_type = data.dtype
        else:
            valid = any([isinstance(data, type) for type in PythonJsonStructure.__serializable_value_types])
            data_type = type(data)
        if not valid:
            raise TypeError('Data is not serializable ({})!'.format(data_type))
