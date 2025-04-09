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

# Tested using SCPI over telnet (via ethernet). call signature:
# $ pytest test_ptwUNIDOS_with_device.py --device-address "TCPIP::172.23.19.1::8123::SOCKET"
# make sure the lock symbol on the display is closed so that write access is possible
#
# tested with a PTW UNIDOS Tango dosemeter


import pytest
from pymeasure.instruments.ptw.ptwUNIDOS import ptwUNIDOS
from time import sleep

############
# FIXTURES #
############


@pytest.fixture(scope="module")
def unidos(connected_device_address):
    instr = ptwUNIDOS(connected_device_address)
    instr.write_enabled = 1
    # ensure the device is in a defined state, e.g. by resetting it.
    return instr


class TestPTWUnidos:
    """Unit tests for PTW UNIDOS dosemeter."""

    RANGES = ['VERY_LOW', 'LOW', 'MEDIUM', 'HIGH']

    def test_id(self, unidos):
        name, type_nr, fw_ver, hw_rev = unidos.id
        assert 'UNIDOS' in name
        assert len(type_nr) == 7
        assert len(fw_ver) > 0
        assert len(hw_rev) == 3

    def test_reset(self, unidos):
        unidos.reset()
        assert unidos.status == 'RES'

    def test_write_enabled(self, unidos):
        assert unidos.write_enabled is True

    def test_mac_address(self, unidos):
        assert len(unidos.mac_address) == 17

    @pytest.mark.parametrize("range", RANGES)
    def test_range(self, unidos, range):
        unidos.range = range
        sleep(1)
        assert unidos.range == range

    def test_measure_hold(self, unidos):
        unidos.measure()
        assert unidos.status == 'MEAS'
        sleep(1)
        unidos.hold()
        assert unidos.status == 'HOLD'
        sleep(1)

    def test_status(self, unidos):
        assert unidos.status in ['RES', 'MEAS', 'HOLD', 'INT', 'INTHLD', 'ZERO',
                                 'AUTO', 'AUTO_MEAS', 'AUTO_HOLD', 'EOM', 'WAIT',
                                 'INIT', 'ERROR', 'SELF_TEST', 'TST']
