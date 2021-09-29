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

    def __init__(self, _id, _cooperate, _progress, _spy, _imposter):
        # 
        # to set the correct values for the following attributes.
        self._id = _id
        self.cooperate = _cooperate
        self.progress = _progress
        self.defect = False
        self.total_progress = _progress
        self.spy = _spy
        self.imposter = _imposter


    def did_cooperate(self, _random_agent, _threshold):
        # checks if it is in agent's interest to cooperate
        # checks if progress gained by cooperating is greater than loss of progress from complying to AI Safety measures

        if self.imposter:
            return True

        if _random_agent.progress < (self.progress + _threshold):
            return False
        elif _random_agent.progress >= (self.progress + _threshold):
            return True
    
    def did_defect(self, _random_agent, _threshold):
        # checks if it is in agent's best interest to defect
        # checks if progress gained by defecting is greater than progress from cooperating

        if (self.cooperate) and (_random_agent.cooperate):
            if _random_agent.progress < (self.progress + _threshold):
                self.defect = True
                self.cooperate = False
                return True
            elif _random_agent.progress >= (self.progress + _threshold):
                return False

    def spying(self, random_agent):
        odds = random.randrange(0,100)
        if odds >= 80:
            return True
        return False

    def did_get_caught(self):
        odds = random.randrange(0,100)
        if odds >= 80:
            self.defect = True
            self.imposter = False
            self.spy = False
            return True
        return False