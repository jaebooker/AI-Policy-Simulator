import random, sys
random.seed(42)
from logger import *
from agent import *
class Simulation(object):

    def __init__(self, _agent_size, _threshold, _initial_cooperation=1):
        self.agent_size = _agent_size
        self.population = []
        self.next_agent_id = 0
        self.threshold = _threshold
        self.file_name = "_simulation_pop_{}_th_{}_cooperate_{}.txt".format(
            _agent_size, _threshold, _initial_cooperation)

        self.logger = Logger(self.file_name)

        self.logger.write_metadata(self.agent_size, self.threshold)
        self.new_interactions = []

        self.population = self._create_population(initial_infected)

    def _create_population(self, initial_infected):
        # 
        # 
        # 
        # 

        population = []
        cooperate_count = 0
        while len(population) != agent_size:
            if cooperate_count !=  _initial_cooperation:
                agent = Agent(self.next_agent_id, True)
                population.append(agent)
                cooperate_count += 1
            else:
                number = random.randrange(0,100)
                if (number / 100) < self.threshold:
                    agent = Agent(self.next_agent_id, False)
                elif (number / 100) >= self.threshold:
                    agent = Agent(self.next_agent_id, True)
                population.append(agent)
            self.next_agent_id += 1
        return population

    def _simulation_should_continue(self):
        # 
        # 
        # 
        #     
        # 

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

    def interaction(self, person, random_agent):
        # 
        # 
        #
        #

        assert person.cooperate == True
        assert random_person.cooperate == False

    def _threshold(self):
        # 
        # 
        # 

if __name__ == "__main__":
    params = sys.argv[1:]
    agent_size = int(params[0])
    threshold = float(params[1])
    if len(params) == 2:
        initial_cooperation = int(params[2])
    else:
        initial_cooperation = 1
    simulation = Simulation(agent_size, threshold, initial_cooperation)
    simulation.run()
