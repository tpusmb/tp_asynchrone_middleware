from random import randint

from event_bus import Process


class ProcessImplement(Process):

    def __init__(self, name, bus_size):
        """
        Constructor of the class.
        :param name: (String) Name of the process.
        :param bus_size: (Integer) Number of process in the bus.
        """
        super().__init__(name, bus_size)
        self.dice = 0
        self.round = 0

        self.process_results = []

    def process(self):
        print("Somting...")

    def dice_game(self):
        """
        Set up the dice game.
        """
        self.process_results = []
        self.dice = randint(1, 100)
        self.round += 1
        print(self.getName() + " Round: {} | Dice: {}".format(self.round, self.dice))
        # self.synchronize()

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
            # self.request()

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
