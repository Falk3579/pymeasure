#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2025 PyMeasure Developers
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set, strict_range
from enum import IntFlag

# https://www.spellmanhv.com/en/high-voltage-power-supplies/XRV


class StatusCode(IntFlag):
    HV_ENABLED = 1
    INTERLOCK_1_CLOSED = 2
    INTERLOCK_2_CLOSED = 4
    ECR_Mode_Active = 8
    POWER_SUPPLY_FAULT = 16
    LOCAL_MODE = 32
    FILAMENT_ENABLED = 64
    LARGE_FILAMENT = 128
    XRAYS_EMINENT = 256
    LARGE_FILAMENT_CONFIRMATION = 512
    SMALL_FILAMENT_CONFIRMATION = 1024
    RESERVED1 = 2048
    RESERVED2 = 4096
    RESERVED3 = 8192
    RESERVED4 = 16384
    POWER_SUPPLY_READY = 32768
    INTERNAL_INTERLOCK_CLOSED = 65536


class SpellmanXRV(Instrument):
    """A class representing the Spellmann high voltage power supply."""

    STX = "\x02"
    ETX = "\x03"

    def __init__(self, adapter,
                 name="Spellman HV Power Supply",
                 query_delay=0.15,
                 **kwargs):
        super().__init__(
            adapter, name,
            includeSCPI=False,
            **kwargs)

        self.query_delay = query_delay

        self.calculate_scaling_factors(self.max_voltage, self.max_current)

    def checksum(self, string):
        """Calculate the checksum.

        The checksum is computed as follows:
        - Add all the bytes before <CSUM>, except <STX>, into a 16 bit (or larger) word.
          The bytes are added as unsigned integers.
        - Take the two’s complement.
        - Truncate the result down to the eight least significant bits.
        - Clear the most significant bit (bit 7) of the resultant byte, (bitwise AND with
          0x7F).
        - Set the next most significant bit (bit 6) of the resultant byte (bitwise OR with
          0x40).

        Using this method, the checksum is always a number between 0x40 and 0x7F.  The
        checksum can never be confused with the <STX> or <ETX> control characters, since
        these have non overlapping ASCII values.
        """

        ascii_sum = 0
        for char in string:
            ascii_sum += ord(char)  # add ascii values together

        csb1 = 0x100 - ascii_sum  # two's complement
        csb2 = 0x7F & csb1  # bitwise AND 0x7F: truncate to the last 7 bits
        csb3 = 0x40 | csb2  # bitwise OR 0x40: set bit 6

        return csb3

    def write(self, command):
        """Add STX in front and CRC + ETX at end of every command before sending it."""

        command_with_comma = command + ","
        csum = self.checksum(command_with_comma)
        super().write(f"{self.STX}{command_with_comma}{csum},{self.ETX}")

    def wait_for(self, query_delay=0):
        """Wait for some time.

        :param query_delay: override the global query_delay.
        """
        super().wait_for(query_delay or self.query_delay)

    def read(self):
        """Read from the device and check for errors.

        Assert that the response starts with <STX> and ends with <ETX>.
        Assert the checksum.
        """
        got = super().read()

        begin_ok = got.startswith(self.STX)
        if not begin_ok:
            raise ConnectionError("Expected <STX>  at begin of received message.")

        end_ok = got.endswith(self.ETX)
        if not end_ok:
            raise ConnectionError("Expected <ETX> at end of received message.")

        # remove <STX> and <ETX> and split to list
        response = got.strip(self.STX).strip(self.ETX).split(",")

        got_checksum = response[-1]  # last element
        calculated_checksum = self.checksum(response[:-1])

        if got_checksum is not calculated_checksum:
            string = f"Checksum error: expected '{calculated_checksum}', got '{got_checksum}'."
            raise ConnectionError(string)

        return response[1:-1]  # without command and checksum


    status = Instrument.measurement(
        "22",
        """Get the power supply status (enum).""",
        get_process_list=lambda v: StatusCode(v)
        )

    baudrate = Instrument.setting(
        "07,%d",
        """Set the baud rate.

        :type: int, strictly in ``9600``, ``19200``, ``38400``, ``57600``, ``115200``
        """,
        validator=strict_discrete_set,
        map_values=True,
        values={9600: 1,
                19200: 2,
                38400: 3,
                57600: 4,
                115200: 5},
        )

    max_voltage = Instrument.measurement(
        "28",
        """Get the maximum voltage in Volts (int).""",
        get_process_list=lambda v: 1000*int(v[0]),
        )

    max_current = Instrument.measurement(
        "28",
        """Get the maximum current in A (float).""",
        get_process_list=lambda v: 1e-3*int(v[1]),
        )

    def calculate_scaling_factors(self, max_voltage, max_current):
        """Calculate the scaling factors for DAC and A/D feedback."""

        # scaling for DAC
        dac_scaling_factor_voltage = max_voltage/4095  # volts/bit
        dac_scaling_factor_current = max_current/4095  # mA/bit

        # Scaling for ADC, ADC has 20% overrange
        adc_scaling_factor_voltage = 1.2*max_voltage/4095  # volts/bit
        adc_scaling_factor_current = 1.2*max_current/4095  # mA/bit
        adc_scaling_factor_power = max_voltage*max_current/4095  # watts/bit

    voltage = Instrument.control(
        "14",
        "10,%d",
        """Control the voltage in Volts (int).""",
        validator=strict_range,
        values=[0, 1],
        set_process=lambda v: int(v/dac_scaling_factor_voltage),
        get_process=lambda v: int(v*46.88),
        dynamic=True,
        )

    current = Instrument.control(
        "15",
        "11,%d",
        """Control current in A (float).

        get 15
        set 11
        """,
        validator=strict_range,
        values=[0, 1e-3],
        set_process=lambda v: int(v/dac_scaling_factor_voltage),
        get_process=lambda v: int(v*46.88),
        dynamic=True,
        )

