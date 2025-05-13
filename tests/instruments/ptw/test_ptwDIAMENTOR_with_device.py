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

# Tested using serial port. call signature:
# $ pytest test_ptwDIAMENTOR_with_device.py --device-address COM1""
#


import pytest
from pymeasure.instruments.ptw.ptwDIAMENTOR import ptwDIAMENTOR
from pyvisa.errors import VisaIOError

BAUD_RATES = [9600, 19200, 38400, 57600, 115200]
DAP_UNITS = ["cGycm2", "Gycm2", "uGym2", "Rcm2"]

############
# FIXTURES #
############

@pytest.fixture(scope="module")
def diamentor(connected_device_address):
    for baud_rate in BAUD_RATES:  # probe for the correct baud rate
        instr = ptwDIAMENTOR(connected_device_address, baud_rate=baud_rate)

        try:
            firmware = diamentor.id
        except VisaIOError:
            firmware = ""

        if "CRS" in firmware:
            return instr


@pytest.fixture(scope="module")
def diamentor9600(connected_device_address):
    instr = ptwDIAMENTOR(connected_device_address, baud_rate=9600)
    return instr


@pytest.fixture(scope="module")
def diamentor19200(connected_device_address):
    instr = ptwDIAMENTOR(connected_device_address, baud_rate=19200)
    return instr


@pytest.fixture(scope="module")
def diamentor38400(connected_device_address):
    instr = ptwDIAMENTOR(connected_device_address, baud_rate=38400)
    return instr


@pytest.fixture(scope="module")
def diamentor57600(connected_device_address):
    instr = ptwDIAMENTOR(connected_device_address, baud_rate=57600)
    return instr


@pytest.fixture(scope="module")
def diamentor115200(connected_device_address):
    instr = ptwDIAMENTOR(connected_device_address, baud_rate=115200)
    return instr


class TestPTWDiamentorProperties:
    """Tests for PTW DIAMENTOR dosemeter properties."""
        
    def test_baudrate(self, diamentor):
        baud_rate = diamentor.baud_rate
        assert baud_rate in BAUD_RATES

    def test_selftest_passed(self, diamentor):
        selftest_passed = diamentor.selftest_passed
        assert type(selftest_passed) in bool

    def test_constancy_check_passed(self, diamentor):
        constancy_check_passed = diamentor.constancy_check_passed
        assert type(constancy_check_passed) in bool

    def test_is_calibrated(self, diamentor):
        is_calibrated = diamentor.is_calibrated
        assert type(is_calibrated) in bool

    def test_is_eeprom_ok(self, diamentor):
        is_eeprom_ok = diamentor.is_eeprom_ok
        assert type(is_eeprom_ok) in bool





    # def test_pressure(self, diamentor):

    def test_id(self, diamentor):
        try:
            firmware = diamentor.id
        except VisaIOError:
            firmware = ""

        assert "CRS" in firmware

    # def test_measurement(self, diamentor):
    # def test_serial_number(self, diamentor):
    # def test_temperature(self, diamentor):
    # def test_dap_unit(self, diamentor):
    # def test_calibration_factor(self, diamentor):
    # def test_correctrion_factor(self, diamentor):
