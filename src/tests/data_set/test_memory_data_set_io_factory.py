import unittest

from qilib.data_set.memory_data_set_io_factory import MemoryDataSetIOFactory
from qilib.data_set.memory_data_set_io_reader import MemoryDataSetIOReader
from qilib.data_set.memory_data_set_io_writer import MemoryDataSetIOWriter


class TestMemoryDataSetIOFactory(unittest.TestCase):
    def test_factory(self):
        io_reader, io_writer = MemoryDataSetIOFactory.get_reader_writer_pair()
        self.assertIsInstance(io_reader, MemoryDataSetIOReader)
        self.assertIsInstance(io_writer, MemoryDataSetIOWriter)

        new_reader, new_writer = MemoryDataSetIOFactory.get_reader_writer_pair()
        self.assertIsNot(io_reader, new_reader)
        self.assertIsNot(io_writer, new_writer)
