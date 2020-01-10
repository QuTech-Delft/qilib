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
from typing import Optional, Union, Dict, Any, Tuple

from qilib.data_set.data_array import DataArray
from qilib.data_set.mongo_data_set_io import MongoDataSetIO
from qilib.data_set.data_set_io_reader import DataSetIOReader
from qilib.data_set.data_set_io_writer import DataSetIOWriter


class MongoDataSetIOWriter(DataSetIOWriter):
    """ Allow a DataSet to store changes, and complete DataSet, to a mongodb."""

    def __init__(self, name: Optional[str] = None, document_id: Optional[str] = None,
                 database: str = MongoDataSetIO.DEFAULT_DATABASE_NAME,
                 collection: str = MongoDataSetIO.DEFAULT_COLLECTION_NAME) -> None:
        """ Construct a new instance of MongoDataSetIOWriter. If name is provided, but not found in the database
            a new document is created with that name.

        Args:
            name: DataSet name.
            document_id: _id of the DataSet in the database.
            database: Name of the database.
            collection: Name of the collections.

        Raises:
            DocumentNotFoundError: If document_id is provided but not found in the database.

        """
        super().__init__()
        self._mongo_data_set_io = MongoDataSetIO(name, document_id, database=database, collection=collection)

    def sync_metadata_to_storage(self, field_name: str, value: Any) -> None:
        """ Update or add metadata field to database.

        Args:
            field_name: Field that changed.
            value:  The new value.

        """
        self._is_finalized()
        update_data = {"{}.{}".format(DataSetIOReader.METADATA, field_name): value}
        self._mongo_data_set_io.update_document(update_data)

    def sync_data_to_storage(self, index_or_slice: Union[Tuple[int, ...], int], data: Dict[str, Any]) -> None:
        """ Registers a DataArray update to the database. The change is registered as a change event and is
            applied on finalize().

        Args:
            index_or_slice: The indices of the DataArray to update.
            data: Name of the DataArray to be updated and the new value.

        """
        self._is_finalized()
        update_data = {DataSetIOReader.ARRAY_UPDATES: (index_or_slice, data)}
        self._mongo_data_set_io.append_to_document(update_data)

    def sync_add_data_array_to_storage(self, data_array: DataArray) -> None:
        """ Add or update a DataArray in the database.

        Args:
            data_array: The DataArray to be updated or added.

        """
        self._is_finalized()
        update_data = {"{}.{}".format(DataSetIOReader.DATA_ARRAYS, data_array.name): {
            "name": data_array.name,
            "label": data_array.label,
            "unit": data_array.unit,
            "is_setpoint": data_array.is_setpoint,
            "set_arrays": [array.name for array in data_array.set_arrays],
            "preset_data": MongoDataSetIO.encode_numpy_array(data_array)}}
        self._mongo_data_set_io.update_document(update_data)

    def finalize(self) -> None:
        """ Update the underlying DataSet and close the connection to the database."""
        self._mongo_data_set_io.update_document({DataSetIOReader.ARRAY_UPDATES: []})
        self._mongo_data_set_io.finalize()
        self._finalized = True
