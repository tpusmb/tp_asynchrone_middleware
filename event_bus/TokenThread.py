#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from threading import Thread
from .Event import Event
from .Message import Message
from time import sleep
import os
import logging.handlers

PYTHON_LOGGER = logging.getLogger(__name__)
if not os.path.exists("log"):
    os.mkdir("log")
HDLR = logging.handlers.TimedRotatingFileHandler("log/TokenThread.log",
                                                 when="midnight", backupCount=60)
STREAM_HDLR = logging.StreamHandler()
FORMATTER = logging.Formatter("%(asctime)s %(filename)s [%(levelname)s] %(message)s")
HDLR.setFormatter(FORMATTER)
STREAM_HDLR.setFormatter(FORMATTER)
PYTHON_LOGGER.addHandler(HDLR)
PYTHON_LOGGER.addHandler(STREAM_HDLR)
PYTHON_LOGGER.setLevel(logging.DEBUG)

# Absolute path to the folder location of this python file
FOLDER_ABSOLUTE_PATH = os.path.normpath(os.path.dirname(os.path.abspath(__file__)))


class TokenThread(Thread):

    def __init__(self, bus, bus_size, owner_name):
        Thread.__init__(self)
        self.bus = bus
        self.bus_size = bus_size
        self.owner_name = owner_name
        self.token = False
        self.is_critical_section = False
        self.is_asking_for_critical_section = False

    def run(self):
        self.on_token()
        sleep(0.1)

    def request_critical_section(self):
        self.is_asking_for_critical_section = True

    def on_token(self):
        """
        Handle the token.
        """
        if self.token and not self.is_critical_section:
            if self.is_asking_for_critical_section:
                self.is_critical_section = True
            else:
                self.send_token()

    def release(self):
        self.send_token()
        self.is_asking_for_critical_section = False
        self.is_critical_section = False

    def send_token(self):
        """
        Send the token to the next process.
        """
        target = (int(self.owner_name()[1:]) % self.bus_size) + 1
        event = Event(topic="P{}".format(target), data=Message("token", self.owner_name, Message.TOKEN))
        self.bus.post(event)
        self.token = False
