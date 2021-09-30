import simulation
import logger
import agent

def _test_simulation():
    agent_size = 20
    threshold = .90
    initial_cooperation = 10
    diffierent_init_progress = True
    simulation = Simulation(agent_size, threshold, different_init_progress, initial_cooperation, 0, 0)
    simulation.run()
