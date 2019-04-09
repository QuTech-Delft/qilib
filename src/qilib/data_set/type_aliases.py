from typing import Tuple, List, Union, Sequence

from qilib.data_set import DataArray

DataArrays = Union[List[DataArray], Tuple[DataArray, ...], DataArray]

PJSValueTypes = Union[None, bool, int, float, complex, str, bytes]
PJSContainers = Sequence[PJSValueTypes]
PJSValues = Union[PJSContainers, PJSValueTypes]
    # __serializable_container_types = (list, tuple, np.ndarray)
    # __serializable_value_types = (type(None), bool, int, float, complex, str, bytes)