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
from typing import Optional, Dict, Any, Union, MutableMapping

from bson.objectid import ObjectId
from pymongo.change_stream import CollectionChangeStream
from pymongo.errors import DuplicateKeyError
from pymongo.mongo_client import MongoClient
from qilib.data_set.data_array import DataArray
from qilib.utils.serialization import NumpyArrayEncDec
from qilib.utils.type_aliases import EncodedNumpyArray, NumpyNdarrayType


class DocumentNotFoundError(Exception):
    """ Error that is raised when document is not found."""


class FieldNotUniqueError(Exception):
    """ Error raised if field is not unique"""


class MongoDataSetIO:
    """ Helper class for the MongoDataSetIOReader and -Writer"""

    DEFAULT_DATABASE_NAME = 'qilib'
    DEFAULT_COLLECTION_NAME = 'data_sets'

    def __init__(self, name: Optional[str] = None, document_id: Optional[str] = None,
                 create_if_not_found: Optional[bool] = True, database: str = DEFAULT_DATABASE_NAME,
                 collection: str = DEFAULT_COLLECTION_NAME) -> None:
        """

        Args:
            name: Name of the document.
            document_id: The document _id.
            create_if_not_found: Create a new document if no match is found.
            database: Name of the database.
            collection: Name of the collections.

        Raises:
            DocumentNotFoundError: If document not found in database.
        """

        if name is None and document_id is None:
            raise DocumentNotFoundError("Neither 'name' nor 'document_id' were provided.")

        self._client = MongoClient()  # type: MongoClient[Any]
        self._db = self._client[database][collection]
        self._assert_name_field_is_unique()

        query_dict: MutableMapping[str, Any] = {}
        if name is not None:
            query_dict['name'] = name
        if document_id is not None:
            query_dict['_id'] = ObjectId(document_id)
        document = self._db.find_one(query_dict)
        if document is None:
            if name is not None and document_id is None and create_if_not_found:
                self._id = str(self._db.insert_one(query_dict).inserted_id)
                self._name = name
            else:
                raise DocumentNotFoundError("Document not found in database.")
        else:
            self._id = str(document.get('_id'))
            self._name = document.get('name')

    @property
    def name(self) -> str:
        return self._name

    @property
    def id(self) -> str:
        return self._id

    def watch(self) -> CollectionChangeStream[Any]:
        """ Start watching the underlying document for updates.

        Returns:
            A blocking watch-cursor iterator that returns updates when available.

        """
        pipeline = [{'$match': {'fullDocument.name': self._name}}]
        cursor = self._db.watch(pipeline=pipeline, full_document='updateLookup')
        return cursor

    def get_document(self) -> Any:
        """ Get the complete document from the database.

        Returns:
            A complete document.

        """
        document = self._db.find_one({"_id": ObjectId(self._id)})
        return document

    def finalize(self) -> None:
        """ Close the connection to the database."""
        self._client.close()

    def append_to_document(self, data: Dict[str, Any]) -> None:
        """ Append data to an array in the underlying document.

        Args:
            data: Data to append to the document.

        """
        self._db.update_one(
            {"name": self._name},
            {"$push": data,
             "$currentDate": {"lastModified": True}})

    def update_document(self, data: Dict[str, Any]) -> None:
        """ Update data in the underlying document.

        Args:
            data: Data to be updated.

        """
        self._db.update_one(
            {"name": self._name},
            {"$set": data,
             "$currentDate": {"lastModified": True}})

    @staticmethod
    def encode_numpy_array(array: Union[NumpyNdarrayType, DataArray]) -> EncodedNumpyArray:
        """ Encode numpy array to store in database.
        Args:
            array: Numpy array to encode.

        Returns:
            The encoded array.

        """
        if isinstance(array, DataArray):
            array = array.data
        return NumpyArrayEncDec.encode(array)

    @staticmethod
    def decode_numpy_array(encoded_array: Dict[str, Any]) -> NumpyNdarrayType:
        """ Decode a numpy array from database.

        Args:
            encoded_array: The encoded array to decode.

        Returns:
            The decoded array.
        """
        return NumpyArrayEncDec.decode(encoded_array)

    def _assert_name_field_is_unique(self) -> None:
        """ The field 'name' should be unique in the database.

        Raises:
            FieldNotUniqueError: If there is already a duplicate name in the database or if this method otherwise
                fails to set 'name' unique.

        """
        try:
            self._db.create_index("name", unique=True)
        except DuplicateKeyError as e:
            raise FieldNotUniqueError("Failed to set field 'name' unique.") from e
        else:
            index_info = self._db.index_information()
            if index_info['name_1']['unique'] is False:
                raise FieldNotUniqueError("Field 'name' is not unique in database.")
