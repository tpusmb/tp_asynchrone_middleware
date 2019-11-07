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
        """
        Constructor of the class.
        :param owner_name: (String) Name of the process that own this instance of comunicator.
        :param bus_size: (Integer) Number of process in the bus.
        """
        self.bus = EventBus.get_instance()
        self.lamport = Lamport()
        self.token_thread = TokenThread(self.bus, bus_size, owner_name)
        self.owner_name = owner_name
        self.number = int(self.owner_name[1:]) - 1

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
        :param payload: (String) Message to send.
        :param dest: (String) Process that will receive the message.
        """
        event = Event(topic="P{}".format(dest), data=Message(payload, self.owner_name, Message.ASYNC))
        self.send(event)

    def send_to_sync(self, payload, dest):
        """
        Send a message to a process and wait for his response.
        :param payload: (String) Message to send.
        :param dest: (String) Process that will receive the message.
        """
        get_msg = False
        event = Event(topic=dest, data=Message(payload, self.owner_name, Message.SYNC))
        self.send(event)
        while not get_msg:
            for msg in self.message_box:
                if msg.from_id == dest and msg.message_type == Message.SYNC:
                    get_msg = True
                    self.message_box.remove(msg)
            sleep(0.1)

    def broadcast(self, payload, message_type):
        """
        Send a message to every process.
        :param payload: (String) Message to send.
        :param message_type: (String) Message type.
        """
        event = Event(topic="broadcast", data=Message(payload, self.owner_name, message_type))
        self.send(event)

    def broadcast_sync(self, payload, sender):
        """
        Send a message to every process if the it is the sender. Else, will receive this message.
        :param payload: (String) Message to send.
        :param sender: (String) Sender of the message.
        """
        if self.owner_name is sender:
            for i in range(0, self.bus_size):
                if "P{}".format(i) is not self.owner_name:
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
        event = Event(topic=sender, data=Message(payload, self.owner_name, Message.SYNC))
        self.send(event)
        return msg_get

    def send(self, event):
        """
        Post a message into the bus.
        :param event: (Event) Event that contains the topic and the data of the message.
        """
        print(self.owner_name + " send DATA: Message: {} & Type: {}"
                                " | TOPIC: {}"
                                " | counter: {}".format(event.get_data().payload,
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
            print(self.owner_name + " receive DATA: Message: {} & Type: {}"
                                    " | TOPIC: {}"
                                    " | counter: {}".format(data.payload, data.message_type, topic, self.lamport.clock))
            if data.message_type is not Message.TOKEN:
                self.update_lamport(event.counter + 1 if event.counter > self.lamport.get_clock()
                                    else self.lamport.get_clock() + 1)

            if data.message_type is Message.TOKEN:
                self.token_thread.token = True
            elif data.message_type is Message.SYNCHRONIZATION:
                self.synch_request_counter += 1
            elif data.message_type is Message.HEARTBIT:
                self.process_alive.append(data.payload)
            else:
                self.message_box.append(data)
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
        Main loop of this communicator. Will send an heartbit type message to notify that his process is alive.
        """
        self.broadcast(self.number, Message.HEARTBIT)
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
            if process_missing < self.number:
                self.number -= 1

