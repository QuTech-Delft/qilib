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
import inspect
from types import ModuleType
from typing import Dict, Tuple, Optional, Type, Any

from qilib.configuration_helper.instrument_adapter import InstrumentAdapter


class InstrumentAdapterFactory:
    """ Creates InstrumentAdapters with corresponding QCoDeS driver.

    Factory class responsible for creating instances of the InstrumentAdapter and the corresponding
    QCoDeS instrument. It is called with the name of the desired InstrumentAdapter sub-class for the
    instrument as well as a dictionary that provides key-value pairs of address specifications.
    """

    #: A container that holds all instantiated instrument adapters created by the factory.
    #: When an adapter is requested via the get_instrument_adapter method, this dictionary is
    #: checked first for an existing adapter with same name and address.
    adapter_instances: Dict[Tuple[str, str], InstrumentAdapter] = {}

    #: A dictionary containing all available adapters. External adapters can be added via add_instrument_adapter_package
    #: or add_instrument_adapter_class.
    _instrument_adapters: Dict[str, Type[InstrumentAdapter]] = {}

    @classmethod
    def add_instrument_adapter_package(cls, package: ModuleType) -> None:
        """ Adds InstrumentAdapters (from an external package)

        Args:
            package: The package that contains InstrumentAdapters

        """

        for adapter in inspect.getmembers(package, lambda m: inspect.isclass(m) and issubclass(m, InstrumentAdapter)):
            cls.add_instrument_adapter_class(adapter[1])

    @classmethod
    def add_instrument_adapter_class(cls, adapter: Type[InstrumentAdapter]) -> None:
        """
        Args:
            adapter: Adapter class to be added to the factory.
        Raises:
            TypeError: If the adapter is not subclass of InstrumentAdapter.

        """
        if not issubclass(adapter, InstrumentAdapter):
            raise TypeError(f'{adapter.__name__} is not a subclass of InstrumentAdapter')
        cls._instrument_adapters[adapter.__name__] = adapter

    @classmethod
    def get_instrument_adapter(cls, instrument_adapter_class_name: str, address: str,
                               instrument_name: Optional[str] = None) -> InstrumentAdapter:
        """ Factory method for creating an InstrumentAdapter with QCoDeS instrument.

        Args:
            instrument_adapter_class_name: Name of the InstrumentAdapter subclass.
            address: Address of the physical instrument.
            instrument_name: An optional name for the underlying instrument.

        Returns:
             An instance of the requested InstrumentAdapter.

        Raises:
            ValueError: If adapter is not found or adapter exist but with a different instrument name.

        """
        instrument_adapter_key = instrument_adapter_class_name, str(address)
        if instrument_adapter_key in cls.adapter_instances:
            return cls._get_adapter_instance(instrument_adapter_key, instrument_name)
        elif instrument_adapter_class_name in cls._instrument_adapters:
            return cls._get_new_adapter_instance(address, instrument_adapter_class_name, instrument_name)
        else:
            raise ValueError(f"No such InstrumentAdapter {instrument_adapter_class_name}")

    @classmethod
    def _get_new_adapter_instance(cls, address: str, class_name: str,
                                  instrument_name: Optional[str] = None) -> InstrumentAdapter:

        args: Any = (address, instrument_name) if instrument_name is not None else (address, )
        adapter: InstrumentAdapter = cls._instrument_adapters[class_name](*args)
        cls.adapter_instances[(class_name, str(address))] = adapter
        return adapter

    @classmethod
    def _get_adapter_instance(cls, instrument_adapter_key: Tuple[str, str],
                              instrument_name: Optional[str] = None) -> InstrumentAdapter:

        adapter = cls.adapter_instances[instrument_adapter_key]
        if instrument_name is not None and adapter.instrument is not None \
           and instrument_name != adapter.instrument.name:
            raise ValueError(f'An adapter exist with different instrument name'
                             f' \'{adapter.instrument.name}\' != \'{instrument_name}\'')
        return adapter
