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
import re
from typing import Tuple, Type, Optional, cast
from spirack import SPI_rack
from qilib.configuration_helper.serial_port_resolver import SerialPortResolver
from qilib.configuration_helper.adapters.spi_rack_instrument_adapter import SpiRackInstrumentAdapter
from qilib.configuration_helper.adapters.common_instrument_adapter import CommonInstrumentAdapter

from qilib.utils.python_json_structure import PythonJsonStructure


class SpiModuleInstrumentAdapter(CommonInstrumentAdapter):

    def __init__(self, address: str, instrument_name: Optional[str] = None,
                 spi_rack_instrument_adapter_class: Optional[Type[SpiRackInstrumentAdapter]] = None) -> None:
        """ The base instrument adapter for each SPI rack module.

        Each module is identified using the name of the spirack the module number. The address is
        the combined value, e.g. 'spirack1_module10'.

        Args:
            address: The unique identifier of the SPI rack module, which should be of the form
                     <spi_name>_module<module_number>, where spi_name is the name of the spi rack
                     and module_number the integer module number.
            instrument_name: An optional name for the underlying instrument.
        """
        super().__init__(address, instrument_name)
        identifier, self._module_number = SpiModuleInstrumentAdapter.__collect_settings(address)
        if spi_rack_instrument_adapter_class is None:
            spi_rack_instrument_adapter_class = SpiRackInstrumentAdapter
        adapter: SpiRackInstrumentAdapter = cast(SpiRackInstrumentAdapter,
                                                 SerialPortResolver.get_serial_port_adapter(
                                                     spi_rack_instrument_adapter_class.__name__, identifier))
        self._spi_rack: SPI_rack = adapter.spi_rack

    def read(self, update: bool = True) -> PythonJsonStructure:
        """ Reads and returns all SPI rack module settings from the device.

        All module parameters will be collected, even if the parameter is write only.
        If the write only parameter has not been set, a None will be set as value.

        Args:
            update: Update the settings first before returning the settings configuration.

        Returns:
            A custom dictionary with all the SPI rack module settings.
        """
        return PythonJsonStructure(super().read(update))

    def _filter_parameters(self, parameters: PythonJsonStructure) -> PythonJsonStructure:
        """ Removes the identifier parameter from the configuration settings.

        Args:
            parameters: A custom dictionary with all the SPI rack module settings.
        """
        parameters.pop('IDN')
        return parameters

    @staticmethod
    def __collect_settings(address: str) -> Tuple[str, int]:
        """ Collects the SPI rack name and the module number from the address identifier.

        Args:
            address: The address of the spirack and the module.

        Returns:
            Contains two items, the spirack identifier as string and the module number as integer.
        """
        results = re.match(r'(\w+)_module(\d+)', address)
        if results is not None:
            identifier = results.group(1)
            module = int(results.group(2))
        else:
            error_message = "Invalid address format. ({} != <spi_name>_module<module_number>)".format(address)
            raise ValueError(error_message)
        return identifier, module
