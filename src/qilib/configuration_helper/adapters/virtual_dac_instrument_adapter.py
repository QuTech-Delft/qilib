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
    from qtt.instrument_drivers.gates import VirtualDAC
except ImportError as e:
    raise ImportError(
        "Quantum Technology Toolbox, qtt, not installed. Please do 'pip install qtt' or install from source.") from e

from qilib.configuration_helper import InstrumentAdapterFactory
from qilib.configuration_helper.adapters import CommonInstrumentAdapter
from qilib.utils import PythonJsonStructure

# Keys in the configuration python json structure
INSTRUMENTS = 'instruments'
BOUNDARIES = 'boundaries'
GATE_MAP = 'gate_map'
CONFIG = 'config'
ADDRESS = 'address'
ADAPTER_CLASS_NAME = 'adapter_class_name'


class VirtualDACInstrumentAdapter(SpiModuleInstrumentAdapter):
    """ Adapter for the qtt VirtualDAC."""

    def __init__(self, address: str) -> None:
        super().__init__(address)
        self._instrument = VirtualDAC(self._name, instruments=[], gate_map={})
        self._dac_adapters = {}

    def _filter_parameters(self, parameters: PythonJsonStructure) -> PythonJsonStructure:
        return parameters

    def read(self, update: bool = False) -> PythonJsonStructure:
        """ Additionally reads the gate_map, boundaries and configs of the nested dacs."""

        config = PythonJsonStructure()
        config[CONFIG] = super().read(update)
        config[BOUNDARIES] = self._instrument.get_boundaries()
        config[GATE_MAP] = self._instrument.gate_map
        config[INSTRUMENTS] = PythonJsonStructure()
        for adapter_name, adapter in self._dac_adapters.items():
            config[INSTRUMENTS][adapter_name] = PythonJsonStructure()
            config[INSTRUMENTS][adapter_name][CONFIG] = adapter.read(True)
            config[INSTRUMENTS][adapter_name][ADDRESS] = adapter.address
            config[INSTRUMENTS][adapter_name][ADAPTER_CLASS_NAME] = adapter.__class__.__name__
        return config

    def apply(self, config: PythonJsonStructure) -> None:
        """ Apply config to the virtual dac and all nested dacs."""

        instruments = config[INSTRUMENTS]
        for instrument in instruments:
            adapter_class_name = instruments[instrument][ADAPTER_CLASS_NAME]
            address = instruments[instrument][ADDRESS]
            adapter_config = instruments[instrument][CONFIG]
            self._add_dac_to_instrument(adapter_class_name, address)
            self._dac_adapters[instrument].apply(adapter_config)
        self._instrument.set_boundaries(config[BOUNDARIES])
        self._instrument.gate_map = config[GATE_MAP]
        super().apply(config[CONFIG])

    def _add_dac_to_instrument(self, adapter_class_name: str, address: str) -> None:
        """ Add a dac to the virtual dac and cache a corresponding instrument adapter."""

        adapter = InstrumentAdapterFactory.get_instrument_adapter(adapter_class_name, address)
        if adapter.name not in self._dac_adapters:
            self._dac_adapters[adapter.name] = adapter
        if adapter.instrument not in self.instrument.instruments:
            self.instrument.add_instruments([adapter.instrument])
