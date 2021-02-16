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
from typing import Any, Optional, Type

from qcodes_contrib_drivers.drivers.QuTech.D5a import D5a

from qilib.configuration_helper.adapters.spi_rack_instrument_adapter import SpiRackInstrumentAdapter
from qilib.configuration_helper.adapters.read_only_configuration_instrument_adapter import \
    ReadOnlyConfigurationInstrumentAdapter
from qilib.configuration_helper.adapters.spi_module_instrument_adapter import SpiModuleInstrumentAdapter
from qilib.utils.python_json_structure import PythonJsonStructure


class SpanValueError(Exception):
    """ Error when dacs have misconfigured span values."""


DAC_STEP = 10e-3
INTER_DELAY = 0.1
RESET_VOLTAGE = False
MV = True


class D5aInstrumentAdapter(ReadOnlyConfigurationInstrumentAdapter, SpiModuleInstrumentAdapter):

    def __init__(self, address: str, instrument_name: Optional[str] = None,
                 instrument_class: Optional[Type[D5a]] = None,
                 spi_rack_instrument_adapter_class: Optional[Type[SpiRackInstrumentAdapter]] = None) -> None:
        super().__init__(address, instrument_name, spi_rack_instrument_adapter_class)
        if instrument_class is None:
            instrument_class = D5a
        self._instrument: D5a = instrument_class(self._instrument_name, self._spi_rack, self._module_number, mV=MV,
                                                 inter_delay=INTER_DELAY,
                                                 reset_voltages=RESET_VOLTAGE, dac_step=DAC_STEP)
        if self._instrument.span3() != '4v bi' and self._instrument.span3() != '2v bi':
            raise SpanValueError(f'D5a instrument has span {self._instrument.span3()} unequal to "4v bi" or "2v bi"')

    def apply(self, config: PythonJsonStructure) -> None:
        """ Applies configuration

        1. Apply configuration update for step, inter_delay.
        2. Apply configuration update for unit of dac parameters based on dac1 unit.
        3. Compares rest of the configuration values with setter command, to existing values and raises
           error in case of mismatch.

        Args:
            config: Containing the instrument configuration.

        """
        unit = config['dac1']['unit']
        self._instrument.set_dac_unit(unit)
        dac_parameters = {param: values for param, values in config.items() if param[0:3] == 'dac'}
        for dac, values in dac_parameters.items():
            self._instrument[dac].step = values['step']
            self._instrument[dac].inter_delay = values['inter_delay']
        super().apply(config)

    def _compare_config_values(self, config_value: Any, device_value: Any, parameter: Optional[str] = None) -> bool:
        return bool(config_value != device_value)
