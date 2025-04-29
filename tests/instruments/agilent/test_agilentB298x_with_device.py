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

# disconnect all cables from the unit before starting the test
#
# Tested using SCPI over USB. call signature:
# $ pytest test_agilentB298x_with_device.py --device-address USB0::0x2A8D::0x9B01::MY61390198::INSTR
#
# Test was performed with B2987B
#

import pytest
from pymeasure.instruments.agilent.agilentB298x import AgilentB2987  # B2987 supports all features
from time import sleep
# from pyvisa.errors import VisaIOError

DEVICE_ID = 'B2987'  # change to the connected device ID
HAS_SOURCE = ['B2985', 'B2987']
HAS_BATTERY = ['B2983', 'B2987']


@pytest.fixture(scope="module")
def agilentB298x(connected_device_address):
    instr = AgilentB2987(connected_device_address)
    return instr


@pytest.fixture
def resetted_b298x(agilentB298x):
    agilentB298x.clear()
    agilentB298x.reset()
    return agilentB298x


@pytest.fixture
def b298x_with_input_enabled(agilentB298x):
    agilentB298x.input_enabled = True
    return agilentB298x


@pytest.fixture
def b298x_idle(agilentB298x):
    agilentB298x.trigger_all_is_idle
    return agilentB298x


# @pytest.mark.skip(reason="Comment")
class TestAgilentB298xAmmeter:
    """Test of the ammeter functions."""

    def test_device_id(self, resetted_b298x):
        vendor, device_id, serial_number, firmware_version = resetted_b298x.id.split(',')
        assert "B298" in device_id

    def test_input_enabled(self, agilentB298x):
        input_enabled = agilentB298x.input_enabled
        assert input_enabled is False

    def test_zero_corrected(self, agilentB298x):
        zero_corrected = agilentB298x.zero_corrected
        assert type(zero_corrected) is bool

    @pytest.mark.parametrize("range", ['MIN', 'MAX', 'DEF', 'UP', 'DOWN', 2E-3])
    def test_current_range(self, agilentB298x, range):
        agilentB298x.current_range = range
        current_range = agilentB298x.current_range
        assert 2E-12 <= current_range <= 20E-3

    def test_current(self, agilentB298x):
        current = agilentB298x.current
        assert type(current) is float

##################
# Trigger system #
##################

    @pytest.mark.parametrize("action", ['ALL', 'ACQ'])
    def test_abort(self, agilentB298x, action):
        agilentB298x.abort(action)
        assert len(agilentB298x.check_errors()) == 0

    # @pytest.mark.parametrize("state", [True, False])
    # def test_arm_bypass_once_enabled(self, agilentB298x, state):
        # agilentB298x.arm_bypass_once_enabled = state
        # assert len(agilentB298x.check_errors()) == 0
        # assert state == agilentB298x.arm_bypass_once_enabled

    @pytest.mark.parametrize("action", ['ALL', 'ACQ'])
    def test_arm(self, agilentB298x, action):
        agilentB298x.arm(action)
        assert len(agilentB298x.check_errors()) == 0

    def test_init(self, agilentB298x):
        agilentB298x.init('ACQ')
        assert len(agilentB298x.check_errors()) == 0

    @pytest.mark.parametrize("count", [1, 10])
    def test_arm_count_acq(self, b298x_idle, count):
        b298x_idle.arm_count = count
        assert len(b298x_idle.check_errors()) == 0
        assert count == b298x_idle.arm_count


@pytest.mark.skipif(DEVICE_ID not in HAS_SOURCE, reason=f"{DEVICE_ID} has no source")
class TestAgilentB298xSource:
    """Test of the source functions of B2985 and B2987."""

    @pytest.mark.parametrize("state", [True, False])
    def test_enabled(self, agilentB298x, state):
        agilentB298x.source_enabled = state
        sleep(1)
        assert state == agilentB298x.source_enabled

    @pytest.mark.parametrize("low_state", ['FLO', 'COMM'])
    def test_source_low_state(self, agilentB298x, low_state):
        agilentB298x.source_low_state = low_state
        sleep(1)
        assert low_state == agilentB298x.source_low_state

    @pytest.mark.parametrize("off_state", ['ZERO', 'HIZ', 'NORM'])
    def test_source_off_state(self, off_state):
        agilentB298x.source_off_state = off_state
        assert off_state == agilentB298x.source_off_state

    @pytest.mark.parametrize("voltage", [-20, -5.3, 0.24, 1.25e1, 0])
    def test_source_voltage(self, agilentB298x, voltage):
        agilentB298x.source_voltage = voltage
        assert voltage == agilentB298x.source_voltage

    @pytest.mark.parametrize("range", ['MIN', 'MAX', 'DEF', 1, 20])
    def test_source_voltage_range(self, agilentB298x, range):
        RANGES = [20, -1000, 1000]
        agilentB298x.source_voltage_range = range
        assert agilentB298x.source_voltage_range in RANGES


@pytest.mark.skipif(DEVICE_ID not in HAS_SOURCE, reason=f"{DEVICE_ID} is not an electrometer")
class TestAgilentB298xElectrometer:
    """Test of the electrometer functions of B2985 and B2987."""

    @pytest.mark.parametrize("function", ['CURR', 'CHAR', 'VOLT'])
    def test_function(self, agilentB298x, function):
        agilentB298x.function = function
        assert function == agilentB298x.function

    def test_function_res(self, agilentB298x):
        agilentB298x.function = 'RES'
        assert ['VOLT', 'CURR', 'RES'] == agilentB298x.function

    def test_charge(self, agilentB298x):
        agilentB298x.function = 'CHAR'
        assert type(agilentB298x.charge) is float

    def test_charge_range(self, agilentB298x):
        assert 2E-9 <= agilentB298x.charge_range <= 2E-6

    def test_resistance(self, agilentB298x):
        agilentB298x.function = 'RES'
        assert type(agilentB298x.resistance) is float

    def test_resistance_range(self, agilentB298x):
        assert 1E6 <= agilentB298x.resistance_range <= 1E15

    def test_voltage(self, agilentB298x):
        agilentB298x.function = 'VOLT'
        assert type(agilentB298x.voltage) is float

    def test_voltage_range(self, agilentB298x):
        assert agilentB298x.voltage_range in [2, 20]


@pytest.mark.skipif(DEVICE_ID not in HAS_BATTERY, reason=f"{DEVICE_ID} has no battery")
class TestAgilentB298xBattery:
    """Test of the battery functions of B2983 and B2987."""

    def test_level(self, agilentB298x):
        level = agilentB298x.battery_level
        assert 0 <= level <= 100

    def test_cycles(self, agilentB298x):
        cycles = agilentB298x.battery_cycles
        assert cycles >= 0

    def test_selftest_passed(self, agilentB298x):
        selftest_passed = agilentB298x.battery_selftest_passed
        assert type(selftest_passed) is bool
