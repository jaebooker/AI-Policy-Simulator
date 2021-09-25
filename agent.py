import random
from simulation import *
from logger import *

class Agent(object):
    '''
    Agent objects will populate the simulation.

    _____Attributes______:

    _id: Int.  A unique ID assigned to each agent

    _____Methods_____:

    __init__(self, _id):
        explanation
    '''

    def __init__(self, _id, _cooperate=True, _progress=1):
        # 
        # to set the correct values for the following attributes.
        self._id = _id
        self.cooperate = _cooperate
        self.progress = _progress
        self.defect = False
        self.total_progress = _progress


    def did_cooperate(self, _random_agent, _threshold):
        # 
        # 
        # 
        if _random_agent.progress < (self.progress + _threshold):
            return False
        elif _random_agent.progress >= (self.progress + _threshold):
            return True
    
    def did_defect(self, _random_agent, _threshold):
        #
        #
        #
        if (self.cooperate = True) and (_random_agent.cooperate = True):
            if _random_agent.progress < (self.progress + _threshold):
                self.defect = True
                self.cooperate = False
                return True
            elif _random_agent.progress >= (self.progress + _threshold):
                return False