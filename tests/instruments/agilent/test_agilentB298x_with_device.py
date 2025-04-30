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

TEST_AMMETER = True
TEST_TRIGGER = True
TEST_SOURCE = True
TEST_BATTERY = True

TRIGGER_LAYERS = ['acquire', 'transient']
TRIGGER_SUB_SYSTEMS = ['arm', 'trigger']


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
def b298x_idle(agilentB298x):
    agilentB298x.trigger_all_is_idle
    agilentB298x.source_enabled = True
    agilentB298x.input_enabled = True
    return agilentB298x


@pytest.mark.skipif(not TEST_AMMETER, reason="Ammeter tests skipped by user")
class TestAmmeter:
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


@pytest.mark.skipif(not TEST_TRIGGER, reason="Trigger system tests skipped by user")
@pytest.mark.parametrize("layer", ['ALL', 'ACQ', 'TRAN'])
class TestTrigger:
    """Test of the trigger methods."""

    def test_abort(self, agilentB298x, layer):
        agilentB298x.abort(layer)
        assert len(agilentB298x.check_errors()) == 0

    def test_arm(self, agilentB298x, layer):
        agilentB298x.arm(layer)
        assert len(agilentB298x.check_errors()) == 0

    def test_init(self, b298x_idle, agilentB298x, layer):
        b298x_idle.init(layer)
        assert len(agilentB298x.check_errors()) == 0


@pytest.mark.skipif(not TEST_TRIGGER, reason="Trigger system tests skipped by user")
@pytest.mark.parametrize("layer", TRIGGER_LAYERS)
@pytest.mark.parametrize("sub_system", TRIGGER_SUB_SYSTEMS)
class TestTriggerProperties:
    """Tests of the trigger properties"""

    @pytest.mark.parametrize("state", [True, False])
    def test_bypass_once_enabled(self, agilentB298x, b298x_idle, layer, sub_system, state):
        setattr(b298x_idle, f"{sub_system}_{layer}_bypass_once_enabled", state)
        assert state == getattr(b298x_idle, f"{sub_system}_{layer}_bypass_once_enabled")
        assert len(agilentB298x.check_errors()) == 0

    @pytest.mark.parametrize("count", [1, 10])
    def test_count(self, agilentB298x, layer, sub_system, count):
        setattr(agilentB298x, f"{sub_system}_{layer}_count", count)
        assert count == getattr(agilentB298x, f"{sub_system}_{layer}_count")
        assert len(agilentB298x.check_errors()) == 0

    @pytest.mark.parametrize("delay", [0, 10, 1e3, 'MIN', 'MAX'])
    def test_delay(self, agilentB298x, layer, sub_system, delay):
        setattr(agilentB298x, f"{sub_system}_{layer}_delay", delay)
        if type(delay) is float:
            assert delay == getattr(agilentB298x, f"{sub_system}_{layer}_delay")
        if type(delay) is str:
            assert getattr(agilentB298x, f"{sub_system}_{layer}_delay") in [0, 100000]
        assert len(agilentB298x.check_errors()) == 0

    @pytest.mark.parametrize("source", ['AINT', 'BUS', 'EXT2'])
    def test_source(self, agilentB298x, sub_system, layer, source):
        setattr(agilentB298x, f"{sub_system}_{layer}_source", source)
        assert source == getattr(agilentB298x, f"{sub_system}_{layer}_source")

    @pytest.mark.parametrize("lan_id", ['LAN0', 'LAN7'])
    def test_source_lan_id(self, agilentB298x, sub_system, layer, lan_id):
        setattr(agilentB298x, f"{sub_system}_{layer}_lan_id", lan_id)
        assert lan_id == getattr(agilentB298x, f"{sub_system}_{layer}_lan_id")

    @pytest.mark.parametrize("timer", ['MIN', 'MAX', 'DEF', 1E-4, 0.12, 100000])
    def test_timer(self, agilentB298x, sub_system, layer, timer):
        setattr(agilentB298x, f"{sub_system}_{layer}_timer", timer)
        if type(timer) is float:
            assert timer == getattr(agilentB298x, f"{sub_system}_{layer}_timer")
        if type(timer) is str:
            assert getattr(agilentB298x, f"{sub_system}_{layer}_timer") in [1E-5, 1E-4, 1E5]
        assert len(agilentB298x.check_errors()) == 0

    @pytest.mark.parametrize("output_signal", ['INT1', 'TOUT', 'EXT3'])
    def test_output_signal(self, agilentB298x, sub_system, layer, output_signal):
        setattr(agilentB298x, f"{sub_system}_{layer}_output_signal", output_signal)
        assert output_signal == getattr(agilentB298x, f"{sub_system}_{layer}_output_signal")

    @pytest.mark.parametrize("state", [True, False])
    def test_output_enabled(self, agilentB298x, sub_system, layer, state):
        setattr(agilentB298x, f"{sub_system}_{layer}_output_enabled", state)
        assert state == getattr(agilentB298x, f"{sub_system}_{layer}_output_enabled")


