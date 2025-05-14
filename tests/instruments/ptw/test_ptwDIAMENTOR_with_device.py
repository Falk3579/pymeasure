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
from time import sleep

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
        assert type(diamentor.selftest_passed) is bool

    def test_constancy_check_passed(self, diamentor):
        assert type(diamentor.constancy_check_passed) is bool

    def test_is_calibrated(self, diamentor):
        assert type(diamentor.is_calibrated) is bool

    def test_is_eeprom_ok(self, diamentor):
        assert type(diamentor.is_eeprom_ok) is bool

    def test_pressure(self, diamentor):
        assert 500 <= diamentor.pressure <= 1500
        diamentor.pressure = 1013
        assert diamentor.pressure == 1013

    def test_id(self, diamentor):
        assert "CRS" in diamentor.id

    def test_measurement(self, diamentor):
        diamentor.reset()
        sleep(2)
        measurement = diamentor.measurement
        assert type(measurement["dap"]) is float
        assert type(measurement["dap_rate"]) is float
        assert type(measurement["time"]) is int
        assert type(measurement["crc"]) is int

    def test_serial_number(self, diamentor):
        serial_number = diamentor.serial_number
        assert type(serial_number) is int
        assert serial_number in range(1000000)

    def test_temperature(self, diamentor):
        temperature = diamentor.temperature
        assert type(temperature) is int
        assert temperature in range(71)
        diamentor.temperature = 20
        assert diamentor.temperature == 20

    def test_dap_unit(self, diamentor):
        assert diamentor.dap_unit in DAP_UNITS

    def test_calibration_factor(self, diamentor):
        assert 1E8 <= diamentor.calibration_factor <= 9.999E12

    def test_correctrion_factor(self, diamentor):
        assert 0 <= diamentor.correctrion_factor <= 9.999
