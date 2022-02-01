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

from operator import itemgetter
from typing import Any, Optional, Union

import numpy as np
from bson import ObjectId
from bson.codec_options import TypeCodec, CodecOptions, TypeRegistry
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

from qilib.data_set.mongo_data_set_io import MongoDataSetIO, NumpyKeys
from qilib.utils.serialization import Serializer, serializer as _serializer
from qilib.utils.storage.interface import (NoDataAtKeyError,
                                           NodeAlreadyExistsError,
                                           StorageInterface,
                                           ConnectionTimeoutError)
from qilib.utils.type_aliases import TagType


class NumpyArrayCodec(TypeCodec):  # type: ignore

    @property
    def python_type(self) -> Any:
        return np.ndarray

    def transform_python(self, value: Any) -> Any:
        return MongoDataSetIO.encode_numpy_array(value)

    @property
    def bson_type(self) -> Any:
        return dict

    def transform_bson(self, value: Any) -> Any:
        if NumpyKeys.OBJECT in value and value[NumpyKeys.OBJECT] == np.array.__name__:
            return MongoDataSetIO.decode_numpy_array(value)

        return value


qi_tag = '_tag'


class StorageMongoDb(StorageInterface):
    """Reference implementation of StorageInterface with an mongodb backend

    Implements a storage tree in a MongoDB collection
    Performance Note: Creating index(es) in mongodb will help improve query performance
    eg: An index on (parent, tag) will improve the performance of queries in _retrieve_nodes_by_tag
    """

    def __init__(self, name: str, host: str = 'localhost', port: int = 27017, database: str = '',
                 serializer: Union[Serializer, None] = None, connection_timeout: float = 30000) -> None:
        """MongoDB implementation of storage class

        See also: `StorageInterface`

        Args:
            name: Symbolic name for the storage instance.
            host: MongoDB host
            port: MongoDB port
            database: The database to use, if empty the name of the storage is used
            connection_timeout: How long to try to connect to database before raising an error in milliseconds
        Raises:
            StorageTimeoutError: If connection to database has not been established before connection_timeout is reached
        """
        super().__init__(name)

        type_registry = TypeRegistry([NumpyArrayCodec()])
        codec_options = CodecOptions(type_registry=type_registry)
        self._client = MongoClient(host, port, serverSelectionTimeoutMS=connection_timeout)
        self._check_server_connection(connection_timeout)
        self._db = self._client.get_database(database or name, codec_options=codec_options)
        self._collection = self._db.get_collection('storage')

        if serializer is None:
            serializer = _serializer
        self._serialize = serializer.encode_data
        self._unserialize = serializer.decode_data

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} at 0x{id(self):x}: name {self._db.name}>'

    def __str__(self) -> str:
        return f'<{type(self).__name__}: name {self._db.name}>'

    def _check_server_connection(self, timeout: float) -> None:
        """ Check if connection has been established to database server."""
        try:
            self._client.server_info()
        except ServerSelectionTimeoutError as e:
            raise ConnectionTimeoutError(f'Failed to connect to Mongo database within {timeout} milliseconds') from e

    def _retrieve_nodes_by_tag(self, tag: TagType, parent: ObjectId, document_limit: int = 0) -> TagType:
        """Traverse the tree and list the children of a given tag

        Args:
            tag: The node tag
            parent: The ObjectID of the node's parent
            document_limit: Maximum number of documents to return. If set to zero there is no limit

        Returns:
            A list of names of the children
        """
        raise

    def _retrieve_value_by_tag(self, tag: TagType, field: Optional[Union[str, int]] = None) -> Any:
        """Traverse the tree and retrieves the value / field value of a given leaf tag
        If the field is specified, it returns the value of the field instead of tag value
        If the specified field does not exist, it will raise a NoDataAtKeyError

        Args:
            tag: The leaf tag
            parent: The ObjectID of the leaf's parent
            field: The field to be retrieved. Default value is none.

        Returns:
            Data held by the leaf. If field is provided, returns the value of the
            field stored in the leaf

        Raises:
            NoDataAtKeyError: If a tag in Tag list does not exist
            or if the field does not exist
        """

        if field is None:
            doc = self._collection.find_one({qi_tag: tag})
        else:
            doc = self._collection.find_one({qi_tag: tag}, {f'value.{field}': 1})

        if doc is None:
            raise NoDataAtKeyError(f'Tag "{tag[0]}" cannot be found')
        elif 'value' not in doc:
            raise NoDataAtKeyError(f'Tag "{tag[0]}" is not a leaf')
        else:
            if field is None:
                return doc['value']
            elif field in doc['value']:
                return doc['value'][field]
            else:
                raise NoDataAtKeyError(f'The field "{field}" does not exists')

    def _store_value_by_tag(self, tag: TagType, data: Any,
                            field: Optional[Union[str, int]] = None) -> None:
        """ Store a value at a given tag. In case a field is specified, function will update the value of the
        field with data. If the field does not already exists, the field will be created

        Args:
            tag: The tag
            data: Data to store
            field: (encoded?) Field to be updated. Default value is None

        Raises:
              NodeAlreadyExistsError: If a tag in Tag List is an unexpected node/leaf
              NoDataAtKeyError:  If a tag in Tag List does not exist
        """

        doc = self._collection.find_one({qi_tag: tag})
        if doc:
            # update
            if field is None:
                self._collection.update_one({qi_tag: tag}, {'$set': {'value': data}})
            else:
                self._collection.update_one({qi_tag: tag}, {'$set': {'value.'+str(field): data}})

        else:
            self._collection.insert_one({qi_tag: tag, 'value': data})

    def load_data(self, tag: TagType) -> Any:

        tag = self._validate_tag(tag)

        return self._unserialize(self._decode_data(self._retrieve_value_by_tag(tag)))

    @staticmethod
    def _validate_tag(tag: TagType) -> None:
        """ Assert that tag is a list of strings."""
        if isinstance(tag, str):
            return tag

        if not isinstance(tag, list) or not all(isinstance(item, str) for item in tag):
            raise TypeError(f'Tag {tag} should be a list of strings')
        if np.any(['.' in t for t in tag]):
            raise Exception('. not allowed in tag components')
        return '.'.join(tag)

    @staticmethod
    def _unpack_tag(tag: str) -> TagType:
        return tag.split('.')

    def save_data(self, data: Any, tag: TagType) -> None:
        tag = self._validate_tag(tag)
        self._store_value_by_tag(tag, self._encode_data(self._serialize(data)))

    def load_individual_data(self, tag: TagType, field: Union[str, int]) -> Any:
        """ Retrieve an individual field value at a given tag

            Args:
                tag: The tag
                field: Name of the individual field to be retrieved

            Raises:
                NoDataAtKeyError if the tag is empty

            Returns:
                Value of the field
        """

        self._validate_tag(tag)
        self._validate_field(field)

        if len(tag) == 0:
            raise NoDataAtKeyError('Tag cannot be empty')

        return self._unserialize(self._decode_data(
            self._retrieve_value_by_tag(tag,  self._encode_field(self._serialize(field)))))

    def update_individual_data(self, data: Any, tag: TagType, field: Union[str, int]) -> None:
        """ Update an individual field at a given tag with the given data.
        If the field does not exist, it will be created.

            Args:
                data: Data to update
                tag: The tag
                field: Name of the individual field to updated

        """

        self._validate_tag(tag)
        self._validate_field(field)
        self._store_value_by_tag(tag, self._encode_data(self._serialize(data)),
                                 self._encode_field(self._serialize(field)))

    def get_latest_subtag(self, tag: TagType) -> Optional[TagType]:
        """ Get the latest subtag

        Args:
            tag: Tag to search from
        Returns:
            Latest subtag found among subtags or None if there are no subtags
        """
        child_tags = self.list_data_subtags(tag, limit=1)
        if len(child_tags) == 0:
            return None

        return self._unpack_tag(tag) + [child_tags[0]]

    def list_data_subtags(self, tag: TagType, limit: int = 0) -> TagType:
        """ List subtags for the given tag. The number of subtags listed is based on the limit parameter (0 for
        listing all subtags)

        Args:
            tag: Tag to search from
            limit: Maximum number of subtags to return. If set to zero there is no limit
        Returns:
            List of subtags found, sorted in descending order
        """
        try:
            vtag = self._validate_tag(tag)
            xtag = {'$regex': f'^{vtag}\..*'}
            c = self._collection.find({qi_tag: xtag}, {'value': 0},     limit=document_limit,  sort=[('tag', -1)])
            tags = list(map(itemgetter(qi_tag), c))

        except NoDataAtKeyError:
            tags = []

        return tags

    def search(self, query: str) -> Any:
        raise NotImplementedError()

    def tag_in_storage(self, tag: TagType) -> bool:
        doc = self._collection.find_one({qi_tag: tag}, {'value': 0})
        if doc is None:
            return False
        else:
            return True

    @staticmethod
    def _encode_field(field: Union[int, str]) -> str:
        """Encodes a field value. A field can be an individual key in a structure like dict which is to be
        read or updated

        Args:
            field: An integer or a string

        Returns:
            Encoded value for the field in string format

        """

        return StorageMongoDb._encode_int(field) if isinstance(field, int) \
            else field

    @staticmethod
    def _encode_int(value: int) -> str:
        """Encodes an int value to a string

        Args:
            value: An integer

        Returns:
            An encoded integer
        """

        return f'_integer[{value}]'

    @staticmethod
    def _is_encoded_int(value: str) -> bool:
        """Checks if the given value is a properly encoded integer

        Args:
            value: The encoded value

        Returns:
            True if an integer can be decoded, False otherwise
        """

        if not value.startswith('_integer[') or not value.endswith(']'):
            return False

        value = value[len('_integer['):-1]
        return value[1:].isdigit() if value.startswith('-') else value.isdigit()

    @staticmethod
    def _decode_int(value: str) -> int:
        """Parses an integer from the encoded value

        Args:
            value: The encoded integer

        Returns:
            The decoded integer
        """

        if not StorageMongoDb._is_encoded_int(value):
            raise ValueError()

        return int(value[len('_integer['):-1])

    @staticmethod
    def _encode_data(data: Any) -> Any:
        """Recursively encode the data and apply dot replacement and integer encoding on the keys

        Args:
            data: The data
        Returns:
            The transformed data
        """

        if isinstance(data, dict):
            return {
                (StorageMongoDb._encode_int(key) if isinstance(key, int) else key): StorageMongoDb._encode_data(value)
                for key, value in data.items()
            }

        elif isinstance(data, list):
            return [StorageMongoDb._encode_data(item) for item in data]

        return data

    @staticmethod
    def _decode_data(data: Any) -> Any:
        """Recursively decode the data and apply dot replacement and integer decoding on the keys

        Args:
            data: The data
        Returns:
            The transformed data
        """

        if isinstance(data, dict):
            return {
                StorageMongoDb._decode_int(key)
                if StorageMongoDb._is_encoded_int(key) else key: StorageMongoDb._decode_data(value)
                for key, value in data.items()
            }

        elif isinstance(data, list):
            return [StorageMongoDb._decode_data(item) for item in data]

        return data


