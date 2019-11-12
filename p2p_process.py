#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
import os
from event_bus import Process
import logging.handlers

PYTHON_LOGGER = logging.getLogger(__name__)
if not os.path.exists("log"):
    os.mkdir("log")
HDLR = logging.handlers.TimedRotatingFileHandler("log/p2p_process.log",
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


class P2pProcess(Process):

    def __init__(self, process_id, bus_size, graph):
        super().__init__(process_id, bus_size)
        self.graph = graph

    def process(self, message_box):

        for message in message_box:
            to, acc, msg = message.payload
            to = int(to)
            # We are the destination
            if to == self.process_id:
                print("I'm {} and i get the message \"{}\" from {}".format(to, msg, message.sender))
            # Send the message to other neighbours
            elif acc - 1 > 0:
                self.send(to, msg, acc - 1, message.sender)
            else:
                print("I'm {} and the message \"{}\" have no more Hops".format(self.process_id, msg))

    def send(self, to, msg, acc=10, from_id=-1):
        """
        Send a message to all his neighbour
        :param to: (int) id of the process to send the message
        :param msg: (string) message body
        :param acc: (int) number of Hops. If Hops == 0 we dont send the message
        :param from_id: (int) id of the process that send the previous message to evoid sending again
        the message
        """
        if acc == 0:
            return
        # Directly send the message
        if to in self.graph[self.process_id]:
            self.communicator.send_to([to, acc, msg], to)
            return
        # Else send the message to each neighbours
        for voisin in self.graph[self.process_id]:
            if voisin != from_id:
                self.communicator.send_to([to, acc, msg], voisin)
