from abc import ABC
from typing import Any

from qilib.utils.storage import StorageMongoDb


class DummyStorage(StorageMongoDb, ABC):

    def __init__(self, name, **kwargs):
        """ Dummy storage used for testing."""
        super().__init__(name, **kwargs)

    def encode_serialize_data(self, data: Any) -> Any:
        return self._encode_data(self._serialize(data))
