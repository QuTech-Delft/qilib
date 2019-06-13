from qilib.configuration_helper import InstrumentAdapter
from qilib.utils import PythonJsonStructure

try:
    from qtt.instrument_drivers.settings import SettingsInstrument
except ImportError as e:
    raise ImportError(
        "Quantum Technology Toolbox, qtt, not installed. Please do 'pip install qtt' or install from source.") from e


class SettingsInstrumentAdapter(InstrumentAdapter):
    def __init__(self, address: str) -> None:
        super().__init__(address)
        self._instrument = SettingsInstrument(self._name)

    def apply(self, config: PythonJsonStructure) -> None:
        """ As there is no configuration to apply, this method is a NOP."""

    def read(self, update: bool = False) -> PythonJsonStructure:
        """ Override default read mechanism as this adapter has no real configuration.

        Returns:
            Empty python-json structure.
        """
        return super().read(update)

    def _filter_parameters(self, parameters: PythonJsonStructure) -> PythonJsonStructure:
        """ As there is no configuration to read, this method is a NOP."""
        return parameters
