import qilib
from typing import Dict, Tuple, cast

from qilib.configuration_helper import InstrumentAdapter


class InstrumentAdapterFactory:
    """ Creates InstrumentAdapters with corresponding QCoDeS driver.

    Factory class responsible for creating instances of the InstrumentAdapter and the corresponding
    QCoDeS instrument. It is called with the name of the desired InstrumentAdapter sub-class for the
    instrument as well as a dictionary that provides key-value pairs of address specifications.
    """

    instrument_adapters: Dict[Tuple[str, str], InstrumentAdapter] = {}

    @staticmethod
    def is_instrument_adapter(instrument_adapter_class_name: str) -> bool:
        """ Check that the class in package qilib.configuration_helper.adapters and is subclass of InstrumentAdapter

        Args:
            instrument_adapter_class_name: name of the class

        Returns:
            True if the named class exists as an InstrumentAdapter in package qilib.configuration_helper.adapters,
            False otherwise

        """
        return hasattr(qilib.configuration_helper.adapters, instrument_adapter_class_name) and issubclass(
            vars(qilib.configuration_helper.adapters)[instrument_adapter_class_name], InstrumentAdapter)

    @classmethod
    def get_instrument_adapter(cls, instrument_adapter_class_name: str, address: str) -> InstrumentAdapter:
        """ Factory method for creating an InstrumentAdapter with QCoDeS instrument.

        Args:
            instrument_adapter_class_name: Name of the InstrumentAdapter subclass.
            address: Address of the physical instrument.

        Returns:
             An instance of the requested InstrumentAdapter.
        """
        instrument_adapter_key = instrument_adapter_class_name, str(address)
        if instrument_adapter_key in cls.instrument_adapters:
            return cls.instrument_adapters[instrument_adapter_key]
        else:
            if cls.is_instrument_adapter(instrument_adapter_class_name):
                adapter = cast(InstrumentAdapter,
                               vars(qilib.configuration_helper.adapters)[instrument_adapter_class_name](address))
            else:
                raise ValueError("No such InstrumentAdapter {0}".format(instrument_adapter_class_name))
            cls.instrument_adapters[instrument_adapter_key] = adapter
            return adapter