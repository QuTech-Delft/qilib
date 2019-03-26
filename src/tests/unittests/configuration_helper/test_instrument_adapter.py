import unittest

from qilib.configuration_helper import InstrumentAdapter


class TestInstrumentAdapter(unittest.TestCase):

    def test_instantiate_abstract_class_should_fail(self):
        with self.assertRaises(TypeError):
            InstrumentAdapter('-test')
