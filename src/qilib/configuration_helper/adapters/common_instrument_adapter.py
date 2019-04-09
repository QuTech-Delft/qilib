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
import logging
from abc import ABC

from qilib.configuration_helper import InstrumentAdapter
from qilib.utils import PythonJsonStructure


class CommonInstrumentAdapter(InstrumentAdapter, ABC):

    def apply(self, config: PythonJsonStructure) -> None:
        """ Applies the given instrument configuration settings onto the adapters instrument.

        Only the setter commands will be updated. Note that setter only parameters which have
        not been set yield a None when reading the configuration from the instrument adapter.
        These None parameter values in the configuration will not be set. A warning will be
        given if any of the configuration parameter values are None.

        Args:
            config: The configuration with settings for the adapters instrument.

        """
        parameters = [parameter for parameter in config if hasattr(self._instrument.parameters[parameter], 'set')]
        if any(config[parameter]['value'] is None for parameter in parameters):
            error_message = 'Some parameter values of {0} are None and will not be set!'.format(self._instrument.name)
            logging.warning(error_message)
        for parameter in parameters:
            if 'value' in config[parameter] and config[parameter]['value'] is not None:
                self._instrument.set(parameter, config[parameter]['value'])
