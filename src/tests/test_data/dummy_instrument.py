from qcodes import Instrument


class DummyInstrument(Instrument):

    def __init__(self, name, **kwargs):
        """ Dummy instrument used for testing."""
        super().__init__(name, **kwargs)

        self.add_parameter('amplitude',
                           label='%s amplitude' % name,
                           unit='V',
                           get_cmd=None,
                           set_cmd=None
                           )
        self.add_parameter('frequency',
                           get_cmd=None,
                           set_cmd=None,
                           unit='Hz',
                           label=name)
        self.add_parameter('enable_output',
                           get_cmd=None,
                           set_cmd=None,
                           label=name)

    def __str__(self):
        return self.__class__.__name__

    def get_idn(self):
        idn = {'vendor': 'QuTech', 'model': self.name,
               'serial': 42, 'firmware': '20-05-2019-RC'}
        return idn


class DummyAMI430Instrument(Instrument):

    def __init__(self, name, **kwargs):
        """ Dummy AMI430 instrument used for testing."""
        super().__init__(name, **kwargs)

        self.add_parameter('field_ramp_limit',
                           unit='T/min',
                           get_cmd=None,
                           set_cmd=None,
                           label=name
                           )
        self.add_parameter('field',
                           get_cmd=None,
                           set_cmd=None,
                           unit='T',
                           label=name)

    def get_idn(self):
        idn = {'vendor': 'QuTech', 'model': self.name,
               'serial': 52, 'firmware': '27-09-2019-RC'}
        return idn
