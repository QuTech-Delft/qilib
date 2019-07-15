"""Quantum Inspire library

Copyright 2019 QuTech Delft

qilib is available under the [MIT open-source license](https://opensource.org/licenses/MIT):

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

try:
    from qtt.instrument_drivers.virtualAwg.virtual_awg import VirtualAwg
    from qtt.instrument_drivers.virtualAwg.settings import SettingsInstrument
except ImportError as e:
    raise ImportError(
        "Quantum Technology Toolbox, qtt, not installed or incorrect version."
        " Please do 'pip install --upgrade qtt' or install from source.") from e

from typing import Dict

from qilib.configuration_helper import InstrumentAdapter, InstrumentAdapterFactory
from qilib.configuration_helper.adapters.constants import INSTRUMENTS, ADAPTER_CLASS_NAME, ADDRESS, CONFIG, SETTINGS, \
    AWG_MAP
from qilib.utils import PythonJsonStructure


class VirtualAwgInstrumentAdapter(InstrumentAdapter):
    def __init__(self, address: str) -> None:
        super().__init__(address)

        settings_instrument = SettingsInstrument('settings')
        self._instrument: VirtualAwg = VirtualAwg(settings=settings_instrument)
        self._adapters: Dict[str, InstrumentAdapter] = {}

    def apply(self, config: PythonJsonStructure) -> None:
        self._instrument.instruments = []
        self._adapters = {}

        instruments = config[INSTRUMENTS]
        for instrument in instruments:
            adapter_class_name = instruments[instrument][ADAPTER_CLASS_NAME]
            address = instruments[instrument][ADDRESS]
            adapter_config = instruments[instrument][CONFIG]
            self.add_adapter_to_instrument_adapter(adapter_class_name, address)
            adapter = self._adapters[instrument]
            adapter.apply(adapter_config)

        settings_config = config[SETTINGS]
        self._instrument.settings.awg_gates = {}
        self._instrument.settings.awg_markers = {}
        self._instrument.settings.awg_map = settings_config[AWG_MAP]

        super().apply(config)

    def read(self, update: bool = False) -> PythonJsonStructure:
        config = super().read(update)
        config[INSTRUMENTS] = PythonJsonStructure()

        for adapter_name, adapter in self._adapters.items():
            config[INSTRUMENTS][adapter_name] = PythonJsonStructure()
            config[INSTRUMENTS][adapter_name][ADAPTER_CLASS_NAME] = adapter.__class__.__name__
            config[INSTRUMENTS][adapter_name][ADDRESS] = adapter.address
            config[INSTRUMENTS][adapter_name][CONFIG] = adapter.read(update)

        config[SETTINGS] = PythonJsonStructure()
        config[SETTINGS][AWG_MAP] = self._instrument.settings.awg_map

        return config

    def add_adapter_to_instrument_adapter(self, adapter_class_name: str, address: str) -> None:
        """
        Adds an instrument to the Virtual AWG instrument

        Args:
            adapter_class_name: The adapter's class name
            address: The address of the adapter
        """

        adapter = InstrumentAdapterFactory.get_instrument_adapter(adapter_class_name, address)
        if adapter.name not in self._adapters:
            self._adapters[adapter.name] = adapter
        if adapter.instrument not in self._instrument.instruments:
            self._instrument.add_instruments([adapter.instrument])

    def add_settings(self, gates: dict, markers: dict) -> None:
        """
        Adds a setting instrument to the Virtual AWG instrument

        Args:
            gates: Gates
            markers: Markers
        """

        self._instrument.settings.awg_gates = gates
        self._instrument.settings.awg_markers = markers
        self._instrument.settings.create_map()

    def _filter_parameters(self, parameters: PythonJsonStructure) -> PythonJsonStructure:
        return parameters

    def close_instrument(self) -> None:
        self._instrument.settings.close()
        super().close_instrument()
