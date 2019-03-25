import logging

from qcodes.instrument_drivers.ZI.ZIHDAWG8 import ZIHDAWG8
from qilib.utils import PythonJsonStructure

from qilib.configuration_helper import InstrumentAdapter


class ZIHDAWG8InstrumentAdapter(InstrumentAdapter):
    def __init__(self, address: str) -> None:
        super().__init__(address)
        self._instrument: ZIHDAWG8 = ZIHDAWG8(self.name, address)

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

    def start(self, awg_number: int) -> None:
        self._instrument.start_awg(awg_number)

    def stop(self, awg_number: int) -> None:
        self._instrument.stop_awg(awg_number)

    def upload(self, sequence_program: str, awg_number: int) -> None:
        self._instrument.upload_sequence_program(awg_number, sequence_program)
