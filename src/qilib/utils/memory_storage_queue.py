""" Provides the MemoryStorageQueue."""
from queue import Queue
from typing import Union, List, Dict, Any

from qilib.data_set import DataArray


class MemoryStorageQueue(Queue): # type: ignore
    """ A simple fifo storage queue shared between the MemoryDataSetIO Reader and Writer."""

    DATA = 'data'
    META_DATA = 'meta_data'
    ARRAY = 'array'

    def add_data(self, index_or_slice: Union[int, List[int]], data: Dict[str, Any]) -> None:
        self.put((self.DATA, (index_or_slice, data)))

    def add_meta_data(self, *meta_data: Any) -> None:
        self.put((self.META_DATA, meta_data))

    def add_array(self, array: DataArray) -> None:
        self.put((self.ARRAY, array))
