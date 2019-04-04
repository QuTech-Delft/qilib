import logging

from qcodes.instrument_drivers.Spectrum.M4i import M4i

from qilib.utils import PythonJsonStructure
from qilib.configuration_helper import InstrumentAdapter


class M4iInstrumentAdapter(InstrumentAdapter):
    def __init__(self, address: str) -> None:
        super().__init__(address)
        self._instrument: M4i = M4i(self.name, cardid=address)

    def apply(self, config: PythonJsonStructure) -> None:
        if any(config[parameter]['value'] is None for parameter in config):
            error_message = 'Some parameter values of {0} are None and will not be set!'.format(self._instrument.name)
            logging.warning(error_message)
        parameters = [parameter for parameter in config if config[parameter]['value'] is not None]
        for parameter in parameters:
            if hasattr(self._instrument.parameters[parameter], 'set'):
                self._instrument.set(parameter, config[parameter]['value'])

    def read(self, update: bool = True) -> PythonJsonStructure:
        return PythonJsonStructure(super().read(update))

    def _filter_parameters(self, parameters: PythonJsonStructure) -> PythonJsonStructure:
        parameters.pop('IDN')
        return parameters