"""
Improvements:
    
    - Much less code
    - No . encoding any more
    - More efficient retrieval of subtags (no tree traversal)
    - Tags can be entered in compact notation 'x.y.z'
    - Multiple subfield retrieval?
"""

# %%
if __name__ == '__main__':
    s = StorageMongoDb('test6')

    self = s

    tag = 'multi'
    for ii in range(4):
        s.save_data(ii, tag)
    assert s.load_data(tag) == 3

    assert s.tag_in_storage(tag)

    #parent = self._collection.insert_one({'test': '.', 'tag': 'tag'}).inserted_id
    #parent = self._collection.insert_one({'test': '.', '\\u002e': 'tag'}).inserted_id
    #parent = self._collection.insert_one({'test': '.', '.': 'dot tag'}).inserted_id

    s.save_data({'one': np.array([1, 2, 4.])}, ['numpy'])
    s.save_data({0: 'integer'}, ['0'])

    s.list_data_subtags([])
    s.save_data({'dot.field.dot': '.'}, ['dot_in_field'])
    s.save_data({'one': 1, 'list': [1, 'a', 'c'], 'dict': {'a+b': 'c'}}, ['a', 'b', 'c'])

    tag = 'a.b.c'
    only_field = s.load_individual_data(tag, field='list')

    s.update_individual_data([], tag, field='list')
    only_field = s.load_individual_data(tag, field='list')

    s.save_data({'one': 1}, 'st.x')
    s.save_data({'no please': 2}, 'no.st.y')
    for t in ['st.x', 'st.y.sub', 'st.z']:
        s.save_data({'t': t}, t)
    s.save_data({'one': np.array([1, 2, 4.])}, 'st.z')
    tag = ['st', 'x']
    doc = s.load_data(tag)
    print(f'got data for {tag}: {doc}')

    print(s.list_data_subtags('st'))
    print(s.list_data_subtags('st.y'))

    s.get_latest_subtag('st')

    tag = 'numpy'
    tag = self._validate_tag(tag)
# %%
if __name__ == '__main__':
    tag = 'st.y'
    document_limit = 100
    xtag = '/^ma/'
    vtag = self._validate_tag(tag)
    xtag = {'$regex': f'^{vtag}\..*'}
    c = self._collection.find({qi_tag: xtag}, {'value': 0},     limit=document_limit,       sort=[('tag', -1)])
    l = list(map(itemgetter(qi_tag), c))
    print(l)

    # TODO: index based on qi_tag
    # TODO: s.list_data_subtags([]) (for empty entries...)
    # TODO: s.list_data_subtags([]) -> returns everyting, but we only want to have the things with no dots...!?
    # TODO: fields are both encoded and serialized. do we really need the serialization?
    # TODO: bulk test, database conversion
    
# %%%
    # if len(tag) == 0:
    #             return list(map(itemgetter('tag'),
    #                             self._collection.find({'parent': parent, 'tag': {'$exists': True}},
    #                                                   {'value': 0},
    #                                                   limit=document_limit,
    #                                                   sort=[('tag', -1)])))
