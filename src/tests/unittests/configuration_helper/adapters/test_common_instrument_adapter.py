import unittest

from qilib.utils import PythonJsonStructure
from tests.test_data.dummy_instrument_adapter import DummyInstrumentAdapter


class TestCommonInstrumentAdapter(unittest.TestCase):
    def test_instantiate_with_name(self):
        adapter = DummyInstrumentAdapter('dummy_address', 'fake_dummy_instrument')
        self.assertEqual('DummyInstrumentAdapter_dummy_address', adapter.name)
        self.assertEqual('fake_dummy_instrument', adapter.instrument.name)
        adapter.close_instrument()

    def test_change_name_with_config(self):
        adapter = DummyInstrumentAdapter('dummy_address')
        self.assertEqual('DummyInstrumentAdapter_dummy_address', adapter.name)
        self.assertEqual('DummyInstrumentAdapter_dummy_address', adapter.instrument.name)
        config = PythonJsonStructure(name='new_name')
        adapter.apply(config)
        self.assertEqual('DummyInstrumentAdapter_dummy_address', adapter.name)
        self.assertNotEqual('new_name', adapter.instrument.name)
        adapter.close_instrument()
