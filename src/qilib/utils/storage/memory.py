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
from typing import Any, Dict, List, Optional

from qilib.utils.storage.interface import (NoDataAtKeyError,
                                           NodeAlreadyExistsError,
                                           StorageInterface)


class StorageMemory(StorageInterface):
    """ Reference implementation of StorageInterface with in-memory backend.

    Implements a storage tree as an in-memory dictionary.
    """

    class __Leaf:
        def __init__(self, data: Any) -> None:
            self.data: Any = data

    class __Node(Dict[str, Any]):
        pass

    def __init__(self, name: str) -> None:
        """ In memory implementation of storage class.

        See also: `StorageInterface`

        """
        super().__init__(name)
        self._data: Dict[str, Any] = {}

    @staticmethod
    def _retrieve_value_from_dict_by_tag(dictionary: Dict[str, Any],
                                         tag: List[str]) -> Any:
        if len(tag) == 0:
            if not isinstance(dictionary, StorageMemory.__Leaf):
                raise NoDataAtKeyError()
            return dictionary.data
        tag_prefix: str = tag[0]
        if tag_prefix not in dictionary:
            raise NoDataAtKeyError(tag)
        return StorageMemory._retrieve_value_from_dict_by_tag(dictionary[tag_prefix], tag[1:])

    @staticmethod
    def _retrieve_nodes_from_dict_by_tag(dictionary: Dict[str, Any],
                                         tag: List[str]) -> List[str]:
        if len(tag) == 0:
            return list(dictionary.keys())
        tag_prefix = tag[0]
        if tag_prefix not in dictionary:
            raise NoDataAtKeyError(tag)
        if isinstance(dictionary[tag_prefix], StorageMemory.__Leaf):
            raise NoDataAtKeyError(tag)

        return StorageMemory._retrieve_nodes_from_dict_by_tag(dictionary[tag_prefix], tag[1:])

    @staticmethod
    def _store_value_to_dict_by_tag(dictionary: Dict[str, Any], tag: List[str], value: Any) -> None:
        if len(tag) == 1:
            if tag[0] in dictionary:
                if isinstance(dictionary[tag[0]], StorageMemory.__Node):
                    raise NodeAlreadyExistsError()
            dictionary[tag[0]] = StorageMemory.__Leaf(value)
        else:
            if not tag[0] in dictionary:
                dictionary[tag[0]] = StorageMemory.__Node()
            elif isinstance(dictionary[tag[0]], StorageMemory.__Leaf):
                raise NodeAlreadyExistsError(f'Cannot store or replace data, because \'{tag[0]}\' is already a node')

            StorageMemory._store_value_to_dict_by_tag(dictionary[tag[0]], tag[1:], value)

    def load_data(self, tag: List[str]) -> Any:
        if not isinstance(tag, list):
            raise TypeError()
        return self._unserialize(StorageMemory._retrieve_value_from_dict_by_tag(self._data, tag))

    def save_data(self, data: Any, tag: List[str]) -> None:
        StorageMemory._store_value_to_dict_by_tag(self._data, tag, self._serialize(data))

    def get_latest_subtag(self, tag: List[str]) -> Optional[List[str]]:
        child_tags: List[str] = self.list_data_subtags(tag)
        if len(child_tags) == 0:
            return None
        child_tags = sorted(child_tags)
        return tag + [child_tags[-1]]

    def list_data_subtags(self, tag: List[str]) -> List[str]:
        try:
            tags: List[str] = self._retrieve_nodes_from_dict_by_tag(self._data, tag)
        except NoDataAtKeyError:
            return []
        return list(tags)

    def search(self, query: str) -> Any:
        raise NotImplementedError()

    def tag_in_storage(self, tag: List[str]) -> bool:
        tmp_data = self._data
        for partial_tag in tag:
            if partial_tag in tmp_data:
                tmp_data = tmp_data[partial_tag]
            else:
                return False
        return True

