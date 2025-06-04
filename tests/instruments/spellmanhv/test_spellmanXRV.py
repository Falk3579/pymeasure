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
from pymeasure.instruments.spellmanhv.spellmanXRV import SpellmanXRV


@pytest.fixture(scope="module")
def spellman(connected_device_address):
    instr = SpellmanXRV(connected_device_address)
    return instr


class TestSpellmanXRV:
    """Test for the Spellman XRV HV power supplies"""
    
    @pytest.mark.parametrize("baudrate", [9600, 38400, 57600, 115200])
    def test_baudrate(self, baudrate):
        with expected_protocol(
            SpellmanXRV,
            [(f"ASL;{baudrate}", f"ASL;{baudrate}"),
             ("ASL", f"ASL;{baudrate}")],
        ) as inst:
            inst.baudrate = baudrate
            assert baudrate == inst.baudrate
