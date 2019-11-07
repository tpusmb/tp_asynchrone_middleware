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
        """
        Constructor of the class.
        :param bus: (EventBus) The bus.
        :param bus_size: (Integer) The size of the bus.
        :param owner_name: (String) The process that own this thread.
        """
        Thread.__init__(self)
        self.bus = bus
        self.bus_size = bus_size
        self.owner_name = owner_name
        self.token = False
        self.is_critical_section = False
        self.is_asking_for_critical_section = False

    def run(self):
        """
        Main loop of this thread.
        """
        self.on_token()
        sleep(0.1)

    def request_critical_section(self):
        """
        Method to ask for the token to enter critical section.
        """
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
        """
        Release the token and quit critical section.
        """
        self.send_token()
        self.is_asking_for_critical_section = False
        self.is_critical_section = False

    def send_token(self):
        """
        Send the token to the next process.
        """
        dest = (int(self.owner_name()[1:]) % self.bus_size) + 1
        event = Event(topic=dest, data=Message("token", self.owner_name, Message.TOKEN))
        self.bus.post(event)
        self.token = False
