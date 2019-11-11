#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

import logging.handlers
import os

from event_bus import Process
import glob
import json

PYTHON_LOGGER = logging.getLogger(__name__)
if not os.path.exists("log"):
    os.mkdir("log")
HDLR = logging.handlers.TimedRotatingFileHandler("log/process_replication.log",
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


class FileStorage:
    FOLDER = "data"

    def __init__(self, process_id):
        self.process_id = process_id
        self.local_data = {}
        if not os.path.exists(self.FOLDER):
            os.makedirs(self.FOLDER)

    def set_value(self, data, value):
        self.local_data[data] = value
        with open(os.path.join(FOLDER_ABSOLUTE_PATH, self.FOLDER, str(self.process_id)), 'w') as f:
            json.dump(self.local_data, f)

    def get_value(self, data):
        return self.local_data[data]

    def get_replica(self, data):
        ids = []
        for path in glob.glob(os.path.join(FOLDER_ABSOLUTE_PATH, self.FOLDER, '*')):
            with open(path) as f:
                data_local = json.load(f)
                if data in data_local and str(self.process_id) != os.path.basename(path):
                    ids.append(int(os.path.basename(path)))
        return ids


class ProcessReplication(Process):

    def __init__(self, name, bus_size):
        super().__init__(name, bus_size)
        self.file_storage = FileStorage(self.process_id)
        self.in_critical = False
        self.acc = -1

    def process(self, message_box):
        for msg in message_box:
            data = msg.payload
            try:
                # section critique
                if data == "section":
                    print("section")
                    self.in_critical = True
                    self.communicator.send_to("ok", msg.sender)
                elif data == "ok":
                    self.acc -= 1
                    print("acc = {}".format(self.acc))
                    if self.acc == 0:
                        self.in_critical = True
                elif data[0] in self.file_storage.local_data:
                    print("{} get: {}, {}".format(self.process_id, data[0], data[1]))
                    self.file_storage.set_value(data[0], data[1])
                    self.in_critical = False
                    # acuser
                    self.communicator.send_to("ok", msg.sender)
            except Exception as e:
                pass

    def edit(self, data, value):

        print("{} wait critical".format(self.process_id))
        while self.in_critical:
            pass
        print("{} done...".format(self.process_id))
        ids = self.file_storage.get_replica(data)

        # ask section critique
        self.acc = len(ids)
        for id_send in ids:
            print("send to: {} the section".format(id_send))
            self.communicator.send_to("section", id_send)

        print("{}  wait for all ok".format(self.process_id))
        while not self.in_critical:
            pass
        print("{} ok".format(self.process_id))

        # Send new value
        self.acc = len(ids)
        self.in_critical = False
        for id_send in self.file_storage.get_replica(data):
            print("send to: {}".format(id_send))
            self.communicator.send_to([data, value], id_send)

        print("{}  wait for all ok".format(self.process_id))
        while not self.in_critical:
            pass
        print("{} ok".format(self.process_id))

        self.in_critical = False
        self.file_storage.set_value(data, value)

    def set(self, data, value):
        print("Add " + data + " " + value)
        self.file_storage.set_value(data, value)
