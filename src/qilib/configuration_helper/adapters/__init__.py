from qilib.configuration_helper import InstrumentAdapterFactory
from qilib.configuration_helper.adapters.ami430_instrument_adapter import AMI430InstrumentAdapter
from qilib.configuration_helper.adapters.common_instrument_adapter import CommonInstrumentAdapter
from qilib.configuration_helper.adapters.keithley_dmm6500_adapter import Keithley6500InstrumentAdapter
from qilib.configuration_helper.adapters.spi_rack_instrument_adapter import SpiRackInstrumentAdapter
from qilib.configuration_helper.adapters.spi_module_instrument_adapter import SpiModuleInstrumentAdapter

from qilib.configuration_helper.adapters.d5a_instrument_adapter import D5aInstrumentAdapter
from qilib.configuration_helper.adapters.f1d_instrument_adapter import F1dInstrumentAdapter
from qilib.configuration_helper.adapters.hdawg8_instrument_adapter import ZIHDAWG8InstrumentAdapter
from qilib.configuration_helper.adapters.m2j_instrument_adapter import M2jInstrumentAdapter
from qilib.configuration_helper.adapters.s5i_instrument_adapter import S5iInstrumentAdapter

try:
    from qilib.configuration_helper.adapters.virtual_dac_instrument_adapter import VirtualDACInstrumentAdapter
except ImportError as e:
    InstrumentAdapterFactory.failed_adapters['VirtualDACInstrumentAdapter'] = e
try:
    from qilib.configuration_helper.adapters.time_stamp_instrument_adapter import TimeStampInstrumentAdapter
except ImportError as e:
    InstrumentAdapterFactory.failed_adapters['TimeStampInstrumentAdapter'] = e

from qilib.configuration_helper.adapters.uhfli_instrument_adapter import ZIUHFLIInstrumentAdapter
from qilib.configuration_helper.adapters.keysight_e8267d_instrument_adapter import KeysightE8267DInstrumentAdapter

try:
    from qilib.configuration_helper.adapters.settings_instrument_adapter import SettingsInstrumentAdapter
except ImportError as e:
    InstrumentAdapterFactory.failed_adapters['SettingsInstrumentAdapter'] = e

try:
    from qilib.configuration_helper.adapters.virtual_awg_instrument_adapter import VirtualAwgInstrumentAdapter
except ImportError as e:
    InstrumentAdapterFactory.failed_adapters['VirtualAwgInstrumentAdapter'] = e
