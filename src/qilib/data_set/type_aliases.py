from typing import Tuple, List, Union, Dict, Any

from qilib.data_set.data_array import DataArray

DataArrays = Union[List[DataArray], Tuple[DataArray, ...], DataArray]
EncodedNumpyArray = Dict[str, Union[str, Dict[str, Union[str, List[Any], bytes]]]]
