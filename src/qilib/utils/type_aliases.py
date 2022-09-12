from typing import Any, Dict, List, Sequence, Union
import numpy.typing as npt

PJSValueTypes = Union[None, bool, int, float, complex, str, bytes]
PJSContainers = Sequence[PJSValueTypes]
PJSValues = Union[PJSContainers, PJSValueTypes]
TagType = List[str]
EncodedNumpyArray = Dict[str, Union[str, Dict[str, Union[str, List[Any], bytes]]]]
# type alias for numpy.ndarray
NumpyNdarrayType = npt.NDArray[Any]


class NumpyKeys:
    """The custom values types for encoding and decoding numpy arrays."""
    OBJECT: str = '__object__'
    CONTENT: str = '__content__'
    DATA_TYPE: str = '__data_type__'
    SHAPE: str = '__shape__'
    ARRAY: str = '__ndarray__'
