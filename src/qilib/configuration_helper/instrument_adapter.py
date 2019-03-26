from abc import ABC, abstractmethod

from qcodes import Instrument
from qilib.utils import PythonJsonStructure


class InstrumentAdapter(ABC):

    def __init__(self, address: str) -> None:
        """ A template for an adapter to the QCoDeS instrument interface.

        Args:
            address: The address/ID of the QCoDeS instrument.
        """
        self._name = '{0}_{1}'.format(self.__class__.__name__, address)
        self._address = address
        self._instrument: Instrument

    @property
    def name(self) -> str:
        return self._name

    @property
    def instrument(self) -> Instrument:
        return self._instrument

    @property
    def address(self) -> str:
        return self._address

    @abstractmethod
    def apply(self, config: PythonJsonStructure) -> None:
        """ An abstract method that should be implemented in subclasses.

        Writes a full set of configuration to the adapters instrument.

        Args:
            config: Containing the instrument configuration.
        """

    def read(self, update: bool = False) -> PythonJsonStructure:
        """ Obtains a full set of settings from the instrument.

        Returns:
            Contains the instrument snapshot without the
            instrument parameters which are filtered out.
        """
        parameters = PythonJsonStructure()
        if self._instrument is not None:
            snapshot = self._instrument.snapshot(update)
            parameters = self._filter_parameters(snapshot['parameters'])
        return parameters

    @abstractmethod
    def _filter_parameters(self, parameters: PythonJsonStructure) -> PythonJsonStructure:
        """ Filters out parameters that are not used for instrument configuration storage.

        This function should be overwritten in the subclasses for each specific instrument,
        if needed when reading the configuration.

        Args:
            parameters: A complete snapshot from an instrument.

        Returns:
            PythonJsonStructure: Contains the instrument snapshot without the instrument
                                 parameters which are filtered out by this function.
        """
