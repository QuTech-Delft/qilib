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

from json import JSONEncoder, JSONDecoder, dumps, loads


class Encoder(JSONEncoder):
    _encoders = {}

    @classmethod
    def register_encoder(cls, _type, encoder):
        cls._encoders[_type] = encoder

    def default(self, o):
        if type(o) in self._encoders:
            return self._encoders[type(o)](o)

        return JSONEncoder.default(self, o)


class Decoder(JSONDecoder):
    _decoders = {}

    @classmethod
    def register_decoder(cls, _type, decoder):
        cls._decoders[_type] = decoder

    def __init__(self):
        super().__init__(object_hook=self._object_hook)

    def _object_hook(self, obj):
        if isinstance(obj, dict):
            if '__object__' in obj:
                if obj['__object__'] in self._decoders:
                    return self._decoders[obj['__object__']](obj)
                else:
                    raise ValueError()

        return obj


def serialize(data):
    return dumps(data, cls=Encoder)


def unserialize(data):
    return loads(data, cls=Decoder)
