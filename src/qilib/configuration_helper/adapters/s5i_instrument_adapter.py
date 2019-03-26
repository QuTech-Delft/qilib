from qcodes.instrument_drivers.QuTech.S5i import S5i

from qilib.configuration_helper.adapters import SpiModuleInstrumentAdapter


class S5iInstrumentAdapter(SpiModuleInstrumentAdapter):

    def __init__(self, address: str) -> None:
        super().__init__(address)
        self._instrument: S5i = S5i(self._name, self._spi_rack, self._module_number)
