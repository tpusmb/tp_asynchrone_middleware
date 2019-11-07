#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from time import sleep
import asyncio
import os
import logging.handlers

PYTHON_LOGGER = logging.getLogger(__name__)
if not os.path.exists("log"):
    os.mkdir("log")
HDLR = logging.handlers.TimedRotatingFileHandler("log/Lamport.log",
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


class Lamport(object):

    def __init__(self):
        """
        Constructor of the class.
        """
        self.clock = 0
        self.sem = asyncio.Semaphore(1)

    def get_clock(self):
        """
        Getter of the clock.
        :return: (Integer) The clock.
        """
        return self.clock

    def set_clock(self, value):
        """
        Setter of the clock.
        :param value: (Integer) The new value of the clock.
        """
        """while not self.sem.locked():
            sleep(0.1)"""
        self.clock = value

    def lock_clock(self):
        """
        Method to lock the access to the clock.
        """
        self.sem.acquire()

    def unlock_clock(self):
        """
        Method to unlock the access to the clock.
        """
        self.sem.release()
