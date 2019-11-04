#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from .EventBus import EventBus
from .Event import Event
from .Lamport import Lamport
from .TokenThread import TokenThread
from .BroadcastEvent import BroadcastEvent
from .DedicatedEvent import DedicatedEvent
import os
import logging.handlers

PYTHON_LOGGER = logging.getLogger(__name__)
if not os.path.exists("log"):
    os.mkdir("log")
HDLR = logging.handlers.TimedRotatingFileHandler("log/Com.log",
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


class Com:

    def __init__(self, owner_name, bus_size):
        self.bus = EventBus.get_instance()
        self.lamport = Lamport()
        self.token_thread = TokenThread()
        self.owner_name = owner_name

        self.bus_size = bus_size
        self.token = False
        self.is_critical_section = False

        self.message_box = []

        DedicatedEvent.subscribe_to_dedicated_channel(self.bus, self)
        BroadcastEvent.subscribe_to_broadcast(self.bus, self)

    def send_to(self, payload, target):
        """
        Send a message to another process.
        :param payload: (String) Message to send.
        :param target: (String) Process that will receive the message
        """
        event = Event(topic="P{}".format(target), data=payload)
        self.send(event)

    def broadcast(self, payload):
        """
        Send a message to every process.
        :param payload: (String) Message to send.
        """
        event = Event(topic="broadcast", data=payload)
        self.send(event)

    def send(self, event):
        """
        Post a message into the bus.
        :param event: (Event) Event that contains the topic and the message.
        """
        print(self.owner_name + " send DATA: {}"
                                " | TOPIC: {}"
                                " | counter: {}".format(event.get_data(), event.get_topic(), self.lamport.clock))
        self.update_lamport(self.lamport.get_clock() + 1)
        event.counter = self.lamport.clock
        self.bus.post(event)

    def receive(self, event):
        """
        Function to receive an event and handle his message.
        :param event: (Event) Event that contains the topic and the message.
        """

        if isinstance(event, Event):
            print(self.owner_name + " receive DATA: {}"
                                    " | TOPIC: {}"
                                    " | counter: {}".format(event.get_data(), event.get_topic(), self.lamport.clock))
            self.update_lamport(event.counter + 1 if event.counter > self.lamport.get_clock() else self.lamport.get_clock() + 1)
            self.message_box.append(event.get_data())

            """if data is "token":
                self.token = True
            elif data is "synchronization":
                self.synch_request_counter += 1
            elif data is "run":
                self.dice_game()
            else:
                self.process_results.append(data)
                if len(self.process_results) == self.bus_size:
                    self.check_winner()"""

        else:
            print(self.owner_name + ' Invalid object type is passed.')

    def launch_token(self):
        """
        Give the token to this process.
        """
        self.token_thread = True

    def request_critical_section(self):
        """
        Enter critical section, set this process critical section to True.
        """
        self.is_critical_section = True

    def release_critical_section(self):
        """
        Quit the critical section.
        """
        self.is_critical_section = False
        # self.send_token()

    def update_lamport(self, value):
        self.lamport.set_clock(value)
