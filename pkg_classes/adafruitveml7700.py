#!/usr/bin/python3
""" Manage VEML7700 light and lux sensor """

# The MIT License (MIT)
#
# Copyright (c) 2019 parttimehacker@gmail.com
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

# Many attributes for this complex sensor.
# pylint: disable=too-many-instance-attributes

import time
import logging
import logging.config

import board
import busio
import adafruit_veml7700

i2c = busio.I2C(board.SCL, board.SDA)
SENSOR = adafruit_veml7700.VEML7700(i2c)

# start the message logging process

logging.config.fileConfig(fname='/home/an/sensor/logging.ini',
                          disable_existing_loggers=False)

# Get the logger specified in the file
LOGGER = logging.getLogger(__name__)
LOGGER.info('Application started')

class Veml7700:
    """ Idle or sleep pattern """

    def __init__(self, client, topic):
        """ create initial conditions and saving display and I2C lock """
        self.client = client
        self.topic = topic
        self.data = {}
        self.averages = {
            'ambientLight': 0.0,
            'lux': 0.0
        }
        self.samples = 0
        self.new_samples()

    def new_samples(self,):
        """ initialize a new set of samples """
        self.data = {
            'ambientLight': 0.0,
            'lux': 0.0
        }
        self.samples = 0

    def collect_sample(self,):
        """ capture one data sample """
        self.data['ambientLight'] += SENSOR.light
        self.data['lux'] += SENSOR.lux
        self.samples += 1

    def average_samples(self,):
        """ compute averages based on number of samples """
        if self.samples > 0:
            self.averages['ambientLight'] = self.data['ambientLight'] / self.samples
            self.averages['lux'] = self.data['lux'] / self.samples
        self.new_samples()

    def publish_samples(self,):
        """ publish data """
        info = "{0:.1f}".format(self.averages['ambientLight'])
        self.client.publish(self.topic+"/ambientLight", str(info), 0, True)
        info = "{0:.1f}".format(self.averages['lux'])
        self.client.publish(self.topic+"/lux", str(info), 0, True)

if __name__ == '__main__':
    exit()
