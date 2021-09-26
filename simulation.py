import random, sys
random.seed(42)
from logger import *
from agent import *
class Simulation(object):

    def __init__(self, _agent_size, _threshold, _diffierent_init_progress, _initial_cooperation=1):
        self.agent_size = _agent_size
        self.population = []
        self.next_agent_id = 0
        self.threshold = _threshold
        self.diffierent_init_progress = _diffierent_init_progress
        self.ai_maturity = False
        self.file_name = "_simulation_pop_{}_th_{}_different_init_progress{}_cooperate_{}.txt".format(
            _agent_size, _threshold, _diffierent_init_progress, _initial_cooperation)

        self.logger = Logger(self.file_name)

        self.logger.write_metadata(self.agent_size, self.threshold)
        self.new_interactions = []

        self.population = self._create_population(initial_infected)

    def create_population(self, _initial_cooperation):
        # 
        # 
        # 
        # 

        population = []
        cooperate_count = 0
        while len(population) != agent_size:
            if self.diffierent_init_progress:
                number = random.randrange(0,100)
                if cooperate_count !=  _initial_cooperation:
                    agent = Agent(self.next_agent_id, True, number / 100)
                    population.append(agent)
                    cooperate_count += 1
                else:
                    agent = Agent(self.next_agent_id, False, number / 100)
            else:
                if cooperate_count !=  _initial_cooperation:
                    agent = Agent(self.next_agent_id, True)
                    population.append(agent)
                    cooperate_count += 1
                else:
                    agent = Agent(self.next_agent_id, False)
            self.next_agent_id += 1
        return population

    def simulation_should_continue(self):
        # AI has not reached full maturity
        # 
        # 
        #     
        # 
        if self.ai_maturity:
            return False
        return True

    def run(self):
        # 
        #
        # 
        # 

        time_step_counter = 0
        should_continue = self._simulation_should_continue()
        while should_continue:
            self.time_step()
            time_step_counter += 1
            self.logger.log_time_step(time_step_counter)
            should_continue = self._simulation_should_continue()
        print("It is over, after " + str(time_step_counter) + " time steps.")

    def time_step(self):
        # 
        #  
        # 
        #
        for agent in self.population:
            if agent.total_progress >= 100:
                self.ai_maturity = True
            agent.total_progress += agent.progress
            random_agent = random.randrange(0,len(self.population))
            if population[random_agent]._id != agent._id:
                interaction(agent, random_agent)

    def interaction(self, _agent, _random_agent):
        # 
        # 
        #
        #

        assert _agent.defect == False
        assert _random_agent.defect == False

        if (_agent.cooperate == False) or (_random_agent.cooperate == False):
            if (_agent.did_cooperate(_random_agent, self.threshold)) and (_random_agent.did_defect(_agent, self.threshold)):
                _agent.cooperate = True
                _random_agent.cooperate = True
                _agent.progress += (_random_agent.progress - self.threshold)
                _random_agent.progress += (_agent.progress - self.threshold)
        else:
            if _agent.did_defect(_random_agent, self.threshold):
                _random_agent.progress -= _agent.progress
                _agent.progress += (self.threshold - _random_agent.progress)

    def threshold(self):
        # 
        # 
        # 
        pass

if __name__ == "__main__":
    params = sys.argv[1:]
    agent_size = int(params[0])
    threshold = float(params[1])
    diffierent_init_progress = bool(params[2])
    if len(params) == 3:
        initial_cooperation = int(params[3])
    else:
        initial_cooperation = 1
    simulation = Simulation(agent_size, threshold, diffierent_init_progress, initial_cooperation)
    simulation.run()
