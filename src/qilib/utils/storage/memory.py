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
from typing import Any, Dict, Optional, Union

from qilib.utils.storage.interface import (NoDataAtKeyError,
                                           NodeAlreadyExistsError,
                                           StorageInterface, NodeDoesNotExistsError)
from qilib.utils.type_aliases import TagType


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
    def _retrieve_value_from_dict_by_tag(dictionary: Dict[str, Any], tag: TagType,
                                         field: Optional[Union[str, int]] = None) -> Any:
        if len(tag) == 0:
            if not isinstance(dictionary, StorageMemory.__Leaf):
                raise NoDataAtKeyError()
            if field is None:
                return dictionary.data
            else:
                if field in dictionary.data:
                    return dictionary.data[field]
                else:
                    raise NoDataAtKeyError(f'The field {field} does not exist.')

        tag_prefix: str = tag[0]
        if tag_prefix not in dictionary:
            raise NoDataAtKeyError(tag)
        return StorageMemory._retrieve_value_from_dict_by_tag(dictionary[tag_prefix], tag[1:], field)

    @staticmethod
    def _retrieve_nodes_from_dict_by_tag(dictionary: Dict[str, Any],
                                         tag: TagType, limit: int = 0) -> TagType:
        if len(tag) == 0:
            results = list(dictionary.keys())
            if limit > 0:
                results = results[:limit]
            return results
        tag_prefix = tag[0]
        if tag_prefix not in dictionary:
            raise NoDataAtKeyError(tag)
        if isinstance(dictionary[tag_prefix], StorageMemory.__Leaf):
            raise NoDataAtKeyError(tag)

        return StorageMemory._retrieve_nodes_from_dict_by_tag(dictionary[tag_prefix], tag[1:], limit=limit)

    @staticmethod
    def _store_value_to_dict_by_tag(dictionary: Dict[str, Any], tag: TagType, value: Any,
                                    field: Optional[Union[str, int]] = None) -> None:
        if len(tag) == 1:
            if tag[0] in dictionary:
                if isinstance(dictionary[tag[0]], StorageMemory.__Node):
                    raise NodeAlreadyExistsError()
            if field is None:
                dictionary[tag[0]] = StorageMemory.__Leaf(value)
            else:
                if tag[0] in dictionary:
                    dictionary[tag[0]].data[field] = value
                else:
                    raise NodeDoesNotExistsError(f'The Node {tag[0]} does not exist')
        else:
            if not tag[0] in dictionary:
                dictionary[tag[0]] = StorageMemory.__Node()
            elif isinstance(dictionary[tag[0]], StorageMemory.__Leaf):
                raise NodeAlreadyExistsError(f'Cannot store or replace data, because \'{tag[0]}\' is already a node')

            StorageMemory._store_value_to_dict_by_tag(dictionary[tag[0]], tag[1:], value, field)

    def load_data(self, tag: TagType) -> Any:
        if not isinstance(tag, list):
            raise TypeError()
        return self._unserialize(StorageMemory._retrieve_value_from_dict_by_tag(self._data, tag))

    def save_data(self, data: Any, tag: TagType) -> None:
        self._validate_tag(tag)
        StorageMemory._store_value_to_dict_by_tag(self._data, tag, self._serialize(data))

    def get_latest_subtag(self, tag: TagType) -> Optional[TagType]:
        child_tags: TagType = self.list_data_subtags(tag)
        if len(child_tags) == 0:
            return None
        child_tags = sorted(child_tags)
        return tag + [child_tags[-1]]

    def list_data_subtags(self, tag: TagType, limit: int = 0) -> TagType:
        try:
            tags: TagType = self._retrieve_nodes_from_dict_by_tag(self._data, tag, limit=limit)
        except NoDataAtKeyError:
            return []
        return list(tags)

    def search(self, query: str) -> Any:
        raise NotImplementedError()

    def tag_in_storage(self, tag: TagType) -> bool:
        tmp_data = self._data
        for partial_tag in tag:
            if partial_tag in tmp_data:
                tmp_data = tmp_data[partial_tag]
            else:
                return False
        return True

    def load_individual_data(self, tag: TagType, field: Union[str, int]) -> Any:
        """ Retrieve the value of an individual field at the given tag

        Args:
            tag: The tag
            field: Name of the field to load

        Returns:
            Value of the field

        """
        self._validate_tag(tag)
        self._validate_field(field)
        return self._unserialize(StorageMemory._retrieve_value_from_dict_by_tag(self._data, tag, field))

    def update_individual_data(self, data: Any, tag: TagType, field: Union[str, int]) -> None:
        """ Update the value of an individual field at the given tag.
        If the field does not already exist, then it will be created.

         Args:
             data: The data to be used for updating the field
             tag: The tag
             field: Name of the field to update

         """
        self._validate_tag(tag)
        self._validate_field(field)
        StorageMemory._store_value_to_dict_by_tag(self._data, tag, self._serialize(data), field)
