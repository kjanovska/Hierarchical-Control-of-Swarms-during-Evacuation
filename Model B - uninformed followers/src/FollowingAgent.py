from Agent import *
from Geometry import LFGeometry
import copy
import random


class FollowingAgent(Agent):
    def __init__(self, sight_length, obedience_level):
        super().__init__(sight_length=sight_length)
        self.evacuated = False
        self.sign = 'F'
        self.obedience_level = obedience_level
        self.leader_position = []
        self.iteration_number = 0
        self.last_known_leader_position = [0, 0]
        self.leader = None 
        self.known_exit = []

    def agent_function(self, state, leaders):
        self.leader_position = self.find_leader(leaders)
        if self.leader_position is None:
            return self.random_free_neighbour(state)
        geometry = LFGeometry(self.leader_position, self.position, state)
        if distance_from_agent(self.position, self.leader_position) > self.sight_length \
                or not geometry.agent1_sees_agent2():
            if self.last_known_leader_position is [0, 0]:
                return self.random_free_neighbour(state)
            else:
                self.leader_position = copy.deepcopy(self.last_known_leader_position)
                if random.randint(1, 100) > self.obedience_level:
                    return self.move_disobey(state)
                else:
                    return self.move_obey(state)
        if distance_from_agent(self.position, self.leader_position) < self.sight_length \
                and geometry.agent1_sees_agent2():
            self.last_known_leader_position = copy.deepcopy(self.leader_position)
        if random.randint(1, 100) > self.obedience_level:
            return self.move_disobey(state)
        else:
            return self.move_obey(state)

    def random_free_neighbour(self, state):
        possible_results = [self.position]
        if state[self.position[0]][self.position[1] + 1] == '.':
            possible_results.append([self.position[0], self.position[1] + 1])
        if state[self.position[0]][self.position[1] - 1] == '.':
            possible_results.append([self.position[0], self.position[1] - 1])
        if state[self.position[0] + 1][self.position[1]] == '.':
            possible_results.append([self.position[0] + 1, self.position[1]])
        if state[self.position[0] - 1][self.position[1]] == '.':
            possible_results.append([self.position[0] - 1, self.position[1]])
        return possible_results[random.randint(0, len(possible_results) - 1)]

    def random_next_follower(self, state, previous_follower):
        possible_results = []
        if state[self.position[0]][self.position[1] + 1] == 'F' and [[self.position[0]], [self.position[1] + 1]] != previous_follower:
            possible_results.append([self.position[0], self.position[1] + 1])
        if state[self.position[0]][self.position[1] - 1] == 'F' and [[self.position[0]], [self.position[1] - 1]] != previous_follower:
            possible_results.append([self.position[0], self.position[1] - 1])
        if state[self.position[0] + 1][self.position[1]] == 'F' and [[self.position[0] + 1], [self.position[1]]] != previous_follower:
            possible_results.append([self.position[0] + 1, self.position[1]])
        if state[self.position[0] - 1][self.position[1]] == 'F' and [[self.position[0] - 1], [self.position[1]]] != previous_follower:
            possible_results.append([self.position[0] - 1, self.position[1]])
        if possible_results:
            return possible_results[random.randint(0, len(possible_results) - 1)]
        return None

    def move_obey(self, state):
        possible_results = []
        if state[self.position[0]][self.position[1] + 1] == '.' \
                and self.is_closer([self.position[0], self.position[1] + 1]):
            possible_results.append([self.position[0], self.position[1] + 1])
        if state[self.position[0]][self.position[1] - 1] == '.' \
                and self.is_closer([self.position[0], self.position[1] - 1]):
            possible_results.append([self.position[0], self.position[1] - 1])
        if state[self.position[0] + 1][self.position[1]] == '.' \
                and self.is_closer([self.position[0] + 1, self.position[1]]):
            possible_results.append([self.position[0] + 1, self.position[1]])
        if state[self.position[0] - 1][self.position[1]] == '.' \
                and self.is_closer([self.position[0] - 1, self.position[1]]):
            possible_results.append([self.position[0] - 1, self.position[1]])
        if len(possible_results) == 1:
            return possible_results[0]
        elif len(possible_results) == 0:
            return self.position
        return possible_results[random.randint(0, len(possible_results) - 1)]

    def move_disobey(self, state):
        possible_results = [self.position]
        if state[self.position[0]][self.position[1] + 1] == '.' \
                and not self.is_closer([self.position[0], self.position[1] + 1]):
            possible_results.append([self.position[0], self.position[1] + 1])
        if state[self.position[0]][self.position[1] - 1] == '.' \
                and not self.is_closer([self.position[0], self.position[1] - 1]):
            possible_results.append([self.position[0], self.position[1] - 1])
        if state[self.position[0] + 1][self.position[1]] == '.' \
                and not self.is_closer([self.position[0] + 1, self.position[1]]):
            possible_results.append([self.position[0] + 1, self.position[1]])
        if state[self.position[0] - 1][self.position[1]] == '.' \
                and not self.is_closer([self.position[0] - 1, self.position[1]]):
            possible_results.append([self.position[0] - 1, self.position[1]])
        return possible_results[random.randint(0, len(possible_results) - 1)]

    """
    compare if selected position is closer to agent's leader then agent's current position
    """
    def is_closer(self, new_position):
        return distance_from_agent(self.position, self.leader_position) \
               > distance_from_agent(new_position, self.leader_position)

    """
    return position of agent's leader
    """
    def find_leader(self, leaders):
        if self.leader is None:
            return None
        return leaders[self.leader].position