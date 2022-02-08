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

import re
from operator import itemgetter
from typing import Any, Optional, Union, List, Dict, Tuple
import re

import numpy as np
from bson import ObjectId
from bson.codec_options import TypeCodec, CodecOptions, TypeRegistry
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
import numpy.typing as npt
import base64

from qilib.data_set.mongo_data_set_io import MongoDataSetIO, NumpyKeys
from qilib.utils.serialization import Serializer, serializer as _serializer
from qilib.utils.storage.interface import (NoDataAtKeyError,
                                           StorageInterface,
                                           ConnectionTimeoutError)
TagType = Union[str, List[str]]


numpy_ndarray_type = npt.NDArray[Any]


def encode_numpy_array(
        array: numpy_ndarray_type) -> Union[float, Dict[str, Any]]:
    """ Encode numpy array to store in database.

    Numpy scalars of floating point type are cast to Python float values.

    Args:
        array: Numpy array to encode.

    Returns:
        The encoded array.

    """
    if isinstance(array, (np.float32, np.float64)):
        return float(array)
    return {
        NumpyKeys.OBJECT: np.array.__name__,
        NumpyKeys.CONTENT: {
            NumpyKeys.ARRAY: base64.b64encode(array.tobytes()).decode('ascii'),
            NumpyKeys.DATA_TYPE: array.dtype.str,
            NumpyKeys.SHAPE: list(array.shape),
        }
    }


def decode_numpy_array(encoded_array: Dict[str, Any]) -> numpy_ndarray_type:
    """ Decode a numpy array from database.

    Args:
        encoded_array: The encoded array to decode.

    Returns:
        The decoded array.
    """
    array: numpy_ndarray_type
    content = encoded_array[NumpyKeys.CONTENT]
    array = np.frombuffer(base64.b64decode(content[NumpyKeys.ARRAY]),
                          dtype=np.dtype(content[NumpyKeys.DATA_TYPE])).reshape(content[NumpyKeys.SHAPE])
    # recreate the array to make it writable
    array = np.array(array)

    return array


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
tag_separator = '.'
mongo_tag_separator = '/'
_mongo_tag_separator_regex = re.escape(mongo_tag_separator)

""" Design decisions

- Data is stored in the subfield `value`. This allows for queries on data without full data retrieval
- Numpy floating point scalars are cast to floats
- Numpy arrays are handled natively
- Tags are allowed to contain a dot (to allow for ISO format timestamps)
- The serialization of the fields happens because we serialize the full data and we need to keep the keys and fields consistent. In practice we only accept str or int as fields, so not much happens
- The encoding of the field is done to handle cases like int (which occurs in the qcodes snapshots)
- We use the / as a tag separator inside MongoDB. No . because we need that for timestamp tags. No | or > since that has special meaning in regexp. maybe take symnbol from extended ascii set

"""


