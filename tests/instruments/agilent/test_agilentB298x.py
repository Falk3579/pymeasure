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
from pymeasure.instruments.agilent.agilentB298x import AgilentB2987


class TestBattery:
    """Tests of the battery functions"""

    def test_battery_level(self):
        """Verify the communication of the battery_level getter."""
        with expected_protocol(
            AgilentB2987,
            [(":SYST:BATT?", "38")]
        ) as inst:
            assert inst.battery_level == 38

    def test_battery_cycles(self):
        """Verify the communication of the battery_cycles getter."""
        with expected_protocol(
            AgilentB2987,
            [(":SYST:BATT:CYCL?", "42")]
        ) as inst:
            assert inst.battery_cycles == 42

    @pytest.mark.parametrize("state", [True, False])
    def test_battery_selftest_passed(self, state):
        """Verify the communication of the battery_selftest_passed getter."""
        mapping = {True: 0, False: 1}
        with expected_protocol(
            AgilentB2987,
            [(":SYST:BATT:TEST?", mapping[state])]
        ) as inst:
            assert state == inst.battery_selftest_passed


class TestAgilentB2981:
    """Tests of the ammeter functions"""

    @pytest.mark.parametrize("state", [True, False])
    def test_input_enabled(self, state):
        """Verify the communication of the input_enabled getter/setter."""
        mapping = {True: 1, False: 0}
        with expected_protocol(
            AgilentB2987,
            [(f":INP {mapping[state]}", None),
             (":INP?", mapping[state])]
        ) as inst:
            inst.input_enabled = state
            assert state == inst.input_enabled

    @pytest.mark.parametrize("state", [True, False])
    def test_zero_corrected(self, state):
        """Verify the communication of the zero correct function getter/setter."""
        mapping = {True: 1, False: 0}
        with expected_protocol(
            AgilentB2987,
            [(f":INP:ZCOR {mapping[state]}", None),
             (":INP:ZCOR?", mapping[state])]
        ) as inst:
            inst.zero_corrected = state
            assert state == inst.zero_corrected

    def test_measure(self):
        """Verify the communication of the measure getter."""
        with expected_protocol(
            AgilentB2987,
            [(":MEAS?", "1.24E-13"),
             (":MEAS?", "1E-3,4895")]
        ) as inst:
            assert inst.measure == 1.24E-13
            assert inst.measure == [1E-3, 4895]

    def test_current(self):
        """Verify the communication of the current getter."""
        with expected_protocol(
            AgilentB2987,
            [(":MEAS:CURR?", "2.24E-14")]
        ) as inst:
            assert inst.current == 2.24E-14

    @pytest.mark.parametrize("range", ['MIN', 20E-6])
    def test_current_range(self, range):
        """Verify the communication of the current_range getter/setter."""
        with expected_protocol(
            AgilentB2987,
            [(f":CURR:RANG {range}", None),
             (":CURR:RANG?", range)]
        ) as inst:
            inst.current_range = range
            assert range == inst.current_range

##################
# Trigger system #
##################

@pytest.mark.parametrize("layer", ['ALL', 'ACQ', 'TRAN'])
class TestAgilentB298xTrigger:

    TRIGGER_LAYERS = {'ALL': 'all',
                      'ACQ': 'acquire',
                      'TRAN': 'transient',
                      }

    def test_abort(self, layer):
        """Verify the communication of the abort method with action."""
        with expected_protocol(
            AgilentB2987,
            [(f":ABOR:{layer}", None)]
        ) as inst:
            inst.abort(layer)

    def test_arm(self, layer):
        """Verify the communication of the arm method with action."""
        with expected_protocol(
            AgilentB2987,
            [(f":ARM:{layer}", None)]
        ) as inst:
            inst.arm(layer)

    def test_init(self, layer):
        """Verify the communication of the trigger init method with action."""
        with expected_protocol(
            AgilentB2987,
            [(f":INIT:{layer}", None)]
        ) as inst:
            inst.init(layer)

    @pytest.mark.parametrize("state", [True, False])
    def test_arm_bypass_once_enabled(self, layer, state):
        """Verify the communication of the arm_bypass_once_enabled getter/setter."""

        mapping = {True: 'ONCE', False: 'OFF'}
        with expected_protocol(
            AgilentB2987,
            [(f":ARM:{layer}:BYP {mapping[state]}", None),
             (f":ARM:{layer}:BYP?", mapping[state])]
        ) as inst:
            setattr(inst, f"arm_{self.TRIGGER_LAYERS[layer]}_bypass_once_enabled", state)
            assert state == getattr(inst, f"arm_{self.TRIGGER_LAYERS[layer]}_bypass_once_enabled")
























