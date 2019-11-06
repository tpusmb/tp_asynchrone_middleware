#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from .EventBus import EventBus
from .Event import Event
from .Lamport import Lamport
from .TokenThread import TokenThread
from .Message import Message
from .BroadcastEvent import BroadcastEvent
from .DedicatedEvent import DedicatedEvent
from time import sleep
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
        self.token_thread = TokenThread(self.bus, self.bus_size, owner_name)
        self.owner_name = owner_name

        self.bus_size = bus_size
        self.synch_request_counter = 0

        self.message_box = []
        self.waiting_for_sync = False
        self.sync_message = None
        DedicatedEvent.subscribe_to_dedicated_channel(self.bus, self)
        BroadcastEvent.subscribe_to_broadcast(self.bus, self)

    def send_to(self, payload, target):
        """
        Send a message to another process.
        :param payload: (String) Message to send.
        :param target: (String) Process that will receive the message
        """
        event = Event(topic="P{}".format(target), data=Message(payload, self.owner_name, Message.ASYNC))
        self.send(event)

    def broadcast(self, payload):
        """
        Send a message to every process.
        :param payload: (String) Message to send.
        """
        event = Event(topic="broadcast", data=Message(payload, self.owner_name, Message.ASYNC))
        self.send(event)

    def broadcast_sync(self, payload, process_from):
        if self.owner_name is process_from:
            for i in range(0, self.bus_size):
                if "P{}".format(i) is not self.owner_name:
                    self.send_to_sync(payload, "P{}".format(i))
        else:
            self.receive_from_sync(payload, process_from)

    def send_to_sync(self, payload, dest):
        get_msg = False
        event = Event(topic=dest, data=Message(payload, self.owner_name, Message.SYNC))
        self.send(event)
        while not get_msg:
            for msg in self.message_box:
                if msg.from_id == dest and msg.message_type == Message.SYNC:
                    get_msg = True
                    self.message_box.remove(msg)
            sleep(0.1)

    def receive_from_sync(self, payload, process_from):
        get_msg = False
        msg_get = None
        while not get_msg:
            for msg in self.message_box:
                if msg.from_id == process_from and msg.message_type == Message.SYNC:
                    get_msg = True
                    msg_get = msg.payload
                    self.message_box.remove(msg)
            sleep(0.1)
        event = Event(topic=process_from, data=Message(payload, self.owner_name, Message.SYNC))
        self.send(event)
        return msg_get

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
            data = event.get_data()
            topic = event.get_topic()
            print(self.owner_name + " receive DATA: {}"
                                    " | TOPIC: {}"
                                    " | counter: {}".format(data, topic, self.lamport.clock))
            if data.message_type is not Message.TOKEN:
                self.update_lamport(event.counter + 1 if event.counter > self.lamport.get_clock()
                                    else self.lamport.get_clock() + 1)

            self.message_box.append(data)

            if data.payload is "synchronization":
                self.synch_request_counter += 1
            """elif data is "run":
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
        self.token_thread.request_critical_section()
        while not self.token_thread.is_critical_section:
            sleep(0.1)

    def release_critical_section(self):
        """
        Quit the critical section.
        """
        self.token_thread.release()

    def synchronize(self):
        """
        Send a message to every process.
        """
        self.broadcast("synchronization")
        while not self.synch_request_counter == self.bus_size:
            sleep(0.1)
        self.synch_request_counter = 0

    def update_lamport(self, value):
        self.lamport.set_clock(value)
