import unittest
import re

from qilib import version

class TestVersion(unittest.TestCase):
    def test_version(self):
        self.assertTrue(re.match(r'^\d+\.\d+\.\d+$', version.__version__))
