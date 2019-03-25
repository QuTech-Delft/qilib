import re
import logging
from typing import Tuple

from qilib.configuration_helper import InstrumentAdapter, SerialPortResolver
from qilib.utils import PythonJsonStructure

from qilib.configuration_helper.adapters import SpiRackInstrumentAdapter


class SpiModuleInstrumentAdapter(InstrumentAdapter):

    def __init__(self, address: str) -> None:
        """ The base instrument adapter for each SPI rack module.

        Each module is identified using the name of the spirack the module number. The address is
        the combined value, e.g. 'spirack1_module10'.

        Args:
            address: The unique identifier of the SPI rack module, which should be of the form
                     <spi_name>_module<module_number>, where spi_name is the name of the spi rack
                     and module_number the integer module number.
        """
        super().__init__(address)
        identifier, self._module_number = SpiModuleInstrumentAdapter.__collect_settings(address)
        adapter = SerialPortResolver.get_serial_port_adapter('SpiRackInstrumentAdapter', identifier)
        self._spi_rack: SpiRackInstrumentAdapter = adapter.instrument

    def apply(self, config: PythonJsonStructure) -> None:
        """ Applies the given adapter configuration settings onto the SPI rack module.

        Only the setter commands will be updated. Note that setter only parameters which have
        not been set yield a None when reading the configuration from the instrument adapter.
        These None parameter values in the configuration will not be set. A warning will be
        given if any of the configuration parameter values are None.

        Args:
            config: The configuration with all the SPI rack module settings.
        """
        if any(config[parameter]['value'] is None for parameter in config):
            error_message = 'Some parameter values of {0} are None and will not be set!'.format(self._instrument.name)
            logging.warning(error_message)
        parameters = [parameter for parameter in config if config[parameter]['value'] is not None]
        for parameter in parameters:
            if hasattr(self._instrument.parameters[parameter], 'set'):
                self._instrument.set(parameter, config[parameter]['value'])

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
