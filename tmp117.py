# SPDX-FileCopyrightText: Copyright (c) 2020 Bryan Siepert for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2023 Jose D. Montoya
#
# SPDX-License-Identifier: MIT
"""
`tmp117`
================================================================================

CircuitPython library for the TI TMP117 Temperature sensor

* Author(s): Bryan Siepert, Ian Grant, Jose D. Montoya

parts based on SparkFun_TMP117_Arduino_Library by Madison Chodikov @ SparkFun Electronics:
https://github.com/sparkfunX/Qwiic_TMP117
https://github.com/sparkfun/SparkFun_TMP117_Arduino_Library

Serial number register information:
https://e2e.ti.com/support/sensors/f/1023/t/815716?TMP117-Reading-Serial-Number-from-EEPROM

Implementation Notes
--------------------

**Hardware:**

* `Adafruit TMP117 ±0.1°C High Accuracy I2C Temperature Sensor
  <https://www.adafruit.com/product/4821>`_ (Product ID: 4821)

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://circuitpython.org/downloads

* Adafruit's Bus Device library:
  https://github.com/adafruit/Adafruit_CircuitPython_BusDevice

* Adafruit's Register library:
  https://github.com/adafruit/Adafruit_CircuitPython_Register

"""

import time
from collections import namedtuple
from micropython import const
from adafruit_bus_device import i2c_device
from adafruit_register.i2c_struct import ROUnaryStruct, UnaryStruct

from adafruit_register.i2c_bit import RWBit, ROBit
from adafruit_register.i2c_bits import RWBits, ROBits

try:
    from typing import Tuple
    from busio import I2C
    from typing_extensions import Literal
except ImportError:
    pass

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/jposada202020/CircuitPython_TMP117.git"

_I2C_ADDR = 0x48  # default I2C Address
_TEMP_RESULT = const(0x00)
_CONFIGURATION = const(0x01)
_T_HIGH_LIMIT = const(0x02)
_T_LOW_LIMIT = const(0x03)
_EEPROM_UL = const(0x04)
_EEPROM1 = const(0x05)
_EEPROM2 = const(0x06)
_TEMP_OFFSET = const(0x07)
_EEPROM3 = const(0x08)
_DEVICE_ID = const(0x0F)
_DEVICE_ID_VALUE = 0x0117
_TMP117_RESOLUTION = (
    0.0078125  # Resolution of the device, found on (page 1 of datasheet)
)

_CONTINUOUS_CONVERSION_MODE = const(0b00)  # Continuous Conversion Mode
_ONE_SHOT_MODE = const(0b11)  # One Shot Conversion Mode
_SHUTDOWN_MODE = const(0b01)  # Shutdown Conversion Mode

ALERT_WINDOW = const(0)
ALERT_HYSTERESIS = const(1)

AVERAGE_1X = const(0b00)
AVERAGE_8X = const(0b01)
AVERAGE_32X = const(0b10)
AVERAGE_64X = const(0b11)
averaged_measurements_values = (AVERAGE_1X, AVERAGE_8X, AVERAGE_32X, AVERAGE_64X)

DELAY_0_0015_S = const(0b000)  # 0.00155
DELAY_0_125_S = const(0b01)  # 0.125
DELAY_0_250_S = const(0b010)  # 0.250
DELAY_0_500_S = const(0b011)  # 0.500
DELAY_1_S = const(0b100)  # 1
DELAY_4_S = const(0b101)  # 4
DELAY_8_S = const(0b110)  # 8
DELAY_16_S = const(0b111)  # 16

CONTINUOUS_CONVERSION_MODE = const(0b00)  # Continuous Conversion Mode
ONE_SHOT_MODE = const(0b11)  # One Shot Conversion Mode
SHUTDOWN_MODE = const(0b01)  # Shutdown Conversion Mode

AlertStatus = namedtuple("AlertStatus", ["high_alert", "low_alert"])


