from qcodes.instrument_drivers.american_magnetics.AMI430 import AMI430

from qilib.configuration_helper import InstrumentAdapter
from qilib.utils import PythonJsonStructure


class ConfigurationError(Exception):
    """ Error to raise if configuration does not match."""


class AMI430InstrumentAdapter(InstrumentAdapter):
    def __init__(self, address: str):
        super().__init__(address)
        self._instrument = AMI430(name=self.name, address=address)

    def apply(self, config: PythonJsonStructure) -> None:
        configuration = self.read(True)
        parameters = [parameter for parameter in config if hasattr(self._instrument.parameters[parameter], 'set')]
        for parameter in parameters:
            if 'value' in config[parameter] and config[parameter]['value'] != configuration[parameter]['value']:
                raise ConfigurationError('Stuff')

    def _filter_parameters(self, parameters: PythonJsonStructure) -> PythonJsonStructure:
        return parameters
