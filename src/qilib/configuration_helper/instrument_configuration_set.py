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
from typing import Union, List

from qilib.configuration_helper import InstrumentConfiguration
from qilib.utils.storage.interface import StorageInterface


class DuplicateTagError(Exception):
    """ Raised if tag already in storage."""


class InstrumentConfigurationSet:
    def __init__(self, storage: StorageInterface, tag: Union[None, List[str]] = None,
                 instruments: Union[None, List[InstrumentConfiguration]] = None):
        self._storage = storage
        self._tag = [StorageInterface.datetag_part()] if tag is None else tag
        if instruments is None:
            instruments = []
        self._instruments = instruments

    @property
    def tag(self) -> List[str]:
        return self._tag

    @property
    def instruments(self) -> List[InstrumentConfiguration]:
        return self._instruments

    @staticmethod
    def load(tag: List[str], storage: StorageInterface) -> 'InstrumentConfigurationSet':
        document = storage.load_data(tag)
        instruments = [InstrumentConfiguration.load(instrument_tag, storage)
                       for instrument_tag in document['instruments']]

        return InstrumentConfigurationSet(storage, tag, instruments)

    def store(self) -> None:
        if self._storage.tag_in_storage(self._tag):
            raise DuplicateTagError(f'InstrumentConfiguration with tag \'{self._tag}\' already in storage')

        instruments = [instrument.tag for instrument in self.instruments]
        self._storage.save_data(instruments, self._tag)

    # todo: generate tags in proper way
    def snapshot(self, tag: Union[None, List[str]] = None) -> None:
        self._tag = [StorageInterface.datetag_part()] if tag is None else tag

        for instrument in self._instruments:
            instrument.refresh()

    def apply(self) -> None:
        for instrument in self.instruments:
            instrument.apply()

    def apply_delta(self, update: bool = True) -> None:
        for instrument in self.instruments:
            instrument.apply_delta(update)

    def apply_delta_lazy(self) -> None:
        for instrument in self.instruments:
            instrument.apply_delta_lazy()
