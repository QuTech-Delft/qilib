import requests
from qcodes.instrument_drivers.tektronix.Keithley_6500 import Keithley_6500

from qilib.configuration_helper.adapters import CommonInstrumentAdapter
from qilib.utils import PythonJsonStructure


class Keithley6500InstrumentAdapter(CommonInstrumentAdapter):
    def __init__(self, address: str):
        super().__init__(address)
        if address[0:5] == 'TCPIP':
            self._send_request_to_instrument(address)
        self._instrument = Keithley_6500(self.name, address)

    def _filter_parameters(self, parameters: PythonJsonStructure) -> PythonJsonStructure:
        return parameters

    @staticmethod
    def _send_request_to_instrument(address):
        ip_address = address.split('::')[1]
        result = requests.get("http://{}/".format(ip_address))
