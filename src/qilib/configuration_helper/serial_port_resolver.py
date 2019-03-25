from typing import Dict

from qilib.configuration_helper import InstrumentAdapterFactory, InstrumentAdapter


class SerialPortResolver:
    """ Creates InstrumentAdapters with a serialport connection.

    Factory class responsible for creating instances of the InstrumentAdapter with a serialport connection.
    The serial port number is resolved from the given identifier and used as address to create the
    InstrumentAdapter. The identifier, serial port address combinations are stored in the
    serial_port_identifiers dictionary.
    """

    serial_port_identifiers: Dict[str, str] = {}

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
