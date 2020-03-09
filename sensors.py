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
import paho.mqtt.client as mqtt

from pkg_classes.adafruitbme680 import Bme680
from pkg_classes.adafruitveml7700 import Veml7700
from pkg_classes.mqttlocationtopic import MqttLocationTopic
from pkg_classes.timedevents import TimedEvents

# Start logging and enable imported classes to log appropriately.

logging.config.fileConfig(fname='/home/an/sensors/logging.ini',
                          disable_existing_loggers=False)
LOGGER = logging.getLogger("sensors")
LOGGER.info('Application started')

# Location info will be provided by the MQTT broker at runtime.

TOPIC = MqttLocationTopic()

# process system messages: calibrate sensors and location information.

def system_message(msg):
    """ process system messages"""
    LOGGER.info(msg.topic+" "+msg.payload.decode('utf-8'))


def topic_message(msg):
    """ Set the sensors location topic. Used to publish measurements. """
    LOGGER.info(msg.topic+" "+msg.payload.decode('utf-8'))
    topic = msg.payload.decode('utf-8')
    TOPIC.set(topic)


# use a dispatch model for the subscriptions
TOPIC_DISPATCH_DICTIONARY = {
    "diy/system/calibrate":
        {"method":system_message},
    "diy/system/who":
        {"method":system_message},
    TOPIC.get_setup():
        {"method":topic_message}
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
    client.subscribe(TOPIC.get_setup(), 1)


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

    # Environment variable contains Mosquitto IP address.

    BROKER_IP = os.environ.get('MQTT_BROKER_IP')

    CLIENT.connect(BROKER_IP, 1883, 60)
    CLIENT.loop_start()

    # message broker will send the location and set waiting to false.

    while TOPIC.waiting_for_location:
        time.sleep(5.0)

    # start the sensors and the timer which controls averaging and publishing

    BME680 = Bme680(CLIENT, TOPIC.get_location())
    BME680.calibrate()

    VEML7700 = Veml7700(CLIENT, TOPIC.get_location())

    TIMER = TimedEvents(CLIENT, TOPIC.get_location(), BME680, VEML7700)

    # loop forever checking for timed events

    while True:
        time.sleep(10.0)
        BME680.collect_sample()
        VEML7700.collect_sample()
        TIMER.check_for_timed_events()
