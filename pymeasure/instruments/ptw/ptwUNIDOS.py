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
from pymeasure.instruments.validators import (strict_discrete_set,
                                              strict_discrete_range)


class ptwUNIDOS(Instrument):
    '''A class representing the PTW UNIDOS dosemeter.'''

    def __init__(self, adapter, name="PTW UNIDOS dosemeter",
                 **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs
        )

    def check_errors(self):
        '''Get device errors.

        Error codes:
        E;01 Syntax error, unknown command
        E;02 Command not allowed in this context
        E;03 Command not allowed at this moment
        E;08 Parameter error
             – Value invalid/out of range
             – Wrong format of the parameter (eg. date in yyy-mm-dd format)
        E;12 Abort by user
        E;16 Command to long
        E;17 Maximum number of parameters exceeded
        E;18 Empty parameter field
        E;19 Wrong number of parameters
        E;20 No user rights, no write permission
        E;21 Required parameter not found (eg. detector)
        E;24 Memory erroro: data could not be stored
        E;28 Unknown parameter
        E;29 Wrong parameter type
        E;33 Measurement module defect
        E;51 Undefined command
        E;52 Wrong parameter type of the HTTP response
        E;54 HTTP request denied
        E;58 Wrong valueof the HTTP response
        E;96 Timeout
        '''
        pass


#################
# ID and status #
#################

    id = Instrument.measurement(
        "PTW",
        '''Get the dosemeter ID.'''
        )

    serial_number = Instrument.measurement(
        "SER",
        '''Get the dosemeter serial number.'''
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
        "TOK", "TOK",
        '''Control the write access (boolean).''',
        validator=strict_discrete_set,
        mapvalues=True,
        values={True: 1, False: 0}
        )

###################
# Device settings #
###################

    use_electrical_units = Instrument.control(
        "UEL", "",
        '''Control if electrical units are used (boolean).''',
        validator=strict_discrete_set,
        mapvalues=True,
        values={True: 'true', False: 'false'}
        )

    range = Instrument.control(
        "RGE", "",
        '''Control the measurement range.''',
        validator=strict_discrete_set,
        values=['LONG', 'MEDIUM']
        )

    voltage = Instrument.control(
        "HV", "",
        '''HV Aktuelle Hochspannung abfragen/setzen
        Hier werden die Limits des Detektor-Eintrages angewendet. '''
        )

    integration_time = Instrument.control(
        "IT", "",
        '''IT Integrationszeit abfragen/setzen                     '''
        )

    use_autostart = Instrument.control(
        "ASE", "ASE",
        '''ASE Autostart abfragen/setzen    (boolean)                       '''
        )

    use_autoreset = Instrument.control(
        "ASR", "ASR",
        '''ASR Autoreset abfragen/setzen             (boolean)              '''
        )

    autostart_level = Instrument.control(
        "ASL", "ASL",
        '''ASL Schwelle für Autostart-Messung abfrage/setzen'''
        )

    def clear_history(self):
        self.write("CHR")
        '''CHR: Komplette Historie löschen'''
        pass

###########################
# Measurement and Control #
###########################

    def meas(self):
        '''Start the dose or charge measurement'''
        self.write("STA")

    def hold(self):
        '''Set the measurment to HOLD state'''
        self.write("HLD")

    def reset(self):
        '''RES Dosis- oder Ladungsmessung und      '''
        '''Rücksetzen der Messwerte beenden        '''
        self.write("RES")

    def intervall(self):
        '''INT Intervallmessung starten            '''
        self.write("INT")

    def zero(self):
        '''NUL Nullabgleich starten
        Antwort wird vor Beendigung der Aktion gesendet.
        Abgleichsende und -resultat muss mit NUS abgefragt werden.
        '''
        pass

    def selftest(self):
        '''AST Elektrometerfunktionstest starten
        Antwort wird vor Beendigung der Aktion gesendet.
        Ende und Resultat der Elektrometerfunktionstests muss mit ASS abgefragt
        werden.'''
        pass


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
        "", "",
        '''ATG Administrator-Berechtigung anfordern
        ATV Administrator-Berechtigung prüfen'''
        )

    read_all = Instrument.measurement(
        "", "",
        '''RDA Alle Detektoren auslesen'''
        )

    detector = Instrument.control(
        "", "",
        '''RDR Detektor auslesen
        WDR Detektor bearbeiten'''
        )

    detector_delete = Instrument.control(
        "", "",
        '''CDR Detektor löschen
        GDR Detektor erstellen'''
        )

    meas_param = Instrument.control(
        "", "",
        '''RMR Messparameter auslesen
        WMR Messparameter bearbeiten'''
        )

    system_settings = Instrument.measurement(
        "RSR",
        '''RSR Systemsettings auslesen'''
        )

    system_info = Instrument.control(
        "", "",
        '''WSR Systeminformationen bearbeiten
        RIR Systeminformationen auslesen'''
        )

    meas_history = Instrument.measurement(
        "RHR",
        '''RHR Verlauf der Messungen auslesen'''
        )

    ap_config = Instrument.control(
        "", "",
        '''RAC WLAN Access Point Konfiguration auslesen
        WAC WLAN Access Point Konfiguration bearbeiten'''
        )

    lan_config = Instrument.control(
        "", "",
        '''REC Ethernet Konfiguration auslesen
        WEC Ethernet Konfiguration bearbeiten'''
        )
