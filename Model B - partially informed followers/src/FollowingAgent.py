from Agent import *
from Geometry import LFGeometry
from Square import Square
import copy
import random


class FollowingAgent(Agent):
    def __init__(self, sight_length, obedience_level):
        super().__init__(sight_length=sight_length)
        self.evacuated = False
        self.sign = 'F'
        self.obedience_level = obedience_level
        self.leader_position = []
        self.last_known_leader_position = [0, 0]
        self.time_since_seen_leader = 0
        self.leader = None
        self.known_exit = [0, 0]

    def agent_function(self, state, leaders):
        self.leader_position = self.find_leader(leaders)
        if self.leader_position is None:
            self.time_since_seen_leader += 1
            if self.time_since_seen_leader > 30:
                return self.bfs(state)
            return self.random_free_neighbour(state)
        geometry = LFGeometry(self.leader_position, self.position, state)
        if distance_from_agent(self.position, self.leader_position) > self.sight_length or not geometry.agent1_sees_agent2():
            self.time_since_seen_leader += 1
            if self.time_since_seen_leader > 30:
                return self.bfs(state)
            if self.last_known_leader_position is [0, 0]:
                return self.random_free_neighbour(state)
            else:
                self.leader_position = copy.deepcopy(self.last_known_leader_position)
                if random.randint(1, 100) > self.obedience_level:
                    return self.move_disobey(state)
                else:
                    return self.move_obey(state)
        if distance_from_agent(self.position, self.leader_position) < self.sight_length and geometry.agent1_sees_agent2():
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
        return distance_from_agent(self.position, self.leader_position) \
               > distance_from_agent(new_position, self.leader_position)

    """
    return position of agent's leader
    """
    def find_leader(self, leaders):
        if self.leader is None:
            return None
        return leaders[self.leader].position
    
    def bfs(self, state):
        open_squares = []
        squares = self.fill_state(state)
        predecessor_tab = [[Square() for i in range(len(state[0]))] for j in range(len(state))]
        working_square = copy.deepcopy(squares[self.position[0]][self.position[1]])
        
        squares[self.position[0]][self.position[1]].state = 'OPEN'
        working_square.state = 'OPEN'
        working_square.x_pos = self.position[0]
        working_square.y_pos = self.position[1]
        working_square.len_from_start = 0
        open_squares.append(working_square)
        while not len(open_squares) == 0:
            working_square = open_squares.pop(0)
            if working_square.x_pos == self.known_exit[0] and working_square.y_pos == self.known_exit[1]:
                return self.first_predecessor(working_square, predecessor_tab)
            self.search_left(squares, open_squares, working_square, predecessor_tab)
            self.search_right(squares, open_squares, working_square, predecessor_tab)
            self.search_top(squares, open_squares, working_square, predecessor_tab)
            self.search_bottom(squares, open_squares, working_square, predecessor_tab)
            working_square.state = 'CLOSED'
            squares[working_square.x_pos][working_square.y_pos].state = 'CLOSED'
        return self.first_predecessor(working_square, predecessor_tab)

    """
    find the next move for a follower according to the predecessor table
    """
    def first_predecessor(self, working_square, predecessor_tab):
        all_positions = []
        actual_x = working_square.x_pos
        actual_y = working_square.y_pos
        if predecessor_tab[actual_x][actual_y].x_pos == 0 and predecessor_tab[actual_x][actual_y].y_pos == 0:
            return self.position
        while not (actual_x == self.position[0] and actual_y == self.position[1]):
            predecessor_x = predecessor_tab[actual_x][actual_y].x_pos
            predecessor_y = predecessor_tab[actual_x][actual_y].y_pos
            all_positions.append([predecessor_x, predecessor_y])
            if predecessor_x == self.position[0] and predecessor_y == self.position[1]:
                all_positions.reverse()
                if len(all_positions) > 1:
                    return all_positions[1]
                else:
                    return self.position
            actual_x = predecessor_x
            actual_y = predecessor_y
        all_positions.reverse()
        if len(all_positions) > 1:
            return all_positions[1]
        else:
            return self.position

    def search_left(self, squares, open_squares, working_square, predecessor_tab):
        left_x = working_square.x_pos
        left_y = working_square.y_pos - 1
        self.square_movement(squares, open_squares, working_square, predecessor_tab, [left_x, left_y])

    def search_right(self, squares, open_squares, working_square, predecessor_tab):
        right_x = working_square.x_pos
        right_y = working_square.y_pos + 1
        self.square_movement(squares, open_squares, working_square, predecessor_tab, [right_x, right_y])

    def search_top(self, squares, open_squares, working_square, predecessor_tab):
        top_x = working_square.x_pos - 1
        top_y = working_square.y_pos
        self.square_movement(squares, open_squares, working_square, predecessor_tab, [top_x, top_y])

    def search_bottom(self, squares, open_squares, working_square, predecessor_tab):
        bottom_x = working_square.x_pos + 1
        bottom_y = working_square.y_pos
        self.square_movement(squares, open_squares, working_square, predecessor_tab, [bottom_x, bottom_y])

    """
    plan a move and update the node and the predecessor table
    """
    def square_movement(self, squares, open_squares, working_square, predecessor_tab, new_position):
        if squares[new_position[0]][new_position[1]].state != 'FRESH':
            return
        if squares[new_position[0]][new_position[1]].sign == '@':
            return
        if new_position[0] == working_square.x_pos and new_position[1] == working_square.y_pos:
            return
        squares[new_position[0]][new_position[1]].state = 'OPEN'
        neighbour_square = Square()
        neighbour_square.x_pos = new_position[0]
        neighbour_square.y_pos = new_position[1]
        neighbour_square.len_from_start = working_square.len_from_start + 1
        predecessor_tab[neighbour_square.x_pos][neighbour_square.y_pos] = working_square
        neighbour_square.state = 'OPEN'
        open_squares.append(neighbour_square)
