# Tp Asynchrone Middleware

BLANC Swan & LE BRAS Clément

This project implements an asynchronous middleware with a communication bus.

## Installation

You will need the following package:
    
    sudo apt install python3
    sudo apt install virtualenv
    sudo apt install python3-pip

## Python env preparation

Prepare your virtualenv:

    virtualenv -p python3 venv
    . venv/bin/activate

install all requirements

    pip install -r requirements.txt 

If you want to exit your virtualenv:

    deactivate

## Quick start

### Creat process

To creat a new process you need to implement the Process Class

```python
from event_bus import Process
class MyProcess(Process):

    def __init__(self, process_id, bus_size, param1, param2):
        super().__init__(process_id, bus_size)
        self.param1 = param1
        self.param2 = param2

    def process(self, message_box):
        """
        Function call we get a new message
        """
        pass
```

Then to run you process:

```python
from event_bus import ProcessManager
process_launch = ProcessManager()
# Start 5 MyProcess
process_launch.add_process(5, MyProcess, param1="foo", param2="bar")
process_launch.stop_process()
```

## Usage Exmaple

You have 4 different code example

### P2p graph

Example of p2p communication graph.

Test script: `python test_p2p.py`

Process class: `process_p2p.py`

### Data replication

Each process duplicate a data. When one process change his local data it notifies other processes to update their values

Test script: `python test_process_replication.py`

Process class: `process_replication.py`

### Sync communication

Simple sync communication between 2 process

Test script: `python test_sync_communication.py`

Process class: `test_sync_communication.py`

### Dice game

Dice game each process do the folling steps:

1. Throw a dice value between 1 and 100
2. Send the result to each other process
3. The process throw the bigest value. Ask for critical section to write his result
4. All Processes synchronize before restarting

Test script: `python test_dice_game.py`

Process class: `process_dice_game.py`