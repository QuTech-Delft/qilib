import numpy as np


class DataArray:
    """ A container for measurement data and setpoint arrays.

    All attributes/methods not defined in the DataArray are delegated to an underlying numpy array.

    The DataArray makes sure that the dimensions of the set arrays are correct with regards to the data array and vice
    versa (e.g., trying to set a 1D array of 10 elements as the data array with a 1D setpoint array of 8 elements will
    raise an error).
    """

    def __init__(self, name, label, unit='', is_setpoint=False, preset_data=None, set_arrays=None, shape=None):
        """
        Args:
            name (str):  Name for the data array
            label (str): Label, e.g. x-axis if it is a setpoint.
            unit (str): Unit for the measurement, or setpoint data.
            is_setpoint (bool): If the DataArray is a setpoint.
            preset_data (numpy.ndarray): Initialize the DataArray with predefined data. Note that a copy of the numpy
                array is stored in data, not the actual array.
            set_arrays (DataArray[]): a list of setpoint arrays.
            shape (tuple): Initialize with a shape rather than predefined data.
        """

        self._name = name
        self._label = label
        self._unit = unit
        self._is_setpoint = is_setpoint
        if preset_data is not None:
            self._data = np.array(preset_data).copy()
        elif shape is not None:
            self._data = np.ndarray(shape) * np.NAN
        else:
            raise TypeError("Required arguments 'shape' or 'preset_data' not found")
        self._set_arrays = set_arrays if set_arrays is not None else []
        if len(self._set_arrays) > 0:
            self._verify_array_dimensions()

    def __add__(self, other):
        return self._data.__add__(other)

    def __mul__(self, other):
        return self._data.__mul__(other)

    def __matmul__(self, other):
        return self._data.__matmul__(other)

    def __pow__(self, *args, **kwargs):
        return self._data.__pow__(*args, **kwargs)

    def __sub__(self, other):
        return self._data.__sub__(other)

    def __mod__(self, other):
        return self._data.__mod__(other)

    def __floordiv__(self, other):
        return self._data.__floordiv__(other)

    def __lshift__(self, other):
        return self._data.__lshift__(other)

    def __rshift__(self, other):
        return self._data.__rshift__(other)

    def __and__(self, other):
        return self._data.__and__(other)

    def __or__(self, other):
        return self._data.__or__(other)

    def __xor__(self, other):
        return self._data.__xor__(other)

    def __truediv__(self, other):
        return self._data.__truediv__(other)

    def __getattr__(self, name):
        if hasattr(np.ndarray, name):
            return getattr(self._data, name)
        raise AttributeError("DataArray has no attribute '{}'".format(name))

    def __dir__(self):
        data_dir = dir(self._data)
        data_array_dir = super(DataArray, self).__dir__()
        return set(data_dir + data_array_dir)

    def __str__(self):
        array_names = [array.name for array in self.set_arrays] if self.set_arrays is not None else []
        print_string = "{} {}: {}\ndata: {}\nset_arrays:{}".format(self.__class__.__name__, self.shape, self.name,
                                                                   self._data, array_names)
        return print_string

    def __repr__(self):
        return "DataArray(id=%r, name=%r, label=%r, unit=%r, is_setpoint=%r, data=%r, set_arrays=%r)" % (
            id(self), self._name, self._label, self._unit, self._is_setpoint, self._data, self._set_arrays)

    def __getitem__(self, index):
        return self._data[index]

    def __setitem__(self, index, data):
        self._data[index] = data

    def _verify_array_dimensions(self):
        shapes = [array.shape for array in self._set_arrays]
        shapes.sort(key=lambda s: len(s))
        if self.is_setpoint:
            shapes.append(self._data.shape)
        else:
            if shapes[-1] != self.shape:
                raise ValueError("Dimensions of 'set_arrays' and 'data' do not match.")
        DataArray._check_dimensions(shapes)

    @staticmethod
    def _check_dimensions(shapes):
        for i in range(len(shapes)):
            dim = shapes.pop(0)
            if not all(shape[i] == dim[i] for shape in shapes):
                raise ValueError("Dimensions of 'set_arrays' do not match.")

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def unit(self):
        return self._unit

    @unit.setter
    def unit(self, unit):
        self._unit = unit

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, label):
        self._label = label

    @property
    def is_setpoint(self):
        return self._is_setpoint

    @property
    def set_arrays(self):
        return self._set_arrays
