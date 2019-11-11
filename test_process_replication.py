#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

from event_bus import ProcessManager
from process_replication import ProcessReplication
import logging.handlers
import os

PYTHON_LOGGER = logging.getLogger(__name__)
if not os.path.exists("log"):
    os.mkdir("log")
HDLR = logging.handlers.TimedRotatingFileHandler("log/exam_2018_2019.log",
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

my_local_storage = {}

process_launch = ProcessManager()
process_launch.add_process(4, ProcessReplication)

print("set id (0, n-1), data, value")
print("edit id (0, n-1), data, value")

process_launch.process_list[0].set("a", "120")
process_launch.process_list[1].set("a", "120")
process_launch.process_list[2].set("a", "120")
process_launch.process_list[2].set("b", "100")
process_launch.process_list[3].set("b", "100")

while True:
    txt = input(">>>")
    if txt == "exit":
        break
    elif "edit" in txt:
        pro_id, data, value = txt.replace('edit', '').split(',')
        data = data.strip()
        value = value.strip()
        pro_id = int(pro_id.strip())
        process_launch.process_list[pro_id].edit(data, value)
    elif "set" in txt:
        pro_id, data, value = txt.replace('set', '').split(',')
        data = data.strip()
        value = value.strip()
        pro_id = int(pro_id.strip())
        process_launch.process_list[pro_id].set(data, value)


process_launch.stop_process()
