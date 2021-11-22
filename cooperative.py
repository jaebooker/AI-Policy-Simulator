from simulation import *
from logger import *
from agent import *

class Cooperative(object):
    '''
    '''

    def __init__(self, _init_progress):
        # 
        # 
        self.progress = _init_progress
    #     self.members = []

    # def did_cooperate(self, agent):
    #     self.members.append(agent)
    #     self.progress += agent.progress

    # def did_defect(self, agent):
    #     self.members.remove(agent)
    #     self.progress -= agent.progress