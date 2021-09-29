from simulation import *
from agent import *

class Logger(object):
    '''
    Utility class responsible for logging all interactions of note during the
    simulation.


    _____Attributes______

    file_name: the name of the file that the logger will be writing to.

    _____Methods_____

    __init__(self, file_name):

    write_metadata
    '''

    def __init__(self, file_name):
        # full file name of the file that the logs will be written to.
        self.file_name = file_name

    def write_metadata(self, _agent_size, _threshold, _different_init_progress, _initial_cooperation):
        # logs number of agents and relevant details

        with open(self.file_name, "w") as f:
            f.write("Agents: {}\t Threshold: {}\t Different Initial Progress: {}\t Initial Cooperation: {}\n".format(_agent_size, _threshold, _different_init_progress, _initial_cooperation))
        f.closed
    def log_interaction(self, _agent1, _agent2, _type, _did_cooperate_or_defect):
        #logs if an agent defected or cooperated

        with open(self.file_name, "a") as f:
            f.write("Agent 1: {}\t Agent 2: {}\t {} : {} \n".format(_agent1._id, _agent2._id, _type, _did_cooperate_or_defect))
        f.closed

    def log_time_step(self, time_step_number):
        # logs each iteration

        with open(self.file_name, "a") as f:
            f.write("Time Steps: {}\n".format(time_step_number))
        f.closed

    def log_spy(self, _agent1, _agent2, _success, _amount):
        #logs spy activity

        with open(self.file_name, "a") as f:
            f.write("Spy: {}\t Spied on: {}\t Success {}\t Amount: {} \n".format(_agent1._id, _agent2._id, _success, _amount))
        f.closed