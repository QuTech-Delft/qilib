from typing import Dict

from qilib.configuration_helper import InstrumentAdapter, InstrumentAdapterFactory
from qilib.utils import PythonJsonStructure

try:
    from qtt.instrument_drivers.virtualAwg.virtual_awg import VirtualAwg
except ImportError as e:
    raise ImportError(
        "Quantum Technology Toolbox, qtt, not installed. Please do 'pip install qtt' or install from source.") from e

# Keys used in the configuration
INSTRUMENTS = 'instruments'
SETTINGS = 'settings'
AWG_MAP = 'awg_map'
CONFIG = 'config'
ADDRESS = 'address'
ADAPTER_CLASS_NAME = 'adapter_class_name'


class VirtualAwgInstrumentAdapter(InstrumentAdapter):
    def __init__(self, address):
        super().__init__(address)

        self._instrument: VirtualAwg = VirtualAwg()
        self._adapters: Dict[str, InstrumentAdapter] = {}
        self._settings_adapter = None

    def apply(self, config: PythonJsonStructure) -> None:
        instruments = config.pop(INSTRUMENTS)
        for instrument in instruments:
            adapter_class_name = instruments[instrument][ADAPTER_CLASS_NAME]
            address = instruments[instrument][ADDRESS]
            adapter_config = instruments[instrument][CONFIG]
            self.add_instrument(adapter_class_name, address)
            adapter = self._adapters[instrument]
            adapter.apply(adapter_config)

        settings_config = config.pop(SETTINGS)
        adapter = InstrumentAdapterFactory.get_instrument_adapter('SettingsInstrumentAdapter', '')
        adapter.apply(settings_config[CONFIG])
        adapter.instrument.awg_map = settings_config[AWG_MAP]

        super().apply(config)

    def read(self, update: bool = False) -> PythonJsonStructure:
        config = super().read(update)
        config[INSTRUMENTS] = PythonJsonStructure()

        for adapter_name, adapter in self._adapters.items():
            config[INSTRUMENTS][adapter_name] = PythonJsonStructure()
            config[INSTRUMENTS][adapter_name][ADAPTER_CLASS_NAME] = adapter.__class__.__name__
            config[INSTRUMENTS][adapter_name][ADDRESS] = adapter.address
            config[INSTRUMENTS][adapter_name][CONFIG] = adapter.read(True)

        config[SETTINGS] = PythonJsonStructure()
        config[SETTINGS][AWG_MAP] = self._settings_adapter.instrument.awg_map
        config[SETTINGS][CONFIG] = self._settings_adapter.read()

        return config

    def add_instrument(self, adapter_class_name, address):
        adapter = InstrumentAdapterFactory.get_instrument_adapter(adapter_class_name, address)
        if adapter.name not in self._adapters:
            self._adapters[adapter.name] = adapter
        if adapter.instrument not in self._instrument.instruments:
            self._instrument.add_instruments([adapter.instrument])

        return adapter

    def add_settings(self, gates, markers):
        adapter = InstrumentAdapterFactory.get_instrument_adapter('SettingsInstrumentAdapter', '')

        adapter.instrument.awg_gates = gates
        adapter.instrument.awg_markers = markers
        adapter.instrument.create_map()

        self._instrument.settings = adapter.instrument
        self._settings_adapter = adapter

    def _filter_parameters(self, parameters: PythonJsonStructure) -> PythonJsonStructure:
        return parameters
