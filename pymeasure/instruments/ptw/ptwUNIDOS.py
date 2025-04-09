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


class ptwUNIDOS(Instrument):
    '''A class representing the PTW UNIDOS dosemeter.'''

    def __init__(self, adapter, name="PTW UNIDOS dosemeter",
                 timeout=5000,
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
        '''Read the response and check for errors.'''

        got = super().read()

        if got.startswith('E'):
            error_code = got.replace(';', '').strip()

            errors = {
                'E01': 'Syntax error, unknown command',
                'E02': 'Command not allowed in this context',
                'E03': 'Command not allowed at this moment',
                'E08': 'Parameter error: value invalid/out of range or \
wrong format of the parameter',
                'E12': 'Abort by user',
                'E16': 'Command to long',
                'E17': 'Maximum number of parameters exceeded',
                'E18': 'Empty parameter field',
                'E19': 'Wrong number of parameters',
                'E20': 'No user rights, no write permission',
                'E21': 'Required parameter not found (eg. detector)',
                'E24': 'Memory error: data could not be stored',
                'E28': 'Unknown parameter',
                'E29': 'Wrong parameter type',
                'E33': 'Measurement module defect',
                'E51': 'Undefined command',
                'E52': 'Wrong parameter type of the HTTP response',
                'E54': 'HTTP request denied',
                'E58': 'Wrong valueof the HTTP response',
                'E96': 'Timeout'
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

###########
# Methods #
###########

    def clear(self):
        '''Clear the complete device history.

        Write permission is required.'''
        self.ask("CHR")

    def hold(self):
        '''Set the measurment to HOLD state.

        Write permission is required.'''
        self.ask("HLD")

    def intervall(self):
        '''Execute an intervall measurement.

        Write permission is required.'''
        self.ask("INT")

    def measure(self):
        '''Start the dose or charge measurement.

        Write permission is required.'''
        self.ask("STA")

    def reset(self):
        '''Reset the dose and charge measurement values.

        Write permission is required.'''
        self.ask("RES")

    def selftest(self):
        '''Execute the electrometer selftest.

        The function returns before the end of the selftest.
        End and result of the self test have to be requested by
        the :selftest_result: property.
        Write permission is required.'''
        self.ask("AST")

    def zero(self):
        '''Execute the zero correction measurement.

        The function returns before the end of the zero correction
        measurement. End and result of the zero correction measurement
        have to be requested by the :zero_result: property.
        Write permission is required.'''
        self.ask('NUL')

##############
# Properties #
##############

    autostart_level = Instrument.control(
        "ASL", "ASL;%s",
        '''Control the threshold level of autostart measurements''',
        validator=strict_discrete_set,
        values=['LOW', 'MEDIUM', 'HIGH'],
        check_set_errors=True
        )

    id = Instrument.measurement(
        "PTW",
        '''Get the dosemeter ID.

        Name, type number, firmware version, hardware revision'''
        )

    integration_time = Instrument.control(
        "IT", "IT;%s",
        '''Control the integration time.''',
        validator=truncated_range,
        values=[1, 3599999],
        check_set_errors=True,
        cast=int
        )

    mac_address = Instrument.measurement(
        "MAC",
        '''Get the dosemeter MAC address.'''
        )

    meas_result = Instrument.measurement(
        "MV",
        '''Get the measurement results.''',
        get_process=lambda v: [v[0],  # status
                               float(str(v[1]) + str(v[2])),  # charge/dose value
                               float(str(v[5]) + str(v[6])),  # current/doserate value
                               v[9],   # timebase for doserate
                               v[10],  # measurement time
                               v[12],  # voltage
                               v[14]]  # flags
        )

    range = Instrument.control(
        "RGE", "RGE;%s",
        '''Control the measurement range.''',
        validator=strict_discrete_set,
        values=['VERY_LOW', 'LOW', 'MEDIUM', 'HIGH'],
        check_set_errors=True
        )

    range_max = Instrument.measurement(
        "MVM",
        '''Get the max value of the current measurement range.''',
        get_process=lambda v: [v[0],  # range
                               float(str(v[1]) + str(v[2])),  # current/doserate value
                               v[5]],  # timebase for doserate
        )

    range_res = Instrument.measurement(
        "MVR",
        '''Get the resolution of the current measurement range.''',
        get_process=lambda v: [v[0],  # range
                               float(str(v[1]) + str(v[2])),  # charge/dose value
                               float(str(v[5]) + str(v[6])),  # current/doserate value
                               v[9]],  # timebase for doserate
        )

    selftest_result = Instrument.measurement(
        "ASS",
        '''Get the status and result of the dosemeter selftest.

        NotYet, Passed, Failed, Aborted, Running''',
        get_process=lambda v: [v[0],  # status
                               v[1],  # remaining time
                               v[2],  # total time
                               float(str(v[4]) + str(v[5])),   # LOW result
                               float(str(v[9]) + str(v[10])),   # MEDIUM result
                               float(str(v[14]) + str(v[15]))],  # HIGH for
        )

    serial_number = Instrument.measurement(
        "SER",
        '''Get the dosemeter serial number.''',
        cast=int
        )

    status = Instrument.measurement(
        "S",
        '''Get the measurement status.'''
        )

    tfi = Instrument.measurement(
        "TFI",
        ''' Get the Telegram Failure Information.

        Information about the last failed command with HTTP request.'''
        )

    use_autostart = Instrument.control(
        "ASE", "ASE;%s",
        '''Control the measurement autostart (boolean).''',
        validator=strict_discrete_set,
        map_values=True,
        values={True: 'true', False: 'false'},
        check_set_errors=True
        )

    use_autoreset = Instrument.control(
        "ASR", "ASR;%s",
        '''Control the measurement auto reset (boolean).''',
        validator=strict_discrete_set,
        map_values=True,
        values={True: 'true', False: 'false'},
        check_set_errors=True
        )

    use_electrical_units = Instrument.control(
        "UEL", "UEL;%s",
        '''Control whether electrical units are used (boolean).''',
        validator=strict_discrete_set,
        map_values=True,
        values={True: 'true', False: 'false'},
        check_set_errors=True
        )

    voltage = Instrument.control(
        "HV", "HV;%d",
        '''Control the detector voltage in volt (-400, 400).

        The Limits of the detector are applied.''',
        validator=truncated_range,
        values=[-400, 400],
        check_set_errors=True
        )

    write_enabled = Instrument.control(
        "TOK;1", "TOK%s",
        '''Control write permission (boolean).''',
        validator=strict_discrete_set,
        values=[True, False],
        set_process=lambda v: '' if (v) else f";{int(v)}",  # 'TOK' = request write permission
                                                            # 'TOK;0' = release write permision
                                                            # 'TOK;1' = get status
        get_process=lambda v: True if (v[1] == 'true') else False,
        check_set_errors=True
        )

    zero_result = Instrument.measurement(
        "NUS",
        '''Get status and result of the zero correction measurement.

        status, time remaining, total time ~82sec
        NotYet, Passed, Failed, Aborted, Running''',
        )