class StorageMongoDb(StorageInterface):
    """Reference implementation of StorageInterface with an mongodb backend

    Uses the materialized path design in a MongoDB collection see https://docs.mongodb.com/manual/tutorial/model-tree-structures-with-materialized-paths/
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
            serializer: Serialized used for data serialization.
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

    def _retrieve_value_by_tag(self, tag: TagType, field: Optional[str] = None) -> Any:
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
            raise NoDataAtKeyError(f'Tag "{tag}" cannot be found')
        elif 'value' not in doc:
            raise NoDataAtKeyError(f'Tag "{tag}" is not a leaf')
        else:
            if field is None:
                return doc['value']
            elif field in doc['value']:
                return doc['value'][field]
            else:
                raise NoDataAtKeyError(f'The field "{field}" does not exists')

    def _store_value_by_tag(self, tag: TagType, data: Any,
                            field: Optional[str] = None) -> None:
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

        document_query = {qi_tag: tag}
        doc = self._collection.find_one(document_query)
        if doc:
            # update
            if field is None:
                self._collection.update_one(document_query, {'$set': {'value': data}})
            else:
                self._collection.update_one(document_query, {'$set': {'value.'+(field): data}})

        else:
            if field is None:
                self._collection.insert_one( {qi_tag: tag, 'value': data})
            else:
                raise NoDataAtKeyError(f'Tag "{tag}" does not exist')

    def load_data(self, tag: TagType) -> Any:
        # docstring inherited
        validated_tag = self._validate_tag(tag)

        return self._unserialize(self._decode_data(self._retrieve_value_by_tag(validated_tag)))

    def load_raw_document(self, tag: TagType) -> Any:
        """Load MongoDB document without decoding """
        validated_tag = self._validate_tag(tag)

        return self._collection.find_one({qi_tag: validated_tag})

    def save_raw_document(self, data: Any, tag: TagType) -> None:
        """ Save MongoDB document without encoding """
        validated_tag = self._validate_tag(tag)

        return self._store_value_by_tag(validated_tag, data)

    @staticmethod
    def _validate_tag(tag: TagType) -> TagType:  # type: ignore
        """ Assert that tag is a list of strings."""
        if isinstance(tag, str):
            tag = mongo_tag_separator.join(tag.split(tag_separator))
            return tag

        if not isinstance(tag, list) or not all(isinstance(item, str) for item in tag):
            raise TypeError(f'Tag {tag} should be a list of strings')
        if np.any([mongo_tag_separator in t for t in tag]):
            raise Exception(f'{mongo_tag_separator} not allowed in tag components')
        return mongo_tag_separator.join(tag)

    @staticmethod
    def _unpack_tag(tag: TagType) -> TagType:
        if isinstance(tag, str):
            return tag.split(mongo_tag_separator)
        else:
            return tag

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

        tag = self._validate_tag(tag)
        self._validate_field(field)

        if len(tag) == 0:
            raise NoDataAtKeyError('Tag cannot be empty')

        return self._unserialize(self._decode_data(
            self._retrieve_value_by_tag(tag, field=self._encode_field(self._serialize(field)))))

    def update_individual_data(self, data: Any, tag: TagType, field: Union[str, int]) -> None:
        """ Update an individual field at a given tag with the given data.
        If the field does not exist, it will be created.

            Args:
                data: Data to update
                tag: The tag
                field: Name of the individual field to updated

        """

        tag = self._validate_tag(tag)
        self._validate_field(field)
        self._store_value_by_tag(tag, self._encode_data(self._serialize(data)),
                                 self._encode_field(self._serialize(field)))

    def get_latest_subtag(self, tag: TagType) -> Optional[TagType]:  # type: ignore
        """ Get the latest subtag

        Args:
            tag: Tag to search from
        Returns:
            Latest subtag found among subtags or None if there are no subtags
        """
        child_tags = self.list_data_subtags(tag, limit=1)
        if len(child_tags) == 0:
            return None

        return self._unpack_tag(tag) + [child_tags[0]]  # type: ignore

    def list_data_subtags(self, tag: TagType, limit: int = 0, return_full_tag=False) -> TagType:  # type: ignore
        """ List subtags for the given tag.

        Args:
            tag: Tag to search from
            limit: Maximum number of subtags to return. If set to zero there is no limit
            return_full_tag: If True, return the full tag
        Returns:
            List of subtags found, sorted in descending order
        """
        try:
            validated_tag = self._validate_tag(tag)

            if validated_tag == '':
                tag_query = {'$regex': '^.*$'}
            else:
                tag_query = {'$regex': f'^{validated_tag}{_mongo_tag_separator_regex}.*$'}
            c = self._collection.find({qi_tag: tag_query}, {'value': 0},  limit=limit,  sort=[(qi_tag, -1)])
            tags = list(map(itemgetter(qi_tag), c))

            def last_part(t: str) -> str:
                r = t[len(validated_tag)+1:]
                n = t[:len(validated_tag)+1] + r.split(mongo_tag_separator)[0]
                return n
            tags = [last_part(t) for t in tags]
            tags = sorted(list(set(tags)))[::-1]
        except NoDataAtKeyError:
            tags = []

        if not return_full_tag:
            tags = [t.split(mongo_tag_separator)[-1] for t in tags]
        return tags

    def search(self, query: str) -> Any:
        raise NotImplementedError()

    def tag_in_storage(self, tag: TagType) -> bool:
        # docstring inherited
        validated_tag = self._validate_tag(tag)
        doc = self._collection.find_one({qi_tag: validated_tag}, {'value': 0})
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
            else StorageMongoDb._encode_str(field)

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
    def _encode_str(value: str) -> str:
        """Encodes a (dotted) string
        Args:
            value: The value

        Returns:
            The encoded value
        """

        return value.replace('.', '\\u002e')

    @staticmethod
    def _decode_str(value: str) -> str:
        """Decodes a (dotted) string

        Args:
            value: The value

        Returns:
            The decoded value
        """

        return value.replace('\\u002e', '.')

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
                StorageMongoDb._encode_str(StorageMongoDb._encode_int(key) if isinstance(key, int) else key): StorageMongoDb._encode_data(value)
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
                StorageMongoDb._decode_int(StorageMongoDb._decode_str(key))
                if StorageMongoDb._is_encoded_int(key) else StorageMongoDb._decode_str(key): StorageMongoDb._decode_data(value)
                for key, value in data.items()
            }

        elif isinstance(data, list):
            return [StorageMongoDb._decode_data(item) for item in data]

        return data

    def query_data(self, tag: TagType, limit: int = 0, fields: Optional[List[str]] = None) -> List[Any]:
        """ Query data by tag and return part of the results 

        Returns data for all subtags of the specified tag

        Args:
            tag: Tag to be removed
            limit: Maximum number of documents to inclide in the return
            fields: Fields to select

        Returns:
            List with data for retrieved documents
        """
        validated_tag = self._validate_tag(tag)
        if validated_tag == '':
            tag_query = {'$regex': f'^[^{mongo_tag_separator}]*$'}
        else:
            tag_query = {'$regex': f'^{validated_tag}{mongo_tag_separator}[^{mongo_tag_separator}]*$'}
        if fields is None:
            selection = {'value': 1}
        else:
            selection = {f'value.{f}': 1 for f in fields}
        c = self._collection.find({qi_tag: tag_query}, selection,  limit=limit,  sort=[(qi_tag, -1)])
        raw_data = list(map(itemgetter('value'), c))
        data = self._unserialize(self._decode_data(raw_data))
        return data  # type: ignore
    
    def query_data_tags(self, tag: TagType, limit: int = 0, fields : Optional[List[str]] = None) -> Tuple[List[Any], List[Any]]:
        """ Query data by tag and return both the tags and data"""
        validated_tag = self._validate_tag(tag)
        if validated_tag == '':
                    tag_query = {'$regex': f'^[^{mongo_tag_separator}]*$'}
        else:
                    tag_query = {'$regex': f'^{validated_tag}{mongo_tag_separator}[^{mongo_tag_separator}]*$'}
        selection={qi_tag: 1,}
        if fields is None:
            selection.update({'value': 1})
        else:
            selection.update({f'value.{f}':1 for f in fields})
        c = self._collection.find({qi_tag: tag_query}, selection,  limit=limit,  sort=[(qi_tag, -1)])
        raw_data = list(map(itemgetter(qi_tag, 'value'), c))      
        if raw_data:
            tags, data = list(zip(*raw_data))
            tags = [self._unpack_tag(t) for t in tags]
            data  = self._unserialize(self._decode_data(list(data)))
        else:
            tags=[]; data=[]
        return tags, data 

    def delete_data(self, tag: TagType) -> None:
        """ Remove data for the specified tag 

        Args:
            tag: Tag to be removed
        """
        result = self._collection.delete_one({qi_tag: tag})
        if result.deleted_count == 0:
            raise NoDataAtKeyError('could not delete {tag}')


# %%
if __name__ == '__main__':
    import uuid
    s = self = StorageMongoDb('test_database')# 'test'+str(uuid.uuid4()))
    docs = self._collection.find()
    for d in docs:
        s.delete_data(d[qi_tag])
    
    st=s.list_data_subtags('')
    assert st==[]
    s.query_data_tags('b')
    
    s.save_data({'one': 1}, 'a.b.c.d.e')
    s.save_data(2, 'a.b.c.d.f')
    s.save_data(2, 'b.c')
    tag = 'a.b'
    assert 'c' in s.list_data_subtags(tag)
    #s = self= StorageMongoDb('p')
    col = s._collection
    resp = col.create_index([(qi_tag, 1)])
    resp = col.create_index([(qi_tag, -1)])
    list(col.list_indexes())

    s.save_data({'one': np.array([1, 2, 4.])}, ['numpy'])
    s.save_data({0: 'integer'}, ['0'])
    s.save_data({'list': 'abc'}, ['a', 'b', 'c'])

    tag = 'a.b.c'
    only_field = s.load_individual_data(tag, field='list')

    import numpy as np
    #s = StorageMongoDb('p')
    for ii in range(10):
        s.save_data({'x': ii, 'y': (ii, str(ii)), 'z': np.array([np.random.rand()])}, ['mydata', str(ii)])
    results = s.query_data(tag, fields=['y', 'z'])

# %%
if __name__ == '__main__':

    import datetime

    tag = 'mydata'

    results = s.query_data(tag)
    fields = ['z']
    results = s.query_data(tag, fields=fields)
    print(results)

    r = self._collection.insert_one({qi_tag: 'testxx', 'value': np.array([1, 2, 3.])})
    #r=self._collection.insert_one({qi_tag: 'testxx', 'value': (1,3)})
    r = self._collection.insert_one({qi_tag: 'testd', 'value': {'tuple': (1, 3), 'array': np.array([1, 2])}})
    r
    self.load_data('testd')
    self.load_data('testxx').dtype

    self.save_data([100, np.inf, None], 'test.a.b')
    value = self.load_data('test.a.b')
    print(value)
    raw = self.load_raw_document('test.a.b')
    print(raw)

    v = datetime.datetime.now().isoformat()
    self.save_data([100, np.inf, None], ['test', v])
    value = self.load_data(['test', v])
    print(value)
    raw = self.load_raw_document(['test', v])
    print(raw)

    self.save_data({1: 'nofloat', 0: 'int'}, ['test'])
    value = self.load_data(['test'])
    print(value)
    raw = self.load_raw_document(['test'])
    print(raw)

    self._serialize({'a': (1, 2), 'b': np.array([1, 2.])})
