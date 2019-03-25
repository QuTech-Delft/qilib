from qcodes.instrument_drivers.QuTech.M2j import M2j

from qilib.configuration_helper.adapters import SpiModuleInstrumentAdapter


class M2jInstrumentAdapter(SpiModuleInstrumentAdapter):

    def __init__(self, address: str) -> None:
        super().__init__(address)
        self._instrument: M2j = M2j(self._name, self._spi_rack, self._module_number)
