from threading import Thread
from time import sleep

from .Com import Com
from random import randint


class Process(Thread):

    def __init__(self, name, bus_size):
        """
        Constructor of the class.
        :param name: (String) Name of the process.
        :param bus_size: (Integer) Number of process in the bus.
        """
        Thread.__init__(self)

        self.setName(name)
        self.communicator = Com(self.getName(), bus_size)

        self.alive = True
        self.dice = 0
        self.round = 0

        self.process_results = []

        self.start()

    def process(self, event):
        """
        Function to receive an event and handle his message.
        :param event: (Event) Event that contains the topic and the message.
        """
        self.communicator.receive(event)

    def run(self):
        """
        Main loop of the process.
        """
        sleep(1)
        # self.dice_game()
        loop = 0
        while self.alive:
            sleep(1)
            self.communicator.broadcast("heartbit")

        print(self.getName() + " stopped")

    def dice_game(self):
        """
        Set up the dice game.
        """
        self.process_results = []
        self.dice = randint(1, 100)
        self.round += 1
        print(self.getName() + " Round: {} | Dice: {}".format(self.round, self.dice))
        self.synchronize()

    def stop(self):
        """
        Stop the process.
        """
        self.alive = False
        self.join()

    def check_winner(self):
        """
        Find out if the process has the higer dice score and ask for the token if so.
        """
        higer_result = 0
        for i in range(0, len(self.process_results)):
            if self.process_results[i] > higer_result:
                higer_result = self.process_results[i]
        if self.dice >= higer_result:
            print(self.getName() + " is the winner with: {}".format(self.dice))
            self.request()

    def write_winner(self):
        """
        Write in a file the current round number and the process's name with his score.
        """
        print(self.getName() + " write")
        file = open("winner.txt", "a+")
        file.write("Round: {} Winner: {} Score: {}\n".format(self.round, self.getName(), self.dice))
        file.close()

    def get_round(self):
        """
        Get the current round of this process.
        :return: (Integer) The current round of this process.
        """
        return self.round

