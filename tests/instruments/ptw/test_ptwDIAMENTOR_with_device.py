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


############
# FIXTURES #
############


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

    def test_id(self, diamentor9600):
        try:
            firmware = diamentor9600.id
        except VisaIOError:
            firmware = ""
            pass
        assert 'CRS' in firmware
