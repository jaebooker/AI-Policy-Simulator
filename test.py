import simulation
import logger
import agent

def _test_simulation():
    agent_size = 20
    threshold = .90
    initial_cooperation = 10
    simulation = Simulation(agent_size, threshold, initial_cooperation)
    simulation.run()
