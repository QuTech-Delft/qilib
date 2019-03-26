from qcodes.instrument_drivers.QuTech.F1d import F1d

from qilib.configuration_helper.adapters import SpiModuleInstrumentAdapter


class F1dInstrumentAdapter(SpiModuleInstrumentAdapter):

    def __init__(self, address: str) -> None:
        super().__init__(address)
        self._instrument: F1d = F1d(self.name, self._spi_rack, self._module_number)
