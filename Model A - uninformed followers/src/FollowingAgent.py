from Agent import *
from Agent import Agent
from Geometry import LFGeometry
import copy
import random


class FollowingAgent(Agent):
    def __init__(self, sight_length, obedience_level):
        super().__init__(sight_length=sight_length)
        self.evacuated = False
        self.sign = 'F'
        self.obedience_level = obedience_level
        self.closest_leader_position = []
        self.last_known_leader_position = [0, 0]
        self.time_since_seen_leader = 0
        self.known_exit = [0, 0]

    def agent_function(self, state, leaders):
        self.choose_nearest_leader(leaders)
        geometry = LFGeometry(self.closest_leader_position, self.position, state)
        if distance_from_agent(self.position, self.closest_leader_position) > self.sight_length \
        or not geometry.agent1_sees_agent2():
            self.time_since_seen_leader += 1
            if self.time_since_seen_leader > 30 or self.last_known_leader_position == [0, 0]:
                return self.random_free_neighbour(state)
            else:
                self.closest_leader_position = copy.deepcopy(self.last_known_leader_position)
                if random.randint(1, 100) > self.obedience_level:
                    return self.move_disobey(state)
                else:
                    return self.move_obey(state)
        if distance_from_agent(self.position, self.closest_leader_position) < self.sight_length \
            and geometry.agent1_sees_agent2():
            self.last_known_leader_position = copy.deepcopy(self.closest_leader_position)
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
        if state[self.position[0]][self.position[1] + 1] == 'F' and [[self.position[0]], [self.position[1] + 1]] not in previous_follower:
            possible_results.append([self.position[0], self.position[1] + 1])
        if state[self.position[0]][self.position[1] - 1] == 'F' and [[self.position[0]], [self.position[1] - 1]] not in previous_follower:
            possible_results.append([self.position[0], self.position[1] - 1])
        if state[self.position[0] + 1][self.position[1]] == 'F' and [[self.position[0] + 1], [self.position[1]]] not in previous_follower:
            possible_results.append([self.position[0] + 1, self.position[1]])
        if state[self.position[0] - 1][self.position[1]] == 'F' and [[self.position[0] - 1], [self.position[1]]] not in previous_follower:
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
        return distance_from_agent(self.position, self.closest_leader_position) \
               > distance_from_agent(new_position, self.closest_leader_position)

    def choose_nearest_leader(self, leaders):
        lowest_distance = float('inf')
        for leader in leaders:
            if distance_from_agent(self.position, leader.position) < lowest_distance:
                lowest_distance = distance_from_agent(self.position, leader.position)
                self.closest_leader_position = leader.position

 