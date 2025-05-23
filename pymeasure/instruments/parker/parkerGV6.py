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

from pymeasure.instruments import Instrument, SCPIUnknownMixin
from time import sleep
import re


class ParkerGV6(SCPIUnknownMixin, Instrument):
    """ Represents the Parker Gemini GV6 Servo Motor Controller
    and provides a high-level interface for interacting with
    the instrument
    """

    degrees_per_count = 0.00045  # 90 deg per 200,000 count

    def __init__(self, adapter, name="Parker GV6 Motor Controller", **kwargs):
        super().__init__(
            adapter,
            name,
            asrl={'baud_rate': 9600,
                  'timeout': 500,
                  },
            write_termination="\r",
            **kwargs
        )
        self.set_defaults()

    def read(self):
        """ Overwrite the Instrument.read command to provide the correct
        functionality
        """
        # TODO seems to be broken as it does not make sense see issue #623
        return re.sub(r'\r\n\n(>|\?)? ', '', "\n".join(self.readlines()))

    def set_defaults(self):
        """ Set up the default values for the motor, which
        is run upon construction
        """
        self.echo = False
        self.set_hardware_limits(False, False)
        self.use_absolute_position()
        self.average_acceleration = 1
        self.acceleration = 1
        self.velocity = 3

    def reset(self):
        """ Reset the motor controller while blocking and
        (CAUTION) resets the absolute position value of the motor
        """
        self.write("RESET")
        sleep(5)
        self.setDefault()
        self.enable()

    def enable(self):
        """ Enables the motor to move """
        self.write("DRIVE1")

    def disable(self):
        """ Disables the motor from moving """
        self.write("DRIVE0")

    @property
    def status(self):
        """ Get a list of the motor status in readable format """
        return self.ask("TASF").split("\r\n\n")

    def is_moving(self):
        """ Return True if the motor is currently moving """
        return self.position is None

    @property
    def angle(self):
        """ Control the angle in degrees based on the position
        and whether relative or absolute positioning is enabled,
        """
        position = self.position
        if position is not None:
            return position * self.degrees_per_count
        else:
            return None

    @angle.setter
    def angle(self, angle):
        self.position = int(angle * self.degrees_per_count**-1)

    @property
    def angle_error(self):
        """ Get the angle error in degrees based on the
        position error, or returns None on error
        """
        position_error = self.position_error
        if position_error is not None:
            return position_error * self.degrees_per_count
        else:
            return None

    @property
    def position(self):
        """ Control the angular position in counts, 4000 per revolution (int).
        """
        match = re.search(r'(?<=TPE)-?\d+', self.ask("TPE"))
        if match is None:
            return None
        else:
            return int(match.group(0))

    @position.setter
    def position(self, counts):
        self.write("D" + str(int(counts)))

    @property
    def position_error(self):
        """ Get the error in the number of counts that corresponds
        to the error in the angular position where 1 revolution equals
        4000 counts
        """
        match = re.search(r'(?<=TPER)-?\d+', self.ask("TPER"))
        if match is None:
            return None
        else:
            return int(match.group(0))

    def move(self):
        """ Initiate the motor to move to the setpoint """
        self.write("GO")

    def stop(self):
        """ Stop the motor during movement """
        self.write("S")

    def kill(self):
        """ Stop the motor """
        self.write("K")

    def use_absolute_position(self):
        """ Set the motor to accept setpoints from an absolute
        zero position
        """
        self.write("MA1")
        self.write("MC0")

    def use_relative_position(self):
        """ Set the motor to accept setpoints that are relative
        to the last position
        """
        self.write("MA0")
        self.write("MC0")

    def set_hardware_limits(self, positive=True, negative=True):
        """ Enable (True) or disables (False) the hardware
        limits for the motor
        """
        if positive and negative:
            self.write("LH3")
        elif positive and not negative:
            self.write("LH2")
        elif not positive and negative:
            self.write("LH1")
        else:
            self.write("LH0")

    def set_software_limits(self, positive, negative):
        """ Set the software limits for motion based on
        the count unit where 4000 counts is 1 revolution
        """
        self.write("LSPOS%d" % int(positive))
        self.write("LSNEG%d" % int(negative))

    @property
    def echo(self):
        """Set whether the echoing of all commands sent to the instrument is enabled (bool)."""
        raise NotImplementedError

    @echo.setter
    def echo(self, enable=False):
        if enable:
            self.write("ECHO1")
        else:
            self.write("ECHO0")

    @property
    def acceleration(self):
        """ Set the acceleration setpoint in revolutions per second
        squared.
        """
        pass  # TODO: Implement acceleration return value

    @acceleration.setter
    def acceleration(self, acceleration):
        self.write("A" + str(float(acceleration)))

    @property
    def average_acceleration(self):
        """ Set the average acceleration setpoint in revolutions
        per second squared.
        """
        pass  # TODO: Implement average_acceleration return value

    @average_acceleration.setter
    def average_acceleration(self, acceleration):
        self.write("AA" + str(float(acceleration)))

    @property
    def velocity(self):
        """ Set the velocity setpoint in revolutions per second."""
        pass  # TODO: Implement velocity return value

    @velocity.setter
    def velocity(self, velocity):  # in revs/s
        self.write("V" + str(float(velocity)))
