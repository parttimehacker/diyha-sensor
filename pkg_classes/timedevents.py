#!/usr/bin/python3
""" Do it yourself timed event handler """

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

import time

class TimedEvents:
    """ timed event handler """

    def __init__(self, client, location_name, django, bme680, veml7700):
        """ Initialize 10 minute measurements intervals and a calibration """
        self.timed_events_dictionary = {
            "01": {"method": self.execute_timed_event, "executed": False},
            "11": {"method": self.execute_timed_event, "executed": False},
            "21": {"method": self.execute_timed_event, "executed": False},
            "31": {"method": self.execute_timed_event, "executed": False},
            "41": {"method": self.execute_timed_event, "executed": False},
            "51": {"method": self.execute_timed_event, "executed": False}
            }
        self.client = client
        self.location_name = location_name
        self.django = django
        self.bme680 = bme680
        self.veml7700 = veml7700
        
    def django_update(self,):
        ''' PUT environment data to the Django web server '''
        info = {'name': self.location_name}
        info['temperature'] = self.bme680.dict['temperature']
        info['humidity'] = self.bme680.dict['humidity']
        info['gas'] = self.bme680.dict['gas']
        info['pressure'] = self.bme680.dict['pressure']
        info['lux'] = self.veml7700.dict['lux']
        self.django.put_environment(info)

    def execute_timed_event(self,):
        ''' Execute timed event to compute averages and them publish. '''
        self.bme680.average_samples()
        self.bme680.publish_samples()
        self.veml7700.average_samples()
        self.veml7700.publish_samples()
        self.django_update()

    def last_timed_event(self,):
        ''' Reset the timed events dictionary to restart the process. '''
        for key in self.timed_events_dictionary:
            self.timed_events_dictionary[key]["executed"] = False
        # calibrate gas sensor every hour
        self.bme680.calibrate()

    def check_for_timed_events(self,):
        ''' see if its time to capture and publish measurements. '''
        minute_string = time.strftime("%M")
        if minute_string == "55":
            self.last_timed_event()
        elif minute_string in self.timed_events_dictionary:
            if not self.timed_events_dictionary[minute_string]["executed"]:
                self.timed_events_dictionary[minute_string]["executed"] = True
                self.timed_events_dictionary[minute_string]["method"]()