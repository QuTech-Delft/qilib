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
