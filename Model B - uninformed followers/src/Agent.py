from Architecture import *
from Square import Square
import math
import copy

"""
return distance between two agents
"""
def distance_from_agent(position, agent2_position):
    return math.sqrt(pow(position[0] - agent2_position[0], 2) + pow(position[1] - agent2_position[1], 2))


class Agent:

    """
    init variables common for both leaders and followers
    """
    def __init__(self, sight_length):
        self.sight_length = sight_length
        self.position = []

    """
    return map with cells represented by Square - for A*
    """
    def fill_state(self, state):
        squares = [[Square() for i in range(len(state[0]))] for j in range(len(state))]
        for row in range(0, len(state)):
            for column in range(0, len(state[0])):
                squares[row][column].sign = copy.deepcopy(state[row][column])
                squares[row][column].state = 'FRESH'
                if state[row][column] == '@':
                    squares[row][column].state = 'CLOSED'
                squares[row][column].x_pos = row
                squares[row][column].y_pos = column
        return squares
