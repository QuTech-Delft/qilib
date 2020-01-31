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
from typing import Dict

from qilib.configuration_helper.instrument_adapter_factory import InstrumentAdapterFactory
from qilib.configuration_helper.instrument_adapter import InstrumentAdapter


class SerialPortResolver:
    """ Creates InstrumentAdapters with a serialport connection.

    Factory class responsible for creating instances of the InstrumentAdapter with a serialport connection.
    The serial port number is resolved from the given identifier and used as address to create the
    InstrumentAdapter. The identifier, serial port address combinations are stored in the
    serial_port_identifiers dictionary.
    """

    serial_port_identifiers: Dict[str, str] = {'spirack3': 'COM3',
                                               'spirack4': 'COM1',
                                               'spirack7': 'COM6'}

    @classmethod
    def get_serial_port_adapter(cls, serial_port_adapter_class_name: str, identifier: str) -> InstrumentAdapter:
        """ Factory method for creating an InstrumentAdapter with QCoDeS instrument.

        Gets the instrument adapter given corresponding to the identifier that uniquely
        defines the connection to the QCodes instrument.

        Args:
            serial_port_adapter_class_name: The name of the InstrumentAdapter subclass.
            identifier: The address of the physical instrument.

        Returns:
             An instance of the requested InstrumentAdapter.
        """
        if identifier not in cls.serial_port_identifiers.keys():
            raise ValueError("No such identifier {0} in SerialPortResolver".format(identifier))

        serial_port = cls.serial_port_identifiers[identifier]
        return InstrumentAdapterFactory.get_instrument_adapter(serial_port_adapter_class_name, serial_port)
