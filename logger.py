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

    def write_metadata(self, _agent_size, _threshold, initial_cooperation):
        # 
        # 
        # 
        with open(self.file_name, "w") as f:
            f.write("Agents: {}\t Threshold: {}\t Number cooperating: {}\n".format(_agent_size, _threshold, _initial_cooperation))
        f.closed
    def log_interaction(self, agent1, agent2, _did_cooperate):
        with open(self.file_name, "a") as f:
            f.write("Agent 1: {}\t Agent 2: {}\t Did cooperate: \n".format(agent1._id, agent2._id, _did_cooperate))
        f.closed

    def log_time_step(self, time_step_number):
        # 
        # 
        with open(self.file_name, "a") as f:
            f.write("Time Steps: {}\n".format(time_step_number))
        f.closed