class TestAgilentB2985:
    """Tests of the electrometer functions"""

    @pytest.mark.parametrize("function", ['CURR', 'CHAR', 'VOLT', 'RES'])
    def test_function(self, function):
        """Verify the communication of the function getter/setter."""
        with expected_protocol(
            AgilentB2987,
            [(f":FUNC '{function}'", None),
             (":FUNC?", function)]
        ) as inst:
            inst.function = function
            assert function == inst.function

    def test_charge(self):
        """Verify the communication of the charge getter."""
        with expected_protocol(
            AgilentB2987,
            [(":MEAS:CHAR?", "5E-9")]
        ) as inst:
            assert inst.charge == 5E-9

    @pytest.mark.parametrize("range", ['MIN', 2E-6])
    def test_charge_range(self, range):
        """Verify the communication of the charge_range getter/setter."""
        with expected_protocol(
            AgilentB2987,
            [(f":CHAR:RANG {range}", None),
             (":CHAR:RANG?", range)]
        ) as inst:
            inst.charge_range = range
            assert range == inst.charge_range

    def test_resistance(self):
        """Verify the communication of the resistance getter."""
        with expected_protocol(
            AgilentB2987,
            [(":MEAS:RES?", "5E9")]
        ) as inst:
            assert inst.resistance == 5E9

    @pytest.mark.parametrize("range", ['MIN', 1E12])
    def test_resistance_range(self, range):
        """Verify the communication of the resistance_range getter/setter."""
        with expected_protocol(
            AgilentB2987,
            [(f":RES:RANG {range}", None),
             (":RES:RANG?", range)]
        ) as inst:
            inst.resistance_range = range
            assert range == inst.resistance_range

    def test_voltage(self):
        """Verify the communication of the voltage getter."""
        with expected_protocol(
            AgilentB2987,
            [(":MEAS:VOLT?", "11.34")]
        ) as inst:
            assert inst.voltage == 11.34

    @pytest.mark.parametrize("range", ['DEF', 20])
    def test_voltage_range(self, range):
        """Verify the communication of the voltage_range getter/setter."""
        with expected_protocol(
            AgilentB2987,
            [(f":VOLT:RANG {range}", None),
             (":VOLT:RANG?", range)]
        ) as inst:
            inst.voltage_range = range
            assert range == inst.voltage_range

####################
# Source functions #
####################

    @pytest.mark.parametrize("state", [0, 1])
    def test_source_enabled(self, state):
        """Verify the communication of the source_enabled getter/setter."""
        with expected_protocol(
            AgilentB2987,
            [(f":OUTP {state}", None),
             (":OUTP?", state)]
        ) as inst:
            inst.source_enabled = state
            assert state == inst.source_enabled

    @pytest.mark.parametrize("state", ['FLO', 'COMM'])
    def test_source_low_state(self, state):
        """Verify the communication of the source_low_state getter/setter."""
        with expected_protocol(
            AgilentB2987,
            [(f":OUTP:LOW {state}", None),
             (":OUTP:LOW?", state)]
        ) as inst:
            inst.source_low_state = state
            assert state == inst.source_low_state

    @pytest.mark.parametrize("state", ['ZERO', 'HIZ', 'NORM'])
    def test_source_off_state(self, state):
        """Verify the communication of the source_off_state getter/setter."""
        with expected_protocol(
            AgilentB2987,
            [(f":OUTP:OFF:MODE {state}", None),
             (":OUTP:OFF:MODE?", state)]
        ) as inst:
            inst.source_off_state = state
            assert state == inst.source_off_state

    @pytest.mark.parametrize("voltage", [0, 3, -2.5, 1000, 1.5e2, -1e3])
    def test_source_voltage(self, voltage):
        """Verify the communication of the source_voltage getter/setter."""
        with expected_protocol(
            AgilentB2987,
            [(f":SOUR:VOLT {voltage:g}", None),
             (":SOUR:VOLT?", voltage)]
        ) as inst:
            inst.source_voltage = voltage
            assert voltage == inst.source_voltage

    @pytest.mark.parametrize("range", ['MIN', 1000])
    def test_source_voltage_range(self, range):
        """Verify the communication of the source_voltage_range getter/setter."""
        with expected_protocol(
            AgilentB2987,
            [(f":SOUR:VOLT:RANG {range}", None),
             (":SOUR:VOLT:RANG?", range)]
        ) as inst:
            inst.source_voltage_range = range
            assert range == inst.source_voltage_range
