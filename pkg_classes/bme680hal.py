#!/usr/bin/python3
""" Manage BME680 pressure, temperature, humidity and gas sensor """

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
import adafruit_bme680

i2c = busio.I2C(board.SCL, board.SDA)
SENSOR = adafruit_bme680.Adafruit_BME680_I2C(i2c)
# change this to match the location's pressure (hPa) at sea level
SENSOR.sea_level_pressure = 1023.0

# start the message logging process

class Bme680HAL:
    """ Idle or sleep pattern """

    def __init__(self, logging_file, client, topic):
        """ create initial conditions and saving display and I2C lock """
        logging.config.fileConfig(fname=logging_file,
                          disable_existing_loggers=False)
        # Get the logger specified in the file
        self.logger = logging.getLogger(__name__)
        self.logger.info('Application started')
        self.client = client
        self.topic = topic
        # set to zero prior to calibration
        self.gas_baseline = 0.0
        # Set the humidity baseline to 40%, an optimal indoor humidity.
        self.hum_baseline = 40.0
        # This sets the balance between humidity and gas reading in the
        # calculation of air_quality_score (25:75, humidity:gas)
        self.hum_weighting = 0.25
        self.data = {}
        self.averages = {
            'temperature': 0.0,
            'humidity': 0.0,
            'pressure': 0.0,
            'gas': 0.0,
            'airQuality': 0.0
        }
        self.dict = {
            'temperature': '0.0',
            'humidity': '0.0',
            'pressure': '0.0',
            'gas': '0.0',
            'airQuality': '0.0'
        }
        self.samples = 0
        self.new_samples()

    def calibrate(self,):
        """ calibrate the BME680 sensor using burning logic """
        self.logger.info("Calibration: 5 minute gas resistance burn-in")
        start_time = time.time()
        curr_time = time.time()
        burn_in_time = 250
        burn_in_data = []
        while curr_time - start_time < burn_in_time:
            curr_time = time.time()
            burn_in_data.append(SENSOR.gas)
            time.sleep(5.0)
        self.gas_baseline = sum(burn_in_data[-50:]) / 50.0
        self.logger.info("Calibration completed")

    def new_samples(self,):
        """ initialize a new set of samples """
        self.data = {
            'temperature': 0.0,
            'humidity': 0.0,
            'pressure': 0.0,
            'gas': 0.0
        }
        self.samples = 0

    def collect_sample(self,):
        """ capture one data sample """
        self.data['temperature'] += SENSOR.temperature
        self.data['humidity'] += SENSOR.humidity
        self.data['pressure'] += SENSOR.pressure
        self.data['gas'] += SENSOR.gas
        self.samples += 1

    def compute_airquality(self,):
        """ compute air quality based on gas and humidity """
        gas_offset = self.gas_baseline - self.averages['gas']
        hum_offset = self.averages['humidity'] - self.hum_baseline
        # Calculate hum_score as the distance from the hum_baseline.
        if hum_offset > 0:
            hum_score = (100 - self.hum_baseline - hum_offset)
            hum_score /= (100 - self.hum_baseline)
            hum_score *= (self.hum_weighting * 100)
        else:
            hum_score = (self.hum_baseline + hum_offset)
            hum_score /= self.hum_baseline
            hum_score *= (self.hum_weighting * 100)
        # Calculate gas_score as the distance from the gas_baseline.
        if gas_offset > 0:
            gas_score = (self.averages['gas'] / self.gas_baseline)
            gas_score *= (100 - (self.hum_weighting * 100))
        else:
            gas_score = 100 - (self.hum_weighting * 100)
        # Calculate air_quality_score.
        self.averages['airQuality'] = hum_score + gas_score

    def average_samples(self,):
        """ compute averages based on number of samples """
        if self.samples > 0:
            self.averages['temperature'] = self.data['temperature'] / self.samples
            self.averages['humidity'] = self.data['humidity'] / self.samples
            self.averages['pressure'] = self.data['pressure'] / self.samples
            self.averages['gas'] = self.data['gas'] / self.samples
            self.compute_airquality()
        self.new_samples()

    def publish_samples(self,):
        """ publish data """
        # convert celcius to fahrenheit
        fahrenheit = 9.0 / 5.0 * self.averages['temperature'] + 32
        info = "{0:.1f}".format(fahrenheit)
        self.dict['temperature'] = info
        self.client.publish(self.topic+"/temperature", str(info), 0, True)
        time.sleep(1.0)

        info = "{0:.1f}".format(self.averages['humidity'])
        self.dict['humidity'] = info
        self.client.publish(self.topic+"/humidity", str(info), 0, True)
        time.sleep(1.0)

        # scale pressure for units and display
        pressure = self.averages['pressure'] / 10.0
        info = "{0:.1f}".format(pressure)
        self.dict['pressure'] = info
        self.client.publish(self.topic+"/pressure", str(info), 0, True)
        time.sleep(1.0)

        # scale gas for units and display
        gas = self.averages['gas'] / 1000.0
        info = "{0:.1f}".format(gas)
        self.dict['gas'] = info
        self.client.publish(self.topic+"/gas", str(info), 0, True)
        time.sleep(1.0)

        info = "{0:.1f}".format(self.averages['airQuality'])
        self.dict['airQuality'] = info
        self.client.publish(self.topic+"/airQuality", str(info), 0, True)


if __name__ == '__main__':
    exit()
