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

from pymeasure.instruments import Instrument, Channel, SCPIMixin
from enum import IntFlag

class StatusCode(IntFlag):
    """A class representing the status codes ofd the Keithley 4200."""
    NONE = 0
    DATA_READY = 2**0
    SYNTAX_ERROR = 2**1
    B2 = 2**2
    B3 = 2**3
    BUSY = 2**4
    B5 = 2**5
    SERVICE_REQUEST = 2**6
    B7 = 2**7


class Keithley4200SMU(Channel):
    """A class representing the SMU channel."""

    def disable(self):
        """Disable the SMU channel."""
        ch = self.id
        self.write(f"US;DV{ch}")
        self.check_set_errors()


    voltage = Channel.control(
        "US;TV{ch}",
        "US;DV{ch},%d,%g,%g",  # range, value, compliance
        """Control the output voltage and current compliance (int, float, float).
        (range, value, compliance)
         
        :return: dict

        :dict keys: ``value``, ``status``

        Output voltage is in Volts and current compliance in Amps.
        The SMU uses autoranging.
        """,
        check_set_errors=True,
        get_process=lambda v: dict(value=float(v[3:]), 
                                   status=str(v[:3]),
                                   ),
        )

    current = Channel.control(
        "US;TI{ch}",
        "US;DI{ch},%d,%g,%g",  # range, value, compliance
        """Control the output current and voltage compliance (int, float, float).
        (range, value, compliance)

        :return: dict

        :dict keys: ``value``, ``status``

        Output current is in Amps and voltage compliance in Volts.
        The SMU uses autoranging.
        """,
        check_set_errors=True,
        get_process=lambda v: dict(value=float(v[3:]), 
                                   status=str(v[:3]),
                                   ),
        )


class Keithley4200(Instrument):
    """A class representing the Keithley 4200A-SCS Parameter Analyzer.
    
    The driver is only working over LAN interface.
    """

    def __init__(self, adapter,
                 name="Keithley 4200A-SCS",
                 write_termination="\0",
                 read_termination="\0",
                 **kwargs):
        super().__init__(
            adapter, 
            name,
            includeSCPI=False,
            write_termination=write_termination,
            read_termination=read_termination,
            **kwargs
        )

        self.add_smus()

    def add_smus(self):
        """Get the installed modules and add corresponding channels."""
        options = self.options

        for element in options:
            if "SMU" in element.upper():
                id = int(element[-1])
                self.add_child(Keithley4200SMU,
                               id=id,
                               prefix="smu",
                               collection="smu",
                               )

    def check_set_errors(self):
        """Check for errors after sending a command.
        
        :raise: ValueError if response is not 'ACK'
        """
        got = self.read().strip()
        expected = "ACK"
        
        if expected != got:
            raise ValueError(f"Expected '{expected}', got '{got}'")
        
        return []
        

    def clear(self):
        """Clear all data from the buffer.
        
        It also clears bit B0 (Data Ready) of the status byte.
        """
        self.write("BC")
        self.check_set_errors()

    id = Instrument.measurement(
        "ID",
        """Get the identification of the instrument (str).""",
        cast=str,
        maxsplit=0,
        )

    status = Instrument.measurement(
        "SP",
        """Get the status byte (IntFlag).""",
        get_process=lambda v: StatusCode(int(v)),
        )

    options = Instrument.measurement(
        "*OPT?",
        """Get the installed options (list of str).""",
        cast=str,
        )
