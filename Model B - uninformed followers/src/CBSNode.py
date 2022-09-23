from Agent import copy

class CBSNode:
    def __init__(self, state, agents, followers):
        self.state = state
        self.agents = agents
        self.constraints = []  # constraint = tuple (agent, vertex, time)
        self.solution = []  # set of k paths, one for each agent
        self.cost = 0  # f-value of node
        self.followers = followers

    """
    find base solution (list of agent paths) for all agents with set constraints
    """
    def find_individual_paths(self):
        self.solution = []
        for agent in self.agents:
            if not agent.evacuated:
                self.solution.append(copy.deepcopy(agent.find_path(self.state, self.constraints, self.followers, 1)))
            else:
                self.solution.append([agent.position, agent.position])

    """
    update path for a certain agent after adding a constraint
    """
    def update_solution(self, agent_number, previous_solution):
        # constraints have already been updated
        tmp_solution = []
        for index, agent in enumerate(self.agents):
            if index == agent_number:
                tmp_solution.append(copy.deepcopy(agent.find_path(self.state, self.constraints, self.followers, 2)))
            else:
                tmp_solution.append(previous_solution[index])
        self.solution = tmp_solution

    """
    return sum of path lengths = cost of a node
    """
    def compute_cost(self):
        for i in self.solution:
            self.cost += len(i)

    """
    if some of the agents were already waiting too long at the beginning of the CBS, they have planned their next step - different from their current position
    thus setting agent.time_since_moved to zero is necessary - this method is needed for the agents using CBS won't do it themselves
    """
    def forced_move_zero(self):
        for agent in self.agents:
            if agent.time_since_moved >= 26:
                agent.time_since_moved = 0