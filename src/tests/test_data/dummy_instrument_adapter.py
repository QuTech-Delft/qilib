from typing import Any, Optional

from qilib.configuration_helper.adapters import CommonInstrumentAdapter
from tests.test_data.dummy_instrument import DummyInstrument


class DummyInstrumentAdapter(CommonInstrumentAdapter):
    """ Dummy instrument adapter used for testing. """

    def __init__(self, address: str, instrument_name: Optional[str] = None) -> None:
        super().__init__(address, instrument_name)

        self._instrument = DummyInstrument(name=self._instrument_name)

    def _filter_parameters(self, parameters):
        return parameters

    def  _compare_config_values(self, config_value: Any, device_value: Any, parameter: str) -> bool:
        return True
