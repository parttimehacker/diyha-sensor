#!/usr/bin/python3
""" DIYHA test topic model for the siren application """

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

import logging.config

class TestModel:
    """ Manage all diy/system/test topic messages
    """

    def __init__(self, logging_file):
        """ Create two topics for this application. """
        logging.config.fileConfig( fname=logging_file, disable_existing_loggers=False )
        # Get the logger specified in the file
        self.logger = logging.getLogger(__name__)
        self.logger.info("Switch Test Model started")
        self.options = {
            b'0' : self.off,
            b'1': self.no_op,
            b'2': self.no_op,
            b'3': self.no_op,
            b'4': self.no_op,
            b'5': self.on,
            b'6': self.off,
            b'7': self.no_op,
            b'9': self.no_op,
            b'8': self.no_op,
            b'ON' : self.on,
            b'OFF': self.off
        }

    def no_op(self):
        self.logger.info("Tilt: not a valid msg")

    def on(self):
        self.logger.info("case 5: ON switch on")

    def off(self):
        self.logger.info("case 6: OFF switch off")

    def on_message(self, msg):
        print("test message> ", msg)
        self.options[msg]()
        self.logger.info("handle diy/system/test message")

