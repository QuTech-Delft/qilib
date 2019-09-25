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
from typing import Any, Optional

from qcodes.instrument_drivers.QuTech.D5a import D5a

from qilib.configuration_helper.adapters import SpiModuleInstrumentAdapter
from qilib.utils import PythonJsonStructure


class SpanValueError(Exception):
    """ Error when dacs have misconfigured span values."""

class ConfigurationError(Exception):
    """ Error to raise if configuration does not match."""


DAC_STEP = 10e-3
INTER_DELAY = 0.1
RESET_VOLTAGE = False
MV = True


class D5aInstrumentAdapter(SpiModuleInstrumentAdapter):

    def __init__(self, address: str, instrument_name: Optional[str] = None) -> None:
        super().__init__(address, instrument_name)
        self._instrument = D5a(self._instrument_name, self._spi_rack, self._module_number, mV=MV,
                               inter_delay=INTER_DELAY,
                               reset_voltages=RESET_VOLTAGE, dac_step=DAC_STEP)
        if self._instrument.span3() != '4v bi':
            raise SpanValueError('D5a instrument has span unequal to "4v bi"')

    def apply(self, config: PythonJsonStructure) -> None:
        """ Applies config only for  step and inter_delay and for others cofigs with set value does a comparison

        Args:
            config: Containing the instrument configuration.

        Raises:
            ConfigurationError: If config does not match device configuration .

        """
        unit = config['dac1']['unit']
        self._instrument.set_dac_unit(unit)
        dac_parameters = {param: values for param, values in config.items() if param[0:3] == 'dac'}
        for dac, values in dac_parameters.items():
            self._instrument[dac].step = values['step']
            self._instrument[dac].inter_delay = values['inter_delay']

        device_config = self.read(True)

        for parameter in config:
            if parameter in self._instrument.parameters and hasattr(self._instrument.parameters[parameter], 'set'):
                if 'value' in config[parameter]:
                    self._assert_value_matches(config[parameter]['value'], device_config[parameter]['value'], parameter)

    @staticmethod
    def _assert_value_matches(config_value: Any, device_value: Any, parameter: str) -> None:
        if config_value != device_value:
            raise ConfigurationError(
                "Configuration for {} does not match: '{}' != '{}'".format(parameter, config_value, device_value))
