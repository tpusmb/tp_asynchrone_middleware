#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
import os
from time import sleep

from event_bus import ProcessManager, Process
import logging.handlers

PYTHON_LOGGER = logging.getLogger(__name__)
if not os.path.exists("log"):
    os.mkdir("log")
HDLR = logging.handlers.TimedRotatingFileHandler("log/test_sync_communication.log",
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


class SyncProcess(Process):

    def process(self, message_box):
        pass

    def run(self):
        """
        Main loop of the process.
        """
        sleep(1)
        if self.process_id == 0:
            acc_msg = self.communicator.send_to_sync("sync mmsg", 1)
            print("I'm {} and i get acknowledge from {}: {}".format(self.process_id, 1, acc_msg.payload))
        else:
            print("I'm {} and a wait for 5s".format(self.process_id))
            sleep(5)
            message = self.communicator.receive_from_sync("ok from 1", 0)
            print("I'm {} and i receive a message from {}: {}".format(self.process_id, message.sender,
                                                                      message.payload))

        print(self.getName() + " stopped")


if __name__ == "__main__":
    manager = ProcessManager()
    manager.add_process(2, SyncProcess)
    input("enter to exit\n")
    manager.stop_process()