@pytest.mark.skipif(not TEST_TRIGGER, reason="Trigger system tests skipped by user")
@pytest.mark.parametrize("sub_system", TRIGGER_SUB_SYSTEMS)
class TestTriggerPropertiesAllLayer:
    """Tests of the trigger properties for ALL layer"""

    @pytest.mark.parametrize("state", [True, False])
    def test_bypass_once_enabled(self, agilentB298x, b298x_idle, sub_system, state):
        setattr(b298x_idle, f"{sub_system}_all_bypass_once_enabled", state)
        assert len(agilentB298x.check_errors()) == 0

    @pytest.mark.parametrize("count", [1, 10])
    def test_count(self, agilentB298x, sub_system, count):
        setattr(agilentB298x, f"{sub_system}_all_count", count)
        assert len(agilentB298x.check_errors()) == 0

    @pytest.mark.parametrize("delay", [0, 10, 1e3, 'MIN', 'MAX'])
    def test_delay(self, agilentB298x, sub_system, delay):
        setattr(agilentB298x, f"{sub_system}_all_delay", delay)
        assert len(agilentB298x.check_errors()) == 0

    @pytest.mark.parametrize("source", ['AINT', 'BUS', 'EXT2'])
    def test_source(self, agilentB298x, sub_system, source):
        setattr(agilentB298x, f"{sub_system}_all_source", source)
        assert len(agilentB298x.check_errors()) == 0

    @pytest.mark.parametrize("lan_id", ['LAN0', 'LAN7'])
    def test_source_lan_id(self, agilentB298x, sub_system, lan_id):
        setattr(agilentB298x, f"{sub_system}_all_lan_id", lan_id)
        assert len(agilentB298x.check_errors()) == 0

    @pytest.mark.parametrize("timer", ['MIN', 'MAX', 'DEF', 1E-4, 0.12, 100000])
    def test_timer(self, agilentB298x, sub_system, timer):
        setattr(agilentB298x, f"{sub_system}_all_timer", timer)
        assert len(agilentB298x.check_errors()) == 0

    @pytest.mark.parametrize("output_signal", ['INT1', 'TOUT', 'EXT3'])
    def test_output_signal(self, agilentB298x, sub_system, output_signal):
        setattr(agilentB298x, f"{sub_system}_all_output_signal", output_signal)
        assert len(agilentB298x.check_errors()) == 0

    @pytest.mark.parametrize("state", [True, False])
    def test_output_enabled(self, agilentB298x, sub_system, state):
        setattr(agilentB298x, f"{sub_system}_all_output_enabled", state)
        assert len(agilentB298x.check_errors()) == 0


@pytest.mark.skipif(not TEST_SOURCE, reason="Source tests skipped by user")
class TestSource:
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


@pytest.mark.skipif(not TEST_SOURCE, reason="Electrometer tests skipped by user")
class TestElectrometer:
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


@pytest.mark.skipif(not TEST_BATTERY, reason="Battery tests skipped by user")
class TestBattery:
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
