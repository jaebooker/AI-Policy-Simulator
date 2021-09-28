import random, sys
random.seed(42)
# from logger import *
from agent import *
class Simulation(object):

    def __init__(self, _agent_size, _threshold, _different_init_progress, _initial_cooperation):
        self.agent_size = _agent_size
        self.population = []
        self.next_agent_id = 0
        self.threshold = _threshold
        self.different_init_progress = _different_init_progress
        self.initial_cooperation = _initial_cooperation
        self.ai_maturity = False
        self.file_name = "_simulation_pop_{}_th_{}_different_init_progress{}_cooperate_{}.txt".format(
            _agent_size, _threshold, _different_init_progress, _initial_cooperation)

        self.logger = Logger(self.file_name)

        self.logger.write_metadata(self.agent_size, self.threshold, self.different_init_progress, self.initial_cooperation)
        self.new_interactions = []

        self.population = self.create_population(agent_size)

    def create_population(self, agent_size):
        # creates an array of all agents
        # creates agent models
        # assigns pre-defined number of cooperating agents
        # gives ranomized progress states, if different initial levels of progress

        population = []
        cooperate_count = 0
        while len(population) != agent_size:
            if self.different_init_progress:
                number = random.randrange(0,100)
                if cooperate_count !=  self.initial_cooperation:
                    agent = Agent(self.next_agent_id, True, number / 100)
                    population.append(agent)
                    cooperate_count += 1
                else:
                    agent = Agent(self.next_agent_id, False, number / 100)
                    population.append(agent)
            else:
                if cooperate_count !=  self.initial_cooperation:
                    agent = Agent(self.next_agent_id, True)
                    population.append(agent)
                    cooperate_count += 1
                else:
                    agent = Agent(self.next_agent_id, False)
                    population.append(agent)
            self.next_agent_id += 1
        return population

    def simulation_should_continue(self):
        # Checks if AI has reached AGI level
        # If not, continues to run simulation
        if self.ai_maturity:
            return False
        return True

    def run(self):
        # sets timesteps
        # checks if simulation should continue
        # runs iteration

        time_step_counter = 0
        should_continue = self.simulation_should_continue()
        while should_continue:
            self.time_step()
            time_step_counter += 1
            self.logger.log_time_step(time_step_counter)
            should_continue = self.simulation_should_continue()
        print("It is over, after " + str(time_step_counter) + " time steps.")

    def time_step(self):
        # checks if AI has reached AGI level
        # iterates through agents
        # gives random interaction between agents

        for agent in self.population:
            if agent.total_progress >= 100:
                self.ai_maturity = True
            agent.total_progress += agent.progress
            random_agent = random.randrange(0,len(self.population))
            if self.population[random_agent]._id != agent._id:
                self.interaction(agent, self.population[random_agent])

    def interaction(self, _agent, _random_agent):
        # checks if either agent has yet defected
        # checks if both agents are already cooperating
        # if only one agent is currently cooperate, checks to see if other agent will cooperate
        # if true, adjusts progress levels
        # if both agents are cooperating, checks if one agent will defect, and adjusts progress

        if (_agent.defect == False) and (_random_agent.defect == False):

            if (_agent.cooperate == False) and (_random_agent.cooperate == True):
                if _agent.did_cooperate(_random_agent, self.threshold):
                    _agent.cooperate = True
                    _random_agent.cooperate = True
                    _agent.progress += (_random_agent.progress - self.threshold)
                    _random_agent.progress += (_agent.progress)
                self.logger.log_interaction(_agent, _random_agent, "cooperate", _agent.cooperate)
            if (_agent.cooperate == True) and (_random_agent.cooperate == True):
                if _agent.did_defect(_random_agent, self.threshold):
                    _random_agent.progress -= _agent.progress
                    _agent.progress += (self.threshold - _random_agent.progress)
                self.logger.log_interaction(_agent, _random_agent, "defect", _agent.defect)

    def threshold(self):
        # 
        # 
        # 
        pass

if __name__ == "__main__":
    params = sys.argv[1:]
    agent_size = int(params[0])
    threshold = float(params[1])
    different_init_progress = bool(params[2])
    initial_cooperation = int(params[3])
    simulation = Simulation(agent_size, threshold, different_init_progress, initial_cooperation)
    simulation.run()
