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
from types import ModuleType
from typing import Dict, Tuple, cast

import qilib
from qilib.configuration_helper import InstrumentAdapter


class InstrumentAdapterFactory:
    """ Creates InstrumentAdapters with corresponding QCoDeS driver.

    Factory class responsible for creating instances of the InstrumentAdapter and the corresponding
    QCoDeS instrument. It is called with the name of the desired InstrumentAdapter sub-class for the
    instrument as well as a dictionary that provides key-value pairs of address specifications.
    """

    instrument_adapters: Dict[Tuple[str, str], InstrumentAdapter] = {}
    _external_adapters: Dict[str, ModuleType] = {}

    @staticmethod
    def add_instrument_adapters(package: ModuleType):
        """ Adds InstrumentAdapters (from an external package)

        Args:
            package: The package that contains InstrumentAdapters
        """

        InstrumentAdapterFactory._external_adapters.update(vars(package))

    @classmethod
    def get_instrument_adapter(cls, instrument_adapter_class_name: str, address: str) -> InstrumentAdapter:
        """ Factory method for creating an InstrumentAdapter with QCoDeS instrument.

        Args:
            instrument_adapter_class_name: Name of the InstrumentAdapter subclass.
            address: Address of the physical instrument.
        Returns:
             An instance of the requested InstrumentAdapter.

        Raises:
            ValueError: If adapter is not found or error occurred while importing the adapter.

        """
        instrument_adapter_key = instrument_adapter_class_name, str(address)
        if instrument_adapter_key in cls.instrument_adapters:
            return cls.instrument_adapters[instrument_adapter_key]

        adapter = vars(qilib.configuration_helper.adapters).get(instrument_adapter_class_name,
                                                                InstrumentAdapterFactory._external_adapters.get(
                                                                    instrument_adapter_class_name))
        if adapter is None:
            raise ValueError(f"No such InstrumentAdapter {instrument_adapter_class_name}")
        else:
            adapter = cast(InstrumentAdapter, adapter(address))
            cls.instrument_adapters[instrument_adapter_key] = adapter
            return adapter
