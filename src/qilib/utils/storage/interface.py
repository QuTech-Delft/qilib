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

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Callable, Optional, Union

from qilib.utils.type_aliases import TagType


class NoDataAtKeyError(Exception):
    """ Raised when trying to get data from a node or leave can not be found."""


class NodeAlreadyExistsError(Exception):
    """ Raised when trying to create a node or leave when node already exists."""


class ConnectionTimeoutError(Exception):
    """ Raised when connection to storage can not be established."""


class StorageInterface(ABC):
    """ Base class for storage of measurement and calibration results.
        The storage is based on tags (HDF5-like).

        A tag is a list that describes the path in a tree. Data is
        stored at the leafs of the tree.

    Rules:
        nodes cannot contain data
        leaves can be overwritten by leaves
        nodes cannot be overwritten by leaves
    """

    def __init__(self, name: str) -> None:
        """
        Base constructor.

        Args:
            name: Symbolic name for the storage instance.
        """

        self.name: str = name
        self._serialize: Callable[[Any], Any] = lambda x: x
        self._unserialize: Callable[[Any], Any] = lambda x: x
        self.logger: Any = logging.getLogger(self.name)
        self.logger.info('created StorageInterface %s', self.name)

    def __repr__(self):
        return f'{self.__class__.__name__}({self.name!r})'

    @staticmethod
    def datetag_part(date_with_time: Optional[datetime] = None) -> str:
        """
        Return string with date.

        Args:
            date_with_time: optional datetime to use instead of `now()`.

        Returns:
             If dt is specified, returns the ISO 8601 formatted date as a string. If
             dt is not specified or None, returns the current date and time formatted
             as a ISO 8601 string.
        """

        if date_with_time is None:
            date_with_time = datetime.now()
        return date_with_time.isoformat()

    @abstractmethod
    def load_data(self, tag: TagType) -> Any:
        """ Load result from storage.

        Args:
            tag: tag for result to load

        Returns:
            Data found at the node identified by the tag.

        Raises:
            NoDataAtKeyException: if there is no data for the specified tag.
        """

    @staticmethod
    def _tag_to_list(tag: Union[str, TagType]) -> TagType:
        """ Convert a str or list tag to list format. """
        if not isinstance(tag, (str, list)):
            raise TypeError('tag should be of type %s' % list)
        if isinstance(tag, str):
            tag = tag.split('/')
        return tag

    @staticmethod
    def _tag_to_string(tag: Union[str, TagType]) -> str:
        """ Convert a tag to string format. """
        if not isinstance(tag, (str, list)):
            raise TypeError('tag should be of type %s' % list)
        if isinstance(tag, (list,)):
            tag = '/'.join(tag)
        return tag

    @staticmethod
    def _validate_tag(tag: TagType) -> None:
        """ Assert that tag is a list of strings."""

        if not isinstance(tag, list) or not all(isinstance(item, str) for item in tag):
            raise TypeError(f'Tag {tag} should be a list of strings')

    @abstractmethod
    def save_data(self, data: Any, tag: TagType) -> None:
        """ Save data to storage.

        Args:
            data: data to store
            tag: reference tag to store the data
        """
        pass

    @abstractmethod
    def get_latest_subtag(self, tag: TagType) -> Optional[TagType]:
        """ Return tag of latest result for a given tag.

        Args:
            tag: reference tag to retrieve latest result

        Returns:
            The tag of the first result for the nodes found at the tag sorted
            in descending order. This implies that if the node at the tag has
            children that are tagged with a datetime string, the tag of the
            most recent result is returned.

            If an invalid tag was specified, None is returned.
        """
        pass

    @abstractmethod
    def list_data_subtags(self, tag: TagType) -> TagType:
        """ List available result tags of at tag.

        Args:
            tag: hdf5 tag
        Returns:
            results: List of child tags for tag

        See also:
            load_data

        Notes:
            When an invalid path is specified (for example, a tag
            that addresses a leaf node or a tag that has a component
            that does not exist in the storage hierarchy) an empty
            list is returned.
        """
        pass

    @abstractmethod
    def search(self, query: str) -> Any:
        """ Future implementation of query interface """
        raise NotImplementedError('search interface not yet specified')

    @abstractmethod
    def tag_in_storage(self, tag: TagType) -> bool:
        """ Check if tag is already in storage
        Args:
            tag: hdf5 tag
        Returns:
            True of tag found in storage, else False.
        """
