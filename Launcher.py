"""
File to run the TP.

Usage:
    Launcher.py <nb_process> <nb_round>

Options:
    -h --help           Show this screen.
    <nb_process>        Number of process.
    <nb_round>          Number of round.
"""
from event_bus.EventBus import EventBus
from event_bus.ProcessManager import ProcessManager
from docopt import docopt
from process_instance import ProcessImplement

NB_PROCESS = 0
NB_ROUND = 0


if __name__ == '__main__':
    arguments = docopt(__doc__)

    bus = EventBus.get_instance()
    process_manager = ProcessManager()
    NB_PROCESS = int(arguments["<nb_process>"])
    NB_ROUND = int(arguments["<nb_round>"])

    print("\n -> Dice (1 to 100)\n")
    process_manager.add_process(NB_PROCESS, ProcessImplement)
    process_manager.wait_round(NB_ROUND)

    process_manager.stop_process()
    bus.stop()
