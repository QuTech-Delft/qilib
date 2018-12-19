import unittest
import numpy as np

from qilib.utils.serialization import serialize, unserialize


class TestSerialization(unittest.TestCase):

    def setUp(self):
        self.testdata = [10, 3.14, 'string', b'bytes', {'a': 1, 'b': 2}, [1, 2], [1, [2, 3]]]
        self.testdata_arrays = [np.array([1, 2, 3]), np.array([1.0, 2.0]), np.array([[1.0, 0], [0, -.2], [0.123, .0]])]

    def test_serialization_default_types(self):
        for x in self.testdata:
            s = serialize(x)
            xx = unserialize(s)
            self.assertEqual(x, xx)
        for x in self.testdata_arrays:
            s = serialize(x)
            xx = unserialize(s)
            self.assertSequenceEqual(x.tolist(), xx.tolist())

    def test_non_serializable_objects(self):
        with self.assertRaisesRegex(TypeError, 'is not JSON serializable'):
            serialize(object())
