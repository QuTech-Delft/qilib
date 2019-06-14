from qilib.configuration_helper.adapters import CommonInstrumentAdapter

from tests.test_data.dummy_instrument import DummyInstrument


class DummyInstrumentAdapter(CommonInstrumentAdapter):
    """ Dummy instrument adapter used for testing. """

    def __init__(self, address: str) -> None:
        super().__init__(address)
        self._instrument = DummyInstrument(name=self.name)

    def _filter_parameters(self, parameters):
        return parameters
