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
                 timeout=2500,
                 read_termination='\r\n',
                 **kwargs):
        super().__init__(
            adapter,
            name,
            timeout=timeout,
            includeSCPI=False,
            read_termination=read_termination,
            **kwargs
        )

    def read(self):
        '''Read the response and check for errors.

        The command is stripped from the response.'''

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
                error_text = f"{error_code}: {errors[error_code]}"
                raise ValueError(error_text)
            else:
                raise ConnectionError(f"Unknown read error. Received: {got}")

        else:
            command, sep, response = got.partition(';')
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


#################
# ID and status #
#################

    id = Instrument.measurement(
        "PTW",
        '''Get the dosemeter ID.'''
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

    mac_address = Instrument.measurement(
        "MAC",
        '''Get the dosemeter MAC address.'''
        )

    tfi = Instrument.measurement(
        "TFI",
        ''' Get the Telegram Failure Information.

        Information about the last failed command with HTTP request.'''
        )

##################################
# Write premission               #
# TOK request write permission   #
# TOK;1 check write permission   #
# TOK;0 release write permission #
##################################

    def write_enable(self):
        pass

    write_enabled = Instrument.control(
        "TOK", "TOK;1",
        '''Control the write access (boolean).''',
        # validator=strict_discrete_set,
        # map_values=True,
        # values={True: 1, False: 0}
        )

###################
# Device settings #
###################

    use_electrical_units = Instrument.control(
        "UEL", "UEL:%s",
        '''Control if electrical units are used (boolean).''',
        validator=strict_discrete_set,
        map_values=True,
        values={True: 'true', False: 'false'}
        )

    range = Instrument.control(
        "RGE", "RGE;%s",
        '''Control the measurement range.''',
        validator=strict_discrete_set,
        values=['VERY_LOW', 'LOW', 'MEDIUM', 'HIGH']
        )

    voltage = Instrument.control(
        "HV", "HV;%d",
        '''HV Aktuelle Hochspannung abfragen/setzen
        Hier werden die Limits des Detektor-Eintrages angewendet. ''',
        validator=truncated_range,
        values=[100, 500]
        )

    integration_time = Instrument.control(
        "IT", "IT;%s",
        '''IT Integrationszeit abfragen/setzen'''
        )

    use_autostart = Instrument.control(
        "ASE", "ASE;%d",
        '''ASE Autostart abfragen/setzen    (boolean)'''
        )

    use_autoreset = Instrument.control(
        "ASR", "ASR",
        '''ASR Autoreset abfragen/setzen    (boolean)'''
        )

    autostart_level = Instrument.control(
        "ASL", "ASL",
        '''ASL Schwelle für Autostart-Messung abfrage/setzen''',
        validator=strict_discrete_set,
        values=['LOW', 'MEDIUM', 'HIGH']
        )

    def clear_history(self):
        Instrument.setting(
            "CHR",
            '''Clear the complete device history.''',
            check_set_errors=True
            )

###########################
# Measurement and Control #
###########################

    def meas(self):
        Instrument.setting(
            "STA",
            '''Start the dose or charge measurement''',
            check_set_errors=True
            )

    def hold(self):
        Instrument.setting(
            "HLD",
            '''Set the measurment to HOLD state''',
            check_set_errors=True
            )

    def reset(self):
        Instrument.setting(
            "RES",
            '''RES Dosis- oder Ladungsmessung und
            Rücksetzen der Messwerte beenden        ''',
            check_set_errors=True
            )

    def intervall(self):
        '''INT Intervallmessung starten            '''
        self.write("INT")

    def zero(self):
        Instrument.setting(
            'NUL',
            '''NUL Nullabgleich starten
            Antwort wird vor Beendigung der Aktion gesendet.
            Abgleichsende und -resultat muss mit NUS abgefragt werden.
            ''',
            check_set_errors=True
            )

    def selftest(self):
        Instrument.setting(
            "AST",
            '''AST Elektrometerfunktionstest starten
            Antwort wird vor Beendigung der Aktion gesendet.
            Ende und Resultat der Elektrometerfunktionstests muss mit ASS abgefragt
            werden.''',
            check_set_errors=True
            )


###########
# Results #
###########

    meas_result = Instrument.measurement(
        "MV",
        '''MV Messwerte abfragen   '''
        )

    range_end = Instrument.measurement(
        "MVM",
        '''MVM Messbereichsendwert der Strommessung für den Messbereich rge abfragen'''
        )

    resolution = Instrument.measurement(
        "MVR",
        '''MVR Die Messwertauflösung für den Messbereich rge abfragen'''
        )

    zero_result = Instrument.measurement(
        "NUS",
        '''Get status and result of the zero correction''',
        )

    selftest_result = Instrument.measurement(
        "ASS",
        '''Get status and result of the selftest'''
        )


######################
# JSON Configuration #
######################

    admin = Instrument.control(
        "ATG", "ATV",
        '''ATG Administrator-Berechtigung anfordern
        ATV Administrator-Berechtigung prüfen'''
        )

    read_all = Instrument.measurement(
        "RDA",
        '''Get all detectors RDA Alle Detektoren auslesen'''
        )

    detector = Instrument.control(
        "RDR", "WDR",
        '''RDR Detektor auslesen
        WDR Detektor bearbeiten'''
        )

    detector_delete = Instrument.control(
        "CDR", "GDR",
        '''CDR Detektor löschen
        GDR Detektor erstellen'''
        )

    meas_param = Instrument.control(
        "RMR", "WMR",
        '''RMR Messparameter auslesen
        WMR Messparameter bearbeiten'''
        )

    system_settings = Instrument.measurement(
        "RSR",
        '''Get the system settings.'''
        )

    system_info = Instrument.control(
        "RIR", "WSR",
        '''WSR Systeminformationen bearbeiten
        RIR Systeminformationen auslesen'''
        )

    meas_history = Instrument.measurement(
        "RHR",
        '''RHR Verlauf der Messungen auslesen'''
        )

    ap_config = Instrument.control(
        "RAC", "WAC",
        '''RAC WLAN Access Point Konfiguration auslesen
        WAC WLAN Access Point Konfiguration bearbeiten'''
        )

    lan_config = Instrument.control(
        "REC", "WEC",
        '''REC Ethernet Konfiguration auslesen
        WEC Ethernet Konfiguration bearbeiten'''
        )
