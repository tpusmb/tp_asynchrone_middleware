#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script to show an usage example
The idea is that you have p2p graph each node can sen a message just to his neighbour
"""

from __future__ import absolute_import

import logging.handlers
import os

from event_bus import ProcessManager
from process_p2p import P2pProcess

PYTHON_LOGGER = logging.getLogger(__name__)
if not os.path.exists("log"):
    os.mkdir("log")
HDLR = logging.handlers.TimedRotatingFileHandler("log/test_p2p.log",
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

nb_process = 9
network = {0: [1],
           1: [0, 2, 3],
           2: [1],
           3: [4, 1],
           4: [3, 5, 6, 7],
           5: [4],
           7: [4],
           6: [4, 8],
           8: [6]}

process_launch = ProcessManager()
process_launch.add_process(nb_process, P2pProcess, graph=network)

print("commend the you can do. To exit enter `exit`")
print("send id (0, n-1), to id, message")

while True:
    txt = input(">>>")
    if txt == "exit":
        break
    elif "send" in txt:
        pro_id, to_id, msg = txt.replace('send', '').split(',')
        to_id = to_id.strip()
        msg = msg.strip()
        pro_id = int(pro_id.strip())
        process_launch.process_list[pro_id].send(to_id, msg)


process_launch.stop_process()
