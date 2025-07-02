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

# Test using serial port:
# $ pytest test_spellmanXRV_with_device.py --device-address ASRL4
#
# Test using LAN port:
# $ pytest test_spellmanXRV_with_device.py --device-address "TCPIP::192.168.1.4::50000::SOCKET"
#

# The test does not enable the high voltage output.

import pytest
from pymeasure.instruments.spellmanhv.spellmanXRV import SpellmanXRV, StatusCode, ErrorCode


@pytest.fixture(scope="module")
def spellman(connected_device_address):
    instr = SpellmanXRV(connected_device_address)
    instr.reset_errors()
    return instr


class TestSpellmanXRV:
    """Tests for the Spellman XRV HV power supplies"""

    @pytest.mark.parametrize("voltage_setpoint", [19.54, 50e3, 160000, 0])
    def test_voltage_setpoint(self, spellman, voltage_setpoint):
        max_voltage = spellman.scaling["voltage"]
        spellman.voltage_setpoint = voltage_setpoint
        assert voltage_setpoint == pytest.approx(spellman.voltage_setpoint,
                                                 abs=0.51*max_voltage/4095)

    @pytest.mark.parametrize("current_setpoint", [10e-6, 1e-3, 0])
    def test_current_setpoint(self, spellman, current_setpoint):
        max_current = spellman.scaling["current"]
        spellman.current_setpoint = current_setpoint
        assert current_setpoint == pytest.approx(spellman.current_setpoint,
                                                 abs=0.51*max_current/4095)

    def test_analog_monitor(self, spellman):
        analog_monitor = spellman.analog_monitor
        assert list(analog_monitor.keys()) == ["voltage",
                                               "current",
                                               "filament",
                                               "voltage_setpoint",
                                               "current_setpoint",
                                               "limit",
                                               "preheat",
                                               "anode_current"
                                               ]

    def test_hv_on_timer(self, spellman):
        assert type(spellman.hv_on_timer) is float

    def test_status(self, spellman):
        status = spellman.status
        assert type(status) is StatusCode

    def test_dsp(self, spellman):
        dsp = spellman.dsp
        assert type(dsp["part_number"]) is str
        assert type(dsp["version"]) is int

    def test_configuration(self, spellman):
        configuration = spellman.configuration
        assert list(configuration.keys()) == ["reserved1",
                                              "over_voltage_percentage",
                                              "voltage_ramp_rate",
                                              "current_ramp_rate",
                                              "pre_warning_time",
                                              "arc_count",
                                              "reserved2",
                                              "quench_time",
                                              "max_kV",
                                              "max_mA",
                                              "watchdog_timer"
                                              ]

    def test_scaling(self, spellman):
        scaling = spellman.scaling
        assert type(scaling["voltage"]) is int
        assert type(scaling["current"]) is float
        assert scaling["polarity"] in [0, 1]

    def test_fpga(self, spellman):
        fpga = spellman.fpga
        assert type(fpga["part_number"]) is str
        assert type(fpga["version"]) is int

    def test_errors(self, spellman):
        errors = spellman.errors
        assert type(errors) is ErrorCode

    def test_output_enabled(self, spellman):
        output_enabled = spellman.output_enabled
        assert type(output_enabled) is bool

    def test_voltage(self, spellman):
        voltage = spellman.voltage
        assert type(voltage) is int

    def test_system_voltages(self, spellman):
        system_voltages = spellman.system_voltages
        assert list(system_voltages.keys()) == ["temperature",
                                                "reserved",
                                                "anode",
                                                "cathode",
                                                "ac_line_cathode",
                                                "dc_rail_cathode",
                                                "ac_line_anode",
                                                "dc_rail_anode",
                                                "lvps_pos",
                                                "lvps_neg"
                                                ]

    def test_temperature(self, spellman):
        temperature = spellman.temperature
        assert type(temperature) is float
        assert 0 <= temperature < 242.09  # (0.05911815 * 4095)


class TestFilament:
    def test_limit(self, spellman):
        limit = spellman.filament.limit
        assert type(limit) is list
        for element in limit:
            assert type(element) is int
            assert element in range(4096)

    def test_preheat(self, spellman):
        preheat = spellman.filament.preheat
        assert type(preheat) is list
        for element in preheat:
            assert type(element) is int
            assert element in range(4096)


class TestUnscaledData:
    @pytest.mark.parametrize("voltage_setpoint", [25, 4095, 0])
    def test_voltage_setpoint(self, spellman, voltage_setpoint):
        spellman.unscaled.voltage_setpoint = voltage_setpoint
        assert voltage_setpoint == spellman.unscaled.voltage_setpoint

    @pytest.mark.parametrize("current_setpoint", [12, 4095, 0])
    def test_current_setpoint(self, spellman, current_setpoint):
        spellman.unscaled.current_setpoint = current_setpoint
        assert current_setpoint == spellman.unscaled.current_setpoint

    def test_analog_monitor(self, spellman):
        analog_monitor = spellman.unscaled.analog_monitor
        assert type(analog_monitor) is dict
        for key in analog_monitor:
            assert type(analog_monitor[key]) is int
            assert analog_monitor[key] in range(4096)

    def test_voltage(self, spellman):
        voltage = spellman.unscaled.voltage
        assert type(voltage) is int
        assert voltage in range(4096)

    def test_lvps_monitor(self, spellman):
        lvps_monitor = spellman.unscaled.lvps_monitor
        assert type(lvps_monitor) is int
        assert lvps_monitor in range(4096)

    def test_system_voltages(self, spellman):
        system_voltages = spellman.unscaled.system_voltages
        assert type(system_voltages) is dict
        for key in system_voltages:
            assert system_voltages[key] in range(4096)
