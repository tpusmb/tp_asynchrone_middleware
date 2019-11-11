#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

import logging.handlers
import os
import threading
from copy import deepcopy
from time import sleep

from .BroadcastEvent import BroadcastEvent
from .DedicatedEvent import DedicatedEvent
from .Event import Event
from .EventBus import EventBus
from .Lamport import Lamport
from .Message import Message
from .TokenThread import TokenThread

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

    def __init__(self, process_id, bus_size, call_back_function):
        """
        Constructor of the class.
        :param process_id: (int) id of the process
        :param bus_size: (Integer) Number of process in the bus.
        """
        self.bus = EventBus.get_instance()
        self.lamport = Lamport()
        self.token_thread = TokenThread(self.bus, bus_size, process_id)
        self.process_id = process_id
        self.call_back_function = call_back_function
        self.call_back_function_thread = None

        self.bus_size = bus_size
        self.synch_request_counter = 0
        self.waiting_for_sync = False
        self.sync_message = None

        self.process_alive = []
        self.message_box = []

        DedicatedEvent.subscribe_to_dedicated_channel(self.bus, self)
        BroadcastEvent.subscribe_to_broadcast(self.bus, self)

    def process(self, event):
        """
        Function to receive an event and handle his data.
        :param event: (Event) Event that contains the topic and data.
        """
        self.receive(event)

    def send_to(self, payload, dest):
        """
        Send a message to another process.
        :param payload: (String) Message to _send.
        :param dest: (int) Process that will receive the message.
        """
        print("send: {}".format(self.process_id))
        event = Event(topic=dest, data=Message(payload, self.process_id, Message.ASYNC))
        self._send(event)

    def send_to_sync(self, payload, dest):
        """
        Send a message to a process and wait for his response.
        :param payload: (String) Message to _send.
        :param dest: (String) id of the process to send
        """
        get_msg = False
        event = Event(topic=dest, data=Message(payload, self.process_id, Message.SYNC))
        self._send(event)
        while not get_msg:
            for msg in self.message_box:
                if msg.from_id == dest and msg.message_type == Message.SYNC:
                    get_msg = True
                    self.message_box.remove(msg)
            sleep(0.1)

    def broadcast(self, payload, message_type):
        """
        Send a message to every process.
        :param payload: (String) Message to _send.
        :param message_type: (String) Message type.
        """
        event = Event(topic="broadcast", data=Message(payload, self.process_id, message_type))
        self._send(event)

    def broadcast_sync(self, payload, sender):
        """
        Send a message to every process if the it is the sender. Else, will receive this message.
        :param payload: (String) Message to _send.
        :param sender: (int) Sender of the message.
        """
        if self.process_id is sender:
            for i in range(0, self.bus_size):
                if i is not self.process_id:
                    self.send_to_sync(payload, i)
        else:
            self.receive_from_sync(payload, sender)

    def receive_from_sync(self, payload, sender):
        """
        Wait for the message sent by the sender of the broadcast_sync method.
        :param payload: (String) The message.
        :param sender: (String) The sender of the message.
        """
        get_msg = False
        msg_get = None
        while not get_msg:
            for msg in self.message_box:
                if msg.from_id == sender and msg.message_type == Message.SYNC:
                    get_msg = True
                    msg_get = msg.payload
                    self.message_box.remove(msg)
            sleep(0.1)
        event = Event(topic=sender, data=Message(payload, self.process_id, Message.SYNC))
        self._send(event)
        return msg_get

    def _send(self, event):
        """
        Post a message into the bus.
        :param event: (Event) Event that contains the topic and the data of the message.
        """
        print("{} _send DATA: Message: {} & Type: {}"
              " | TOPIC: {}"
              " | counter: {}".format(self.process_id,
                                      event.get_data().payload,
                                      event.get_data().message_type,
                                      event.get_topic(),
                                      self.lamport.clock))
        self.update_lamport(self.lamport.get_clock() + 1)
        event.counter = self.lamport.clock
        self.bus.post(event)

    def receive(self, event):
        """
        Function to receive an event and handle his data.
        :param event: (Event) Event that contains the topic and the data of the message.
        """
        if isinstance(event, Event):
            data = event.get_data()
            topic = event.get_topic()
            if data.message_type is not Message.TOKEN:
                self.update_lamport(event.counter + 1 if event.counter > self.lamport.get_clock()
                                    else self.lamport.get_clock() + 1)

            if data.message_type is Message.TOKEN:
                self.token_thread.token = True
                return
            elif data.message_type is Message.SYNCHRONIZATION:
                self.synch_request_counter += 1
            elif data.message_type is Message.HEARTBIT:
                self.process_alive.append(data.payload)
            else:
                self.message_box.append(data)
                if self.call_back_function_thread is None or not self.call_back_function_thread.is_alive():
                    self.call_back_function_thread = threading.Thread(target=self.call_back_function,
                                                                      args=(deepcopy(self.message_box),))
                    self.message_box = []
                    self.call_back_function_thread.start()
            print("{} receive DATA: Message: {} & Type: {}"
                  " | TOPIC: {}"
                  " | counter: {}".format(self.process_id,
                                          data.payload, data.message_type, topic,
                                          self.lamport.clock))
        else:
            print(self.process_id + ' Invalid object type is passed.')

    def launch_token(self):
        """
        Give the token to this process.
        """
        self.token_thread.token = True

    def request_critical_section(self):
        """
        Wait until the token thread get the token to enter critical section.
        """
        self.token_thread.request_critical_section()
        while not self.token_thread.is_critical_section:
            sleep(0.1)

    def release_critical_section(self):
        """
        Will release the token to quit critical section.
        """
        self.token_thread.release()

    def synchronize(self):
        """
        Send a message to every process and wait until every process responded.
        """
        self.broadcast("synchronization", Message.SYNCHRONIZATION)
        while not self.synch_request_counter == self.bus_size:
            sleep(0.1)
        self.synch_request_counter = 0

    def update_lamport(self, value):
        """
        Set the Lamport clock.
        :param value: (Integer) The new value of the lamport clock.
        """
        self.lamport.set_clock(value)

    def loop(self):
        """
        Main loop of this communicator. Will _send an heartbit type message to notify that his process is alive.
        """
        self.broadcast(self.process_id, Message.HEARTBIT)
        sleep(1)
        self.check_process_alive()

    def check_process_alive(self):
        """
        Check if there is a dead process. Update his number if that is the case.
        """
        if len(self.process_alive) != 0 and len(self.process_alive) != self.bus_size:
            process_missing = 0
            done = False
            while not done and process_missing < self.bus_size:
                if process_missing not in self.process_alive:
                    done = True
                else:
                    process_missing += 1
            if process_missing < self.process_id:
                self.process_id -= 1
