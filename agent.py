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


    def did_cooperate(self, _threshold):
        # 
        # 
        # 
        number = random.randrange(0,100)
        if (number / 100) < _threshold:
            self.cooperate = False
            return False
        elif (number / 100) >= _threshold:
            return True
        else:
            pass
