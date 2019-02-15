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

import numpy as np
import base64
import pickle
import serialize as serialize_module


def __object_to_base64_encoded_pickle(u):
    b = pickle.dumps(u)
    return base64.b64encode(b).decode('ascii')


def __base64_encoded_pickle_to_object(c):
    b = base64.b64decode(c.encode('ascii'))
    return pickle.loads(b)


serialize_module.register_class(np.ndarray, __object_to_base64_encoded_pickle, __base64_encoded_pickle_to_object)


def _bytes_to_base64(b):
    return base64.b64encode(b).decode('ascii')


def _base64_to_bytes(c):
    return base64.b64decode(c.encode('ascii'))


serialize_module.register_class(bytes, _bytes_to_base64, _base64_to_bytes)

__msgfmt = 'json'


def serialize(data):
    """ Serialize a Python object to JSON

    Special objects might be serialized to a Python string.

    Args:
        data (object): object to be serialized
    Returns:
        blob (bytes)
    Raises:
        TypeError: If the object is not serializable
    """
    bdata = serialize_module.dumps(data, fmt=__msgfmt)
    return bdata


def unserialize(bdata):
    """ Unserialize JSON data to a Python object

    Args:
        blob (bytes): data to be unserialized
    Returns:
        data (object): unserialized Python object
    """
    data = serialize_module.loads(bdata, fmt=__msgfmt)
    return data