# Data Byte section of the TCP/IP Datagram
# CommandName  CommandCode ArgumentLength

# Program RS232 unit baud rate 07  1

# Program kV  10  1
# Request kV Set point  14  None

# Program mA  11  1
# Request mA Set point  15  None

# Program Filament Limit 12  1
# Request Filament Limit Set point 16  None

# Program Filament PreHeat 13  1
# Request Filament PreHeat Set point 17  None


# Request Analog Monitor Read backs 19  None
# Request HV On  Hours Counter 21  None

# Request Status  22  None

# Request Software Version 23  None
# Request Model Number 26  None
# Request User Configuration 27  None
# Request Scaling  28  None

# Reset HV On Hours Counter 30  None
# Reset Faults  31  None

# Set Large/Small Filament 32  1
# Request Power Limits  38  None

# Request FPGA Rev  43  None
# Request kV monitor  60  None
# Request  –15V LVPS  65  None
# Request Faults  68  None

# Request System Voltages 69  None
# Filament Enable  70  1
# XRV Controller  71  1

# Program Power Limit  97  2
# Program HV On  98  1

# Local/Remote Mode  99  1

# ResponseName  CommandCode ArgumentLength
# Request kV Set point  14  1
# Request mA Set point  15  1
# Request Filament Limit Set point 16  1
# Request Filament PreHeat Set point 17  1
# Request Analog Monitor Read backs 19  8
# Request Total Hours High Voltage On 21  1
# Request Status  22   17
# Request DSP Software Version 23  1
# Request Model number  26  1
# Request User Configuration  27  12
# Request Scaling   28  3
# Request Power Limits  38  6
# Request FPGA Revision and Build number 43  2
# Request kV monitor  60  1
# Request –15V LVPS  65  1
# Request Faults  68  27
# Request System Voltages  69  10
