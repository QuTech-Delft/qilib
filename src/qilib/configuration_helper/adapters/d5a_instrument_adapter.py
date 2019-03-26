from qcodes.instrument_drivers.QuTech.D5a import D5a

from qilib.configuration_helper.adapters import SpiModuleInstrumentAdapter


class D5aInstrumentAdapter(SpiModuleInstrumentAdapter):

    def __init__(self, address: str) -> None:
        super().__init__(address)
        self._instrument = D5a(self._name, self._spi_rack, self._module_number, mV=True)
