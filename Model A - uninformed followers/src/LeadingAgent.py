from Agent import Agent, copy
from Square import Square
import heapq


class LeadingAgent(Agent):
    def __init__(self, sight_length, agent_number, is_informed, conflict_distance):
        super().__init__(sight_length=sight_length)
        self.evacuated = False
        self.sign = 'L'
        self.agent_number = agent_number
        self.constraints = []
        self.exit = []
        self.is_informed = is_informed
        self.conflict_distance = conflict_distance

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
    def find_path(self, state, all_constraints):
        self.choose_own_constraints(all_constraints)
        squares = self.fill_state(state)
        self.find_exit(squares)
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
        if squares[new_position[0]][new_position[1]].sign == '@' or self.is_position_constrained(new_position, new_distance):
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

    def find_exit(self, squares):  # one exit in map
        coordinates = []  # coordinates[0] = x, coordinates[1] = y
        for row in range(0, len(squares)):
            for column in range(0, len(squares[0])):
                if squares[row][column].sign == 'E':
                    coordinates.append(row)
                    coordinates.append(column)
        self.exit = coordinates

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
        if squares[new_position[0]][new_position[1]].sign == '@':
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