class TMP117:
    """Library for the TI TMP117 high-accuracy temperature sensor"""

    _part_id = ROUnaryStruct(_DEVICE_ID, ">H")
    _raw_temperature = ROUnaryStruct(_TEMP_RESULT, ">h")
    _raw_high_limit = UnaryStruct(_T_HIGH_LIMIT, ">h")
    _raw_low_limit = UnaryStruct(_T_LOW_LIMIT, ">h")
    _raw_temperature_offset = UnaryStruct(_TEMP_OFFSET, ">h")

    # these three bits will clear on read in some configurations, so we read them together
    _alert_status_data_ready = ROBits(3, _CONFIGURATION, 13, 2, False)
    _eeprom_busy = ROBit(_CONFIGURATION, 12, 2, False)
    _mode = RWBits(2, _CONFIGURATION, 10, 2, False)

    _raw_measurement_delay = RWBits(3, _CONFIGURATION, 7, 2, False)
    _raw_averaged_measurements = RWBits(2, _CONFIGURATION, 5, 2, False)

    _data_ready = RWBit(_CONFIGURATION, 13, 2, False)

    _raw_alert_mode = RWBit(_CONFIGURATION, 4, 2, False)  # T/nA bits in the datasheet
    _int_active_high = RWBit(_CONFIGURATION, 3, 2, False)
    _data_ready_int_en = RWBit(_CONFIGURATION, 2, 2, False)
    _soft_reset = RWBit(_CONFIGURATION, 1, 2, False)

    _avg_3 = {0: 1, 1: 1, 2: 1, 3: 1, 4: 1, 5: 4, 6: 8, 7: 16}
    _avg_2 = {0: 0.5, 1: 0.5, 2: 0.5, 3: 0.5, 4: 1, 5: 4, 6: 8, 7: 16}
    _avg_1 = {0: 0.125, 1: 0.125, 2: 0.25, 3: 0.5, 4: 1, 5: 4, 6: 8, 7: 16}
    _avg_0 = {0: 0.0155, 1: 0.125, 2: 0.25, 3: 0.5, 4: 1, 5: 4, 6: 8, 7: 16}
    _averaging_modes = {0: _avg_0, 1: _avg_1, 2: _avg_2, 3: _avg_3}

    def __init__(self, i2c_bus: I2C, address: int = _I2C_ADDR) -> None:
        self.i2c_device = i2c_device.I2CDevice(i2c_bus, address)
        if self._part_id != _DEVICE_ID_VALUE:
            raise AttributeError("Cannot find a TMP117")
        self._soft_reset = True
        # Following a reset, the temperature register reads –256 °C until the first
        # conversion, including averaging, is complete. So we sleep for that amount of time
        time.sleep(
            self._averaging_modes[self._raw_averaged_measurements][
                self._raw_measurement_delay
            ]
        )
        self._mode = CONTINUOUS_CONVERSION_MODE
        while not self._data_ready:
            time.sleep(0.001)
        _ = self._raw_temperature * _TMP117_RESOLUTION

    @property
    def temperature(self) -> float:
        """The current measured temperature in Celsius"""

        return self._raw_temperature * _TMP117_RESOLUTION

    @property
    def temperature_offset(self) -> float:
        """User defined temperature offset to be added to measurements from `temperature`
        In order the see the new change in the temperature we need for the data to be ready.
        There is a time delay calculated according to current configuration.

        .. code-block::python

            import time
            import board
            import tmp117

            i2c = board.I2C()  # uses board.SCL and board.SDA

            tmp117 = tmp117.TMP117(i2c)

            print("Temperature without offset: %.2f degrees C" % tmp117.temperature)
            tmp117.temperature_offset = 10.0
            while True:
                print("Temperature w/ offset: %.2f degrees C" % tmp117.temperature)
                time.sleep(1)

        """
        return self._raw_temperature_offset * _TMP117_RESOLUTION

    @temperature_offset.setter
    def temperature_offset(self, value: float) -> None:
        self._raw_temperature_offset = self._scaled_limit(value)

    @property
    def high_limit(self) -> float:
        """The high temperature limit in Celsius. When the measured temperature exceeds this
        value, the `high_alert` attribute of the `alert_status` property will be True.
        """

        return self._raw_high_limit * _TMP117_RESOLUTION

    @high_limit.setter
    def high_limit(self, value: float) -> None:
        self._raw_high_limit = self._scaled_limit(value)

    @property
    def low_limit(self) -> float:
        """The low  temperature limit in Celsius. When the measured temperature goes below
        this value, the `low_alert` attribute of the `alert_status` property will be True.
        """

        return self._raw_low_limit * _TMP117_RESOLUTION

    @low_limit.setter
    def low_limit(self, value: float) -> None:
        self._raw_low_limit = self._scaled_limit(value)

    @property
    def alert_status(self):
        """The current triggered status of the high and low temperature alerts as a AlertStatus
        named tuple with attributes for the triggered status of each alert.

        .. code-block :: python

            import board
            import tmp117
            i2c = board.I2C()  # uses board.SCL and board.SDA

            tmp117 = tmp117.TMP117(i2c)

            tmp117.high_limit = 25
            tmp117.low_limit = 10

            print("High limit", tmp117.high_limit)
            print("Low limit", tmp117.low_limit)

            # Try changing `alert_mode`  to see how it modifies the behavior of the alerts.
            # tmp117.alert_mode = tmp117.ALERT_WINDOW  #default
            # tmp117.alert_mode = tmp117.HYSTERESIS

            print("Alert mode:", tmp117.alert_mode)
            print("")
            print("")
            while True:
                print("Temperature: %.2f degrees C" % tmp117.temperature)
                alert_status = tmp117.alert_status
                print("High alert:", alert_status.high_alert)
                print("Low alert:", alert_status.low_alert)
                print("")
                time.sleep(1)

        """
        high_alert, low_alert, *_ = self._read_status()
        return AlertStatus(high_alert=high_alert, low_alert=low_alert)

    @property
    def averaged_measurements(self):
        """
        Users can configure the device to report the average of multiple temperature
        conversions with the AVG[1:0] bits to reduce noise in the conversion results.
        When the TMP117 is configured to perform averaging with AVG set to 01, the device executes
        the configured number of conversions to eight. The device accumulates those conversion
        results and reports the average of all the collected results at the end of the process.

        +----------------------------------------+-------------------------+
        | Mode                                   | Value                   |
        +========================================+=========================+
        | :py:const:`tmp117.AVERAGE_1X`          | :py:const:`0b00`        |
        +----------------------------------------+-------------------------+
        | :py:const:`tmp117.AVERAGE_8X`          | :py:const:`0b01`        |
        +----------------------------------------+-------------------------+
        | :py:const:`tmp117.AVERAGE_32X`         | :py:const:`0b10`        |
        +----------------------------------------+-------------------------+
        | :py:const:`tmp117.AVERAGE_64X`         | :py:const:`0b11`        |
        +----------------------------------------+-------------------------+

        .. code-block::python3

            import time
            import board
            import tmp117

            i2c = board.I2C()  # uses board.SCL and board.SDA

            tmp117 = tmp117.TMP117(i2c)

            print("Number of averaged samples per measurement:",
                tmp117.averaged_measurements
            )


        """
        average_measure = ("AVERAGE_1X", "AVERAGE_8X", "AVERAGE_32X", "AVERAGE_64X")

        return average_measure[self._raw_averaged_measurements]

    @averaged_measurements.setter
    def averaged_measurements(self, value: int):
        if value not in (0, 1, 2, 3):
            raise ValueError("averaged_measurements must be set to 0, 1, 2 or 3")
        self._raw_averaged_measurements = value

    @property
    def measurement_mode(self):
        # pylint: disable=line-too-long
        """Sets the measurement mode, specifying the behavior of how often measurements are taken.
                `measurement_mode` must be one of:

        When we use the sensor in One shot mode, the sensor will take the average_measurement value
        into account. However, this measure is done with the formula (15.5 ms × average_time), so in
        normal operation average_time will be 8, therefore time for measure is 124 ms.
        (See datasheet. 7.3.2 Averaging for more information). If we use 64, time will be 15.5 x 65 = 992 ms,
        the standby time will decrease, but the measure is still under 1 Hz cycle.
        (See Fig 7.2 on the datasheet)

        +-----------------------------------------------+------------------------------------------------------+
        | Mode                                          | Behavior                                             |
        +===============================================+======================================================+
        | :py:const:`tmp117.CONTINUOUS_CONVERSION_MODE` | Measurements are made at the interval determined by  |
        |                                               | averaging_measurements.                              |
        |                                               | `temperature` returns the most recent measurement    |
        +-----------------------------------------------+------------------------------------------------------+
        | :py:const:`tmp117.ONE_SHOT`                   | Take a single measurement with the current number of |
        |                                               | averaging_measurements and switch to                 |
        |                                               | :py:const:`SHUTDOWN` when finished.                  |
        |                                               | `temperature` will return the new measurement until  |
        |                                               | `measurement_mode` is set to :py:const:`CONTINUOUS`  |
        |                                               | or :py:const:`ONE_SHOT` is  set again.               |
        +-----------------------------------------------+------------------------------------------------------+
        | :py:const:`tmp117.SHUTDOWN`                   | The sensor is put into a low power state and no new  |
        |                                               | measurements are taken.                              |
        |                                               | `temperature` will return the last measurement until |
        |                                               | a new `measurement_mode` is selected.                |
        +-----------------------------------------------+------------------------------------------------------+

        """
        # pylint: enable=line-too-long
        sensor_modes = {
            0: "CONTINUOUS_CONVERSION_MODE",
            1: "SHUTDOWN_MODE",
            3: "ONE_SHOT_MODE",
        }
        return sensor_modes[self._mode]

    @measurement_mode.setter
    def measurement_mode(self, value: int) -> None:
        self._mode = value

    @property
    def measurement_delay(self):
        """The minimum amount of time between measurements in seconds.
        The specified amount may be exceeded depending on the
        current setting off `averaged_measurements` which determines the minimum
        time needed between reported measurements.


        +-----------------------------------+-------------------+
        | Mode                              | Value             |
        +===================================+===================+
        | :py:const:`tmp117.DELAY_0_0015_S` | :py:const:`0b000` |
        +-----------------------------------+-------------------+
        | :py:const:`tmp117.DELAY_0_125_S`  | :py:const:`0b01`  |
        +-----------------------------------+-------------------+
        | :py:const:`tmp117.DELAY_0_250_S`  | :py:const:`0b010` |
        +-----------------------------------+-------------------+
        | :py:const:`tmp117.DELAY_0_500_S`  | :py:const:`0b011` |
        +-----------------------------------+-------------------+
        | :py:const:`tmp117.DELAY_1_S`      | :py:const:`0b100` |
        +-----------------------------------+-------------------+
        | :py:const:`tmp117.DELAY_4_S`      | :py:const:`0b101` |
        +-----------------------------------+-------------------+
        | :py:const:`tmp117.DELAY_8_S`      | :py:const:`0b110` |
        +-----------------------------------+-------------------+
        | :py:const:`tmp117.DELAY_16_S`     | :py:const:`0b111` |
        +-----------------------------------+-------------------+

        .. code-block::python

            import time
            import board
            import tmp117

            ii2c = board.I2C()  # uses board.SCL and board.SDA

            tmp117 = mp117.TMP117(i2c)

        In order to print information in a nicer way, we create a dictionary with the
        sensor information for the measurement delay.

        .. code-block::python3

            Delay_times = {
                0: "DELAY_0_0015_S",
                1: "DELAY_0_125_S",
                2: "DELAY_0_250_S",
                3: "DELAY_0_500_S",
                4: "DELAY_1_S",
                5: "DELAY_4_S",
                6: "DELAY_8_S",
                7: "DELAY_16_S",
            }

        We print the information for the Temperature sensor

        .. code-block::python3

            # uncomment different options below to see how it affects the reported temperature

            print("Minimum time between measurements:",
            Delay_times[tmp117.measurement_delay])

        """

        return self._raw_measurement_delay

    @measurement_delay.setter
    def measurement_delay(self, value: int) -> None:
        if value not in (0, 1, 2, 3, 4, 5, 6, 7):
            raise ValueError(
                "averaged_measurements must be set to 0, 1, 2, 3, 4, 5, 6, 7"
            )
        self._raw_measurement_delay = value

    def take_single_measurement(self) -> float:
        """Perform a single measurement cycle respecting the value of `averaged_measurements`,
        returning the measurement once complete. Once finished the sensor is placed into a low power
        state until :py:meth:`take_single_measurement` or `temperature` are read.

        **Note:** if `averaged_measurements` is set to a high value there will be a notable
        delay before the temperature measurement is returned while the sensor takes the required
        number of measurements
        """

        return self._set_mode_and_wait_for_measurement(_ONE_SHOT_MODE)  # one shot

    @property
    def alert_mode(self) -> Literal[ALERT_WINDOW, ALERT_HYSTERESIS]:
        """Sets the behavior of the `low_limit`, `high_limit`, and `alert_status` properties.

        When set to :py:const:`ALERT_WINDOW`, the `high_limit` property will unset when the
        measured temperature goes below `high_limit`. Similarly `low_limit` will be True or False
        depending on if the measured temperature is below (`False`) or above(`True`) `low_limit`.

        When set to :py:const:`ALERT_HYSTERESIS`, the `high_limit` property will be set to
        `False` when the measured temperature goes below `low_limit`. In this mode, the `low_limit`
        property of `alert_status` will not be set.

        The default is :py:const:`ALERT_WINDOW`

        +----------------------------------------+-------------------------+
        | Mode                                   | Value                   |
        +========================================+=========================+
        | :py:const:`tmp117.ALERT_WINDOW`        | :py:const:`0b0`         |
        +----------------------------------------+-------------------------+
        | :py:const:`tmp117.ALERT_HYSTERESIS`    | :py:const:`0b1`         |
        +----------------------------------------+-------------------------+


        """

        alert_modes = ("ALERT_WINDOW", "ALERT_HYSTERESIS")

        return alert_modes[self._raw_alert_mode]

    @alert_mode.setter
    def alert_mode(self, value: Literal[ALERT_WINDOW, ALERT_HYSTERESIS]):
        """The alert_mode of the sensor

        Could have the following values:

        * ALERT_WINDOW
        * ALERT_HYSTERESIS

        """
        if value not in [0, 1]:
            raise ValueError("alert_mode must be set to 0 or 1")
        self._raw_alert_mode = value

    @property
    def serial_number(self):
        """A 48-bit, factory-set unique identifier for the device."""
        eeprom1_data = bytearray(2)
        eeprom2_data = bytearray(2)
        eeprom3_data = bytearray(2)
        # Fetch EEPROM registers
        with self.i2c_device as i2c:
            i2c.write_then_readinto(bytearray([_EEPROM1]), eeprom1_data)
            i2c.write_then_readinto(bytearray([_EEPROM2]), eeprom2_data)
            i2c.write_then_readinto(bytearray([_EEPROM3]), eeprom3_data)
        # Combine the 2-byte portions
        combined_id = bytearray(
            [
                eeprom1_data[0],
                eeprom1_data[1],
                eeprom2_data[0],
                eeprom2_data[1],
                eeprom3_data[0],
                eeprom3_data[1],
            ]
        )
        # Convert to an integer
        return combined_id

    def _set_mode_and_wait_for_measurement(self, mode: int) -> float:
        self._mode = mode
        # poll for data ready
        while not self._read_status()[2]:
            time.sleep(0.001)

        return self._raw_temperature * _TMP117_RESOLUTION

    # eeprom write enable to set defaults for limits and config
    # requires context manager or something to perform a general call reset

    def _read_status(self) -> Tuple[int, int, int]:
        # 3 bits: high_alert, low_alert, data_ready
        status_flags = self._alert_status_data_ready

        high_alert = 0b100 & status_flags > 0
        low_alert = 0b010 & status_flags > 0
        data_ready = 0b001 & status_flags > 0

        return (high_alert, low_alert, data_ready)

    # pylint: disable=no-self-use
    @staticmethod
    def _scaled_limit(value: float) -> int:
        """Validates for values to be in the range of :const:`-256` and :const:`255`,
        then return the value divided by the :const:`_TMP117_RESOLUTION`
        """

        if value not in range(-256, 255):
            raise ValueError("value must be from 255 to -256")
        return int(value / _TMP117_RESOLUTION)
