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

# https://github.com/wholden/SpellmanUSB
# https://www.spellmanhv.com/en/high-voltage-power-supplies/XRV

class SpellmanHV(Instrument):
    """
    A class representing the Spellmann high voltage power supply.
    """

    def __init__(self, adapter, name="Spellman HV Power Supply", **kwargs):
        super().__init__(
            adapter, name,
            **kwargs
        )

    baudrate = Instruement.control(
        "GetCommand",
        "SetCommend",
        """Control the baud rate.

        Command code: 07
        """,

    voltage = Instrument.control(
        "GetCommand",
        "SetCommend",
        """Control the voltage in Volts.

        Command code: 10
        """,
        )

    current = Instruement.control(
        "GetCommand",
        "SetCommend",
        """Control current in 

        Command code: 11
        """,
        )

# Data Byte section of the TCP/IP Datagram
# CommandName  CommandCode ArgumentLength

# Program RS232 unit baud rate 07  1

# Program kV  10  1
# Program mA  11  1

# Program Filament Limit 12  1
# Program Filament PreHeat 13  1

# Request kV Set point  14  None
# Request mA Set point  15  None



# Request Filament Limit Set point 16  None
# Request Filament PreHeat Set point 17  None
# Request Analog Monitor Read backs 19  None
# Request HV On  Hours Counter 21  None
# Request Status  22  None
# Request Software Version 23  None
# Request Model Number 26  None
# Request User Configuration 27  None
# Request Scaling  28  None
# Reset HV On Hours Counter 30  None
# Reset Faults  31  None
# Set Large/Small Filament 32  1
# Request Power Limits  38  None
# Request FPGA Rev  43  None
# Request kV monitor  60  None
# Request  –15V LVPS  65  None
# Request Faults  68  None
# Request System Voltages 69  None
# Filament Enable  70  1
# XRV Controller  71  1
# Program Power Limit  97  2
# Program HV On  98  1
# Local/Remote Mode  99  1






# ResponseName  CommandCode ArgumentLength
# Request kV Set point  14  1
# Request mA Set point  15  1
# Request Filament Limit Set point 16  1
# Request Filament PreHeat Set point 17  1
# Request Analog Monitor Read backs 19  8
# Request Total Hours High Voltage On 21  1
# Request Status  22   17
# Request DSP Software Version 23  1
# Request Model number  26  1
# Request User Configuration  27  12
# Request Scaling   28  3
# Request Power Limits  38  6
# Request FPGA Revision and Build number 43  2
# Request kV monitor  60  1
# Request –15V LVPS  65  1
# Request Faults  68  27
# Request System Voltages  69  10
