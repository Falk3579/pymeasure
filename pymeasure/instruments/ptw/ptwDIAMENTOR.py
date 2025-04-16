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
from pymeasure.instruments.validators import (strict_discrete_set,
                                              truncated_range)

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class ptwDIAMENTOR(Instrument):
    '''A class representing the PTW DIAMENTOR dosemeters.'''

    def __init__(self, adapter, name="PTW DIAMENTOR dosemeter",
                 timeout=20000,
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
            error_code = got.replace(';', '').strip()

            errors = {
                'E01': 'Syntax error, unknown command',
                'E04': 'Charge overflow',
                'E05': 'Max. input current exceeded.',
                'E06': 'Chamber voltage is out of range.',
                'E07': 'Parameter is write protected.',
                'E09': 'Parameter is out of range.',
                'E23': 'Error while writing/reading EEPROM',
                'E24': 'DIAMENTOR is not calibrated electrically.',
                'E25': 'Input-Buffer-Overrun',
                'E26': 'Malfunction of the firmware'
                }

            if error_code in errors.keys():
                error_text = f"{error_code}, {errors[error_code]}"
                raise ValueError(error_text)
            else:
                raise ConnectionError(f"Unknown read error. Received: {got}")

        else:
            command, sep, response = got.partition(';')  # command is removed from response
            return response.replace(';', ',')

    def check_set_errors(self):
        '''Check for errors after sending a command.'''

        try:
            self.read()
        except Exception as exc:
            log.exception("Sending a command failed.", exc_info=exc)
            raise
        else:
            return []

    def errorflags_to_text(self, flags):
        '''Convert the error flags to the error message(s).

        :param str flags:
        '''

        err_txt = ['Overload at current measurement',
                   'Overload at charge measurement',
                   'HV-Error at current measurement',
                   'HV-Error at charge measurement',
                   'Low signal at current measurement',
                   'Low signal at charge measurement',
                   'Low auto signal',
                   None,
                   'Radiation safety warning at current measurement',
                   'Radiation safety warning at charge measurement',
                   'PTW internal',
                   'Uncalibrated']

        err_msg = []
        err_code = int(flags, 0)

        for n in range(len(err_txt)):
            if err_code & (2**n):
                err_msg.append(err_txt[n])

        return err_msg

###########
# Methods #
###########


    def reset(self):
        '''Reset the dose and charge measurement values.

        .. note:: Write permission is required.
        '''
        self.ask("RES")

    def selftest(self):
        '''Execute the dosemeter selftest.

        The function returns before the end of the selftest.
        End and result of the self test have to be requested by
        the :attr:`selftest_result` property.

        .. note:: Write permission is required.
        '''
        self.ask("TST")

##############
# Properties #
##############


    id = Instrument.measurement(
        "PTW",
        '''Get the dosemeter ID.

        :type: str
        '''
        )

    serial_number = Instrument.measurement(
        "SER",
        '''Get the dosemeter serial number.

        :type: int
        ''',
        cast=int
        )
