#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
import os
import timeit
import logging.handlers

PYTHON_LOGGER = logging.getLogger(__name__)
if not os.path.exists("log"):
    os.mkdir("log")
HDLR = logging.handlers.TimedRotatingFileHandler("log/Message.log",
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


class Message:

    SYNC = "sync"
    ASYNC = "async"
    TOKEN = "token"
    SYNCHRONIZATION = "synchronization"
    HEARTBIT = "heartbit"

    def __init__(self, payload, sender, message_type=ASYNC):
        """
        Constructor of the class.
        :param payload: (String) The message.
        :param sender: (String) Sender of the message.
        :param message_type: (String) Type of the message.
        """
        self.payload = payload
        self.message_type = message_type
        self.sender = sender
