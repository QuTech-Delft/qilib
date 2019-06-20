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
except ImportError as e:
    raise ImportError(
        "Quantum Technology Toolbox, qtt, not installed. Please do 'pip install qtt' or install from source.") from e

from typing import Dict, Optional

from qilib.configuration_helper import InstrumentAdapter, InstrumentAdapterFactory
from qilib.configuration_helper.adapters import SettingsInstrumentAdapter
from qilib.utils import PythonJsonStructure

from qilib.configuration_helper.adapters.constants import INSTRUMENTS, ADAPTER_CLASS_NAME, ADDRESS, CONFIG, SETTINGS, \
    AWG_MAP


class VirtualAwgInstrumentAdapter(InstrumentAdapter):
    def __init__(self, address: str) -> None:
        super().__init__(address)

        self._instrument: VirtualAwg = VirtualAwg()
        self._adapters: Dict[str, InstrumentAdapter] = {}
        self._settings_adapter: Optional[SettingsInstrumentAdapter] = None

    def apply(self, config: PythonJsonStructure) -> None:
        instruments = config[INSTRUMENTS]
        for instrument in instruments:
            adapter_class_name = instruments[instrument][ADAPTER_CLASS_NAME]
            address = instruments[instrument][ADDRESS]
            adapter_config = instruments[instrument][CONFIG]
            self.add_instrument(adapter_class_name, address)
            adapter = self._adapters[instrument]
            adapter.apply(adapter_config)

        settings_config = config[SETTINGS]
        adapter = InstrumentAdapterFactory.get_instrument_adapter('SettingsInstrumentAdapter', '')
        adapter.apply(settings_config[CONFIG])
        adapter.instrument.awg_map = settings_config[AWG_MAP]

        self.instrument.settings = adapter.instrument

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
        config[SETTINGS][AWG_MAP] = self._settings_adapter.instrument.awg_map
        config[SETTINGS][CONFIG] = self._settings_adapter.read()

        return config

    def add_instrument(self, adapter_class_name: str, address: str) -> None:
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

        adapter = InstrumentAdapterFactory.get_instrument_adapter('SettingsInstrumentAdapter', '')

        adapter.instrument.awg_gates = gates
        adapter.instrument.awg_markers = markers
        adapter.instrument.create_map()

        self._instrument.settings = adapter.instrument
        self._settings_adapter = adapter

    def _filter_parameters(self, parameters: PythonJsonStructure) -> PythonJsonStructure:
        return parameters
