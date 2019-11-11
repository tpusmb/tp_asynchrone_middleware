from abc import ABC, abstractmethod
from threading import Thread
from time import sleep

from .Com import Com


class Process(Thread, ABC):

    def __init__(self, process_id, bus_size):
        """
        Constructor of the class.
        :param process_id: (int) id of the process.
        :param bus_size: (Integer) Number of process in the bus.
        """
        Thread.__init__(self)

        self.setName(str(process_id))
        self.process_id = process_id
        self.communicator = Com(self.process_id, bus_size, self.process)
        self.alive = True

    @abstractmethod
    def process(self, message_box):
        """
        Function call when this process get new messages
        :param message_box: (list of Message) All get message
        """
        pass

    def run(self):
        """
        Main loop of the process.
        """
        sleep(1)
        while self.alive:
            sleep(0.1)

        print(self.getName() + " stopped")

    def stop(self):
        """
        Stop the process.
        """
        self.communicator.token_thread.stop()
        self.alive = False
        self.join()
