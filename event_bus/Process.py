from abc import ABC, abstractmethod
from threading import Thread
from time import sleep

from .Com import Com


class Process(Thread, ABC):

    def __init__(self, name, bus_size):
        """
        Constructor of the class.
        :param name: (String) Name of the process P1 to Pn.
        :param bus_size: (Integer) Number of process in the bus.
        """
        Thread.__init__(self)

        self.setName(name)
        self.process_id = int(name[1:]) - 1
        self.communicator = Com(self.getName(), bus_size)
        self.alive = True

    @abstractmethod
    def process(self):
        pass

    def run(self):
        """
        Main loop of the process.
        """
        sleep(1)
        while self.alive:
            self.process()

        print(self.getName() + " stopped")

    def stop(self):
        """
        Stop the process.
        """
        self.communicator.token_thread.stop()
        self.alive = False
        self.join()
