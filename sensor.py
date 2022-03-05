#!/usr/bin/python3
""" DIYHA Sensors, MQTT messages, timed event handlers and environment sensors """

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

import os
import time
import logging
import logging.config

# imported third party classes

import paho.mqtt.client as mqtt
from pkg_classes.bme680hal import Bme680HAL
from pkg_classes.veml7700hal import Veml7700HAL

# imported DIYHA classes

from pkg_classes.timedevents import TimedEvents

# DIYHA standard classes
from pkg_classes.topicmodel import TopicModel
from pkg_classes.whoview import WhoView
from pkg_classes.configmodel import ConfigModel
from pkg_classes.djangomodel import DjangoModel

# Start logging and enable imported classes to log appropriately.

LOGGING_FILE = '/usr/local/sensor/logging.ini'
logging.config.fileConfig( fname=LOGGING_FILE, disable_existing_loggers=False )
LOGGER = logging.getLogger(__name__)
LOGGER.info('Application started')

# get the command line arguments

CONFIG = ConfigModel(LOGGING_FILE)

# Location is used to create the topics and Django urls

TOPIC = TopicModel()  # Location MQTT topic
TOPIC.set(CONFIG.get_location())

# setup web server updates

DJANGO = DjangoModel(LOGGING_FILE)
DJANGO.set_urls(CONFIG.get_django_api_url(), TOPIC.get_location_name())

# Set up who message handler from MQTT broker and wait for client.

WHO = WhoView(LOGGING_FILE)

# process system messages: calibrate sensors and location information.

def system_message(msg):
    """ process system messages"""
    LOGGER.info(msg.topic+" "+msg.payload.decode('utf-8'))
    if msg.topic == 'diy/system/who':
        if msg.payload == b'ON':
            WHO.turn_on()
        else:
            WHO.turn_off()


# use a dispatch model for the subscriptions
TOPIC_DISPATCH_DICTIONARY = {
    "diy/system/calibrate":
        {"method":system_message},
    "diy/system/who":
        {"method":system_message},
    }


# The callback for when the client receives a CONNACK response from the server.
# def on_connect(client, userdata, flags, rc_msg):
def on_connect(client, userdata, flags, rc_msg):
    """ Subscribing in on_connect() means that if we lose the connection and
        reconnect then subscriptions will be renewed.
    """

    #pylint: disable=unused-argument

    client.subscribe("diy/system/calibrate", 1)
    client.subscribe("diy/system/who", 1)


def on_disconnect(client, userdata, rc_msg):
    """ Subscribing on_disconnect() tilt """

    #pylint: disable=unused-argument

    client.connected_flag = False
    client.disconnect_flag = True


# The callback for when a PUBLISH message is received from the server.

def on_message(client, userdata, msg):
    """ dispatch to the appropriate MQTT topic handler """

    #pylint: disable=unused-argument

    TOPIC_DISPATCH_DICTIONARY[msg.topic]["method"](msg)


if __name__ == '__main__':
    #Start utility threads, setup MQTT handlers then wait for timed events

    CLIENT = mqtt.Client()
    CLIENT.on_connect = on_connect
    CLIENT.on_disconnect = on_disconnect
    CLIENT.on_message = on_message

    # initilze the Who client for publishing.

    WHO.set_client(CLIENT)

    # command line argument for the switch mode - motion activated is the default

    CLIENT.connect(CONFIG.get_broker(), 1883, 60)
    CLIENT.loop_start()
    
    # let MQTT stuff initialize

    time.sleep(2) 

    # start the sensors and the timer which controls averaging and publishing

    BME680 = Bme680HAL(LOGGING_FILE, CLIENT, TOPIC.get_location_topic())
    BME680.calibrate()

    VEML7700 = Veml7700HAL(LOGGING_FILE, CLIENT, TOPIC.get_location_topic())

    TIMER = TimedEvents(CLIENT, TOPIC.get_location_name(), DJANGO, BME680, VEML7700)

    # loop forever checking for timed events

    while True:
        time.sleep(10.0)
        BME680.collect_sample()
        VEML7700.collect_sample()
        TIMER.check_for_timed_events()
