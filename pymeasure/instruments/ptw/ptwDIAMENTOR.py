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


import logging

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import truncated_range

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class ptwDIAMENTOR(Instrument):
    '''A class representing the PTW DIAMENTOR DAP dosemeters.'''

    def __init__(self, adapter, name="PTW DIAMENTOR dosemeter",
                 timeout=2000,
                 read_termination='\r\n',
                 encoding='utf8',
                 **kwargs):
        super().__init__(
            adapter,
            name,
            read_termination=read_termination,
            includeSCPI=False,
            timeout=timeout,
            encoding=encoding,
            **kwargs
        )

    def read(self):
        '''Overwrites the :meth:`Instrument.read <pymeasure.instruments.Instrument.read>` to
        replace semicolon by comma and check the response for errors.
        '''

        got = super().read()

        if got.startswith('E'):

            errors = {
                'E1': 'Syntax error, unknown command',
                'E4': 'Charge overflow',
                'E5': 'Max. input current exceeded.',
                'E6': 'Chamber voltage is out of range.',
                'E7': 'Parameter is write protected.',
                'E9': 'Parameter is out of range.',
                'E23': 'EEPROM reading/writing error',
                'E24': 'DIAMENTOR is not calibrated electrically.',
                'E25': 'Input-Buffer-Overrun',
                'E26': 'Firmware malfunction'
                }

            if got in errors.keys():
                error_text = f"{got}, {errors[got]}"
                raise ValueError(error_text)
            else:
                raise ConnectionError(f"Unknown read error. Received: {got}")

        else:
            return got

    def check_set_errors(self):
        '''Check for errors after sending a command.'''

        try:
            self.read()
        except Exception as exc:
            log.exception("Sending a command failed.", exc_info=exc)
            raise
        else:
            return []

###########
# Methods #
###########

    def reset(self):
        '''Reset the dose and charge measurement values.
        '''
        self.ask("RES")

    def selftest(self):
        '''Execute the DIAMENTOR selftest.

        The function returns before the end of the selftest.
        End and result of the self test have to be requested by
        the :attr:`selftest_result` property.
        '''
        self.ask("TST")

##############
# Properties #
##############

    pressure = Instrument.control(
        "PRE", "PRE%04d",
        '''Control the atmospheric pressure in hPa.

        :type: int, strictly from ``500`` to ``1500``

        It is used for the air density correction.
        ''',
        validator=truncated_range,
        values=[500, 1500],
        check_set_errors=True,
        get_process=lambda v: int(v[3:])
        )

    id = Instrument.measurement(
        "PTW",
        '''Get the DIAMENTOR firmware version.

        :type: str
        '''
        )

    meas_result = Instrument.measurement(
        "M",
        '''Get the measurement results of dose-area-product (DAP) and
        dose-area-product rate.

        :type: dict

        :dict keys: ``dap``,
                    ``dap_rate``,
                    ``time``,
                    ``crc``

        The units of dap and dap_rate depend on property U
        Time is in seconds.
        ''',
        get_process=lambda v: {'dap': v[0][1:],
                               'dap_rate': v[1],
                               'time': 60*int(v[2]) + int(v[3]),
                               'crc': v[8]
                               }
        )

    serial_number = Instrument.measurement(
        "SER",
        '''Get the DIAMENTOR serial number.

        :type: int
        ''',
        get_process=lambda v: int(v[3:])
        )

    temperature = Instrument.control(
        "TMPA", "TMPA%02d",
        '''Control the DIAMENTOR chamber temperature in degC.

        :type: int, strictly from ``0`` to ``70``

        It is used for the air density correction.
        ''',
        validator=truncated_range,
        values=[0, 70],
        check_set_errors=True,
        get_process=lambda v: int(v[4:])
        )

    dap_unit = Instrument.control(
        "U", "U%d",
        '''Control the DAP unit.

        :type: int, strictly from ``1`` to ``4``

            - ``1``: cGycm²
            - ``2``: Gycm²
            - ``3``: µGym²
            - ``4``: Rcm²
        ''',
        validator=truncated_range,
        values=[1, 4],
        check_set_errors=True,
        get_process=lambda v: int(v[1:])
        )
