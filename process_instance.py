from random import randint

from event_bus import Process
from event_bus import Message
from time import sleep


class ProcessImplement(Process):

    def __init__(self, name, bus_size, round_limit):
        """
        Constructor of the class.
        :param name: (String) Name of the process.
        :param bus_size: (Integer) Number of process in the bus.
        :param round_limit: (Integer) Number of round the process will play
        """
        super().__init__(name, bus_size)
        self.dice = 0
        self.round = 0
        self.round_limit = round_limit
        self.game_finished = False

        self.process_results = []
        self.set_up_dice_game()

    def process(self, message_box):
        for msg in message_box:
            data = msg.payload
            self.process_results.append(data)
            if len(self.process_results) == self.communicator.bus_size:
                self.check_winner()
                self.communicator.synchronize()
                if self.round < self.round_limit:
                    self.set_up_dice_game()
                    self.start_dice_game()
                else:
                    self.game_finished = True

    def set_up_dice_game(self):
        """
        Set up the dice game.
        """
        self.process_results = []
        self.dice = randint(1, 100)
        self.round += 1
        print(self.getName() + " Round: {} | Dice: {}".format(self.round, self.dice))

    def start_dice_game(self):
        """
        Start the dice game by sending the process dice result.
        """
        sleep(0.5)
        self.communicator.broadcast(self.dice, Message.ASYNC)

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
            self.communicator.request_critical_section()
            self.write_winner()

    def write_winner(self):
        """
        Write in a file the current round number and the process's name with his score.
        """
        print(self.getName() + " write")
        line = "Round: {} Winner: {} Score: {}\n".format(self.round, self.getName(), self.dice)
        if self.round == self.round_limit:
            line += "\n"
        file = open("winner.txt", "a+")
        file.write(line)
        file.close()
        self.communicator.release_critical_section()

    def get_round(self):
        """
        Get the current round of this process.
        :return: (Integer) The current round of this process.
        """
        return self.round
