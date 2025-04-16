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

import pytest
from pymeasure.test import expected_protocol
from pymeasure.instruments.ptw.ptwDIAMENTOR import ptwDIAMENTOR


def test_id():
    """Verify the communication of the ID getter."""
    with expected_protocol(
        ptwDIAMENTOR,
        [('PTW', 'CRS 1.2.4')],
    ) as inst:
        assert inst.id == 'CRS 1.2.4'


@pytest.mark.parametrize("temperature", [0, 1, 30])
def test_temperature(temperature):
    """Verify the communication of the temperature getter/setter."""
    with expected_protocol(
        ptwDIAMENTOR,
        [(f"TMPA{temperature:02d}", f"TMPA{temperature:02d}"),
         ('TMPA', f"TMPA{temperature:02d}")]
    ) as inst:
        inst.temperature = temperature
        assert inst.temperature == temperature


@pytest.mark.parametrize("pressure", [500, 1500])
def test_pressure(pressure):
    """Verify the communication of the pressure getter/setter."""
    with expected_protocol(
        ptwDIAMENTOR,
        [(f"PRE{pressure:04d}", f"PRE{pressure:04d}"),
         ('PRE', f"PRE{pressure:04d}")]
    ) as inst:
        inst.pressure = pressure
        assert inst.pressure == pressure


def test_serial_number():
    """Verify the communication of the serial number getter."""
    with expected_protocol(
        ptwDIAMENTOR,
        [("SER", "SER345678")]
    ) as inst:
        assert inst.serial_number == 345678


@pytest.mark.parametrize("dap_unit", [1, 2, 4])
def test_dap_unit(dap_unit):
    """Verify the communication of the dap_unit getter/setter."""
    with expected_protocol(
        ptwDIAMENTOR,
        [("U1", "U1")]
    ) as inst:
        inst.dap_unit = dap_unit
        assert inst.dap_unit == 345678
