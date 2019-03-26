from spirack import SPI_rack

from qilib.configuration_helper import InstrumentAdapter
from qilib.utils import PythonJsonStructure


class SpiRackInstrumentAdapter(InstrumentAdapter):

    def __init__(self, address: str) -> None:
        super().__init__(address)
        self._instrument: SPI_rack = SPI_rack(address, baud='115200', timeout=1)

    def apply(self, config: PythonJsonStructure) -> None:
        self._instrument.apply_settings(config['serialport'])

    def read(self, update: bool = True) -> PythonJsonStructure:
        parameters = {
            'version': self._instrument.get_firmware_version(),
            'temperature': self._instrument.get_temperature(),
            'battery': self._instrument.get_battery(),
            'serialport': self._instrument.get_settings()
        }
        return PythonJsonStructure(parameters)

    def _filter_parameters(self, parameters: PythonJsonStructure) -> PythonJsonStructure:
        return parameters
