#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from threading import Thread
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

    def __init__(self):
        Thread.__init__(self)
        self.token = False

    def run(self):
        self.on_token()
        sleep(0.1)

    def on_token(self):
        """
        Handle the token.
        """
        if self.token:
             """if self.is_critical_section:
                self.release_critical_section()
                self.write_winner()
                self.broadcast("run")
            else:
                self.send_token()"""

    def send_token(self):
        """
        Send the token to the next process.
        """
        """target = (int(self.owner_name()[1:]) % self.bus_size) + 1
        self.send_to("token", target)
        self.token = False"""