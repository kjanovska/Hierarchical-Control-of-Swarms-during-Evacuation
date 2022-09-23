from CBSNode import CBSNode
from Geometry import LLGeometry
from Agent import *


def lowest_cost_node(open_nodes):
    return min(open_nodes, key=lambda o_n: o_n.cost)


def new_constraint(agent, vertex, time):
    constraint = (agent, vertex, time)
    return constraint


"""
return a list of all first conflicts between each pair of agents
"""
def first_conflicts(best_node, agents):
    first_conflicts = []
    for index, agent1 in enumerate(best_node.solution):
        if not agents[index].evacuated:
            for agent2_number in range(index + 1, len(best_node.solution)):
                if not agents[agent2_number].evacuated:
                    number_of_steps = min(len(agent1), len(best_node.solution[agent2_number]))
                    for step in range(0, number_of_steps):
                        geometry = LLGeometry(agent1[step], best_node.solution[agent2_number][step], best_node.state,
                                              agents[index].conflict_distance)
                        if geometry.agent1_sees_agent2() and distance_from_agent(agents[index].position, agents[
                            index].exit) >= 5 and distance_from_agent(agents[agent2_number].position,
                                                                      agents[agent2_number].exit) >= 5:
                            first_conflicts.append(
                                (index, agent2_number, agent1[step], best_node.solution[agent2_number][step], step))
                            break
    return first_conflicts


"""
return nearest occuring conflict
"""
def validate(best_node, agents):
    first_conflicts_list = first_conflicts(best_node, agents)
    if len(first_conflicts_list) > 0:
        nearest_conflict = first_conflicts_list[0]
        for conflict in first_conflicts_list:
            if conflict[4] < nearest_conflict[4]:
                nearest_conflict = conflict
        return nearest_conflict
    else:
        return first_conflicts_list


class CBSTree:
    def __init__(self, state, agents, followers):
        self.state = state
        self.nodes = [CBSNode(state, agents, followers)]  # list of nodes containing only the root
        self.followers = followers
        self.agents = agents

    def cbs(self):
        counter = 0
        self.nodes[0].find_individual_paths()  # find a path for EACH agent = low level
        self.nodes[0].compute_cost()  # find the cost of a node
        open_nodes = [self.nodes[0]]
        c = 1
        while len(open_nodes) > 0:
            if counter >= 5:
                new_best_node = lowest_cost_node(open_nodes)
                first_constraints = first_conflicts(new_best_node, self.agents)
                for constraint in first_constraints:
                    for i in {0, 1}:
                        if (constraint[i], constraint[i + 2], constraint[4]) not in new_best_node.constraints:
                            new_best_node.constraints.append((constraint[i], constraint[i + 2], constraint[4]))
                            new_best_node.update_solution(constraint[i], new_best_node.solution)
                return new_best_node.solution
            best_node = lowest_cost_node(open_nodes)  # finds and pops solution with the lowest cost
            open_nodes.remove(best_node)
            first_conflict = validate(best_node, self.agents)  # find conflicts in the best solution
            if len(first_conflict) == 0:  # no conflicts were found -> solution is valid
                return best_node.solution
            new_nodes = [CBSNode(best_node.state, best_node.agents, self.followers) for i in range(2)]
            for index, new_node in enumerate(new_nodes):
                new_node.constraints = copy.deepcopy(best_node.constraints)
                if (first_conflict[index], first_conflict[index + 2], first_conflict[4]) not in new_node.constraints:
                    new_node.constraints.append((first_conflict[index], first_conflict[index + 2], first_conflict[4]))
                new_node.update_solution(first_conflict[index], best_node.solution)
                new_node.compute_cost()
                open_nodes.append(new_node)
                c += 1
            counter += 1
