from Agent import Agent, copy, distance_from_agent
from Agent import *
from Square import Square
from Geometry import *
import heapq


class LeadingAgent(Agent):
    def __init__(self, sight_length, agent_number, min_swarm_denominator, conflict_distance, exits):
        super().__init__(sight_length=sight_length)
        self.evacuated = False
        self.sign = 'L'
        self.agent_number = agent_number
        self.constraints = []
        self.swarm = []
        self.last_number_of_followers = 0
        self.time_since_moved = 0
        self.min_swarm_denominator = min_swarm_denominator
        self.conflict_distance = conflict_distance
        self.forced_move = False
        self.all_exits = exits
        self.exit = []


    """
    choose agent's constraints from a list of all constraints
    """
    def choose_own_constraints(self, all_constraints):
        self.constraints = []
        for constraint in all_constraints:
            if constraint[0] == self.agent_number:
                self.constraints.append(constraint)

    """
    reconstruct agent's path from predecessor table
    """
    def create_path(self, predecessor_tab):
        all_positions = []
        actual_x = self.exit[0]
        actual_y = self.exit[1]
        if predecessor_tab[actual_x][actual_y].x_pos == 0 and predecessor_tab[actual_x][actual_y].y_pos == 0:
            print(self.position)
            return [self.position, self.position] # if the agent didn't find a way, it doesn't move
        while not (actual_x == self.position[0] and actual_y == self.position[1]):
            predecessor_x = predecessor_tab[actual_x][actual_y].x_pos
            predecessor_y = predecessor_tab[actual_x][actual_y].y_pos
            all_positions.append([predecessor_x, predecessor_y])
            if predecessor_x == self.position[0] and predecessor_y == self.position[1]:
                all_positions.reverse()
                return copy.deepcopy(all_positions)
            actual_x = predecessor_x
            actual_y = predecessor_y
        all_positions.reverse()
        return copy.deepcopy(all_positions)

    """
    agent function - A* algorithm modified so the agent will be considerate about its followers
    """
    def find_path(self, state, all_constraints, followers, is_cbs):
        self.choose_own_constraints(all_constraints)
        squares = self.fill_state(state)
        self.find_exit()
        open_squares = []
        predecessor_tab = [[Square() for i in range(len(state[0]))] for j in range(len(state))]
        working_square = copy.deepcopy(squares[self.position[0]][self.position[1]])
        squares[self.position[0]][self.position[1]].state = 'OPEN'
        working_square.state = 'OPEN'
        working_square.x_pos = self.position[0]
        working_square.y_pos = self.position[1]
        working_square.len_from_start = 0
        working_square.heuristics = self.heuristics(working_square)

        heapq.heapify(open_squares)
        heapq.heappush(open_squares, working_square)
        
        if not self.check_swarm(state, followers, is_cbs) and self.time_since_moved < 25 and not self.is_swarm_evacuated(state, followers):
            if is_cbs < 2:
                self.time_since_moved += 1
            return [self.position, self.position, self.position, self.position, self.position]

        if (not self.check_swarm(state, followers, is_cbs) and self.time_since_moved >= 25) or self.forced_move or self.is_swarm_evacuated(state, followers):
            if is_cbs < 2:
                self.time_since_moved = 26
                self.forced_move = False

        if is_cbs < 1:
            self.time_since_moved = 0

        while not len(open_squares) == 0:
            working_square = heapq.heappop(open_squares)  # pop and return smallest item from heap
            if working_square.x_pos == self.exit[0] and working_square.y_pos == self.exit[1]:
                return copy.deepcopy(self.create_path(predecessor_tab))
            self.search_left_neighbour(working_square, squares, open_squares, predecessor_tab)
            self.search_right_neighbour(working_square, squares, open_squares, predecessor_tab)
            self.search_top_neighbour(working_square, squares, open_squares, predecessor_tab)
            self.search_bottom_neighbour(working_square, squares, open_squares, predecessor_tab)
            squares[working_square.x_pos][working_square.y_pos].state = 'CLOSED'
        return copy.deepcopy(self.create_path(predecessor_tab))

    def search_neighbour_common(self, working_square, squares, open_squares, predecessor_tab, new_position):
        new_distance = working_square.len_from_start + 1
        if squares[new_position[0]][new_position[1]].sign == '@' or squares[new_position[0]][new_position[1]].sign == 'S' or self.is_position_constrained(new_position,
                                                                                                 new_distance):
            return
        if squares[new_position[0]][new_position[1]].len_from_start > new_distance or squares[new_position[0]][new_position[1]].state == 'FRESH':
            squares[new_position[0]][new_position[1]].len_from_start = new_distance
            self.square_movement(squares, open_squares, working_square, new_position, predecessor_tab)

    def search_bottom_neighbour(self, working_square, squares, open_squares, predecessor_tab):
        bottom_x = working_square.x_pos + 1
        bottom_y = working_square.y_pos
        self.search_neighbour_common(working_square, squares, open_squares, predecessor_tab, [bottom_x, bottom_y])

    def search_left_neighbour(self, working_square, squares, open_squares, predecessor_tab):
        left_x = working_square.x_pos
        left_y = working_square.y_pos - 1
        self.search_neighbour_common(working_square, squares, open_squares, predecessor_tab, [left_x, left_y])

    def search_right_neighbour(self, working_square, squares, open_squares, predecessor_tab):
        right_x = working_square.x_pos
        right_y = working_square.y_pos + 1
        self.search_neighbour_common(working_square, squares, open_squares, predecessor_tab, [right_x, right_y])

    def search_top_neighbour(self, working_square, squares, open_squares, predecessor_tab):
        top_x = working_square.x_pos - 1
        top_y = working_square.y_pos
        self.search_neighbour_common(working_square, squares, open_squares, predecessor_tab, [top_x, top_y])

    def find_exit(self):
        init_distance = float("inf")
        tmp_best_exit = []
        for exit in self.all_exits:
            if distance_from_agent(self.position, exit) < init_distance:
                tmp_best_exit = copy.deepcopy(exit)
                init_distance = distance_from_agent(self.position, exit)
        self.exit = tmp_best_exit

    def heuristics(self, square):
        return abs(self.exit[0] - square.x_pos + self.exit[1] - square.y_pos)

    def is_position_constrained(self, position, iteration_number):
        for constraint in self.constraints:
            if (self.agent_number, position, iteration_number) == constraint and iteration_number > 0:
                return True
        return False

    def square_movement(self, squares, open_squares, working_square, new_position, predecessor_tab):
        if squares[new_position[0]][new_position[1]].state == 'OPEN':
            squares[new_position[0]][new_position[1]].len_from_start = working_square.len_from_start + 1
            predecessor_tab[new_position[0]][new_position[1]] = working_square
            return
        if squares[new_position[0]][new_position[1]].state != 'FRESH':
            return
        if squares[new_position[0]][new_position[1]].sign == '@' or squares[new_position[0]][new_position[1]].sign == 'S':
            return

        squares[new_position[0]][new_position[1]].state = 'OPEN'
        neighbour_square = Square()
        neighbour_square.x_pos = new_position[0]
        neighbour_square.y_pos = new_position[1]
        neighbour_square.len_from_start = working_square.len_from_start + 1
        neighbour_square.heuristics = self.heuristics(neighbour_square)
        predecessor_tab[neighbour_square.x_pos][neighbour_square.y_pos] = working_square
        heapq.heappush(open_squares, neighbour_square)
        if new_position[0] == self.exit[0] and new_position[1] == self.exit[1]:
            squares[new_position[0]][new_position[1]].state = 'END'

    def find_nearby_followers(self, state):
        swarm = []
        for x in range(max(2, self.position[0] - self.sight_length), min(self.position[0] + self.sight_length, len(state) - 1)):
            for y in range(max(2, self.position[1] - self.sight_length), min(self.position[1] + self.sight_length, len(state[0]) - 1)):
                if state[x][y] == 'F':
                    geometry = FLGeometry(self.position, [x, y], state)
                    if geometry.agent1_sees_agent2():
                        swarm.append([x, y])
        return swarm

    """
    in each step agent has to check how many followers from its original swarm are still in its swarm
    if the number is too low, agent has to wait
    if the number is too low, but the agent has already been waiting for some time and the number of followers in the swarm has recently gone up, it has to move
    if the number is too low but the agent has already been waiting for too long, agent has to move
    """
    def check_swarm(self, state, followers, is_cbs):
        close_followers = self.find_nearby_followers(state)
        my_close_followers = 0
        for close in close_followers:
            for i, follower in enumerate(followers):
                if close == follower.position and followers[i].leader == self.agent_number:
                    my_close_followers+=1
        if my_close_followers < math.ceil(len(self.swarm)/self.min_swarm_denominator):
            if my_close_followers > self.last_number_of_followers and self.time_since_moved > 6 and is_cbs < 2:
                self.forced_move = True
                self.last_number_of_followers = my_close_followers
                return True
            if self.time_since_moved > 25 and is_cbs < 2:
                self.last_number_of_followers = my_close_followers
                return True
            self.last_number_of_followers = my_close_followers
            return False
        self.last_number_of_followers = my_close_followers
        return True

    def can_move(self, state, next_position, followers):
        if self.close_to_exit(next_position) and not self.is_swarm_evacuated(state, followers):
            return False
        return True

    def is_swarm_evacuated(self, state, followers):
        for index, follower in enumerate(followers):
            if index in self.swarm and not follower.evacuated:
                return False
        return True
