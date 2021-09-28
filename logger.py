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
        # 
        # 
        # 
        with open(self.file_name, "w") as f:
            f.write("Agents: {}\t Threshold: {}\t Different Initial Progress: {}\t Initial Cooperation: {}\n".format(_agent_size, _threshold, _different_init_progress, _initial_cooperation))
        f.closed
    def log_interaction(self, _agent1, _agent2, _type, _did_cooperate_or_defect):
        with open(self.file_name, "a") as f:
            f.write("Agent 1: {}\t Agent 2: {}\t {} : {} \n".format(_agent1._id, _agent2._id, _type, _did_cooperate_or_defect))
        f.closed

    def log_time_step(self, time_step_number):
        # 
        # 
        with open(self.file_name, "a") as f:
            f.write("Time Steps: {}\n".format(time_step_number))
        f.closed
