from Agent import *
from CBSTree import CBSTree
from LeadingAgent import LeadingAgent
from FollowingAgent import *
from ParamInit import *

class Map:
    def __init__(self):
        self.map = []
        self.exits = []
        self.followers = []
        self.leaders = []
        self.params = ParamInit()

    def open_map(self, filename):
        file = open(filename, 'r')
        for line in file:
            self.map.append(list(line))

    def print_map(self):
        for line in self.map:
            for pixel in line:
                print(pixel, end='')
        print()

    def find_empty_spot(self):
        empty_spots_list = []
        empty_spot = []
        for index_x, line in enumerate(self.map):
            for index_y, pixel in enumerate(line):
                if self.map[index_x][index_y] == '.':
                    empty_spot.append(index_x)
                    empty_spot.append(index_y)
                    empty_spots_list.append(copy.deepcopy(empty_spot))
                    empty_spot.clear()
        random_spot = random.choice(copy.deepcopy(empty_spots_list))
        return random_spot

    def place_agent(self, agent):
        self.map[agent.position[0]][agent.position[1]] = agent.sign

    def move(self, agent, new_position, agent_type):
        old_position = copy.deepcopy(agent.position)
        if self.map[new_position[0]][new_position[1]] == 'F' and agent_type == 'L':
            self.push_away([old_position], new_position, 0)
        if self.map[new_position[0]][new_position[1]] != '.':
            return
        agent.position[0] = copy.deepcopy(new_position[0])
        agent.position[1] = copy.deepcopy(new_position[1])
        self.update_map(agent, old_position)

    """
    if a leader's planned next position is occupied by a follower, the leader may push him away and move to that position
    FROM POSITION = position of an agent, that pushed away agent calling this function -> agent on from_position cannot be pushed away back
    TO POSITION = position of an agent, that needs to move
    POSITION TO MOVE = position, where the pushed away follower wants to move
    """
    def push_away(self, from_position, to_position, counter):
        if counter > 900:
            return
        if self.map[to_position[0]][to_position[1]] == 'F':
            index = self.find_follower_on(to_position)  # follower to push away - index in list of followers
            position_to_move = copy.deepcopy(
                self.followers[index].position)  # desired position init == this follower's position = to_position
            while position_to_move == self.followers[
                index].position:  # because random free neighbour can be its position
                position_to_move = self.followers[index].random_free_neighbour(
                    self.map)  # select new position for the follower
                if position_to_move is not None and self.map[position_to_move[0]][
                    position_to_move[
                        1]] == '.' and position_to_move not in from_position:  # if the selected position exists and is free
                    self.move(self.followers[index], position_to_move, 'F')
                    return
                else:  # if the chosen position is follower's current position, it has to move
                    follower_to_push_away = self.followers[index].random_next_follower(self.map,
                                                                                       from_position)  # ensuring the chosen agent isn't the predecessor
                    if follower_to_push_away is None:
                        return
                    from_position.append(to_position)
                    self.push_away(from_position, follower_to_push_away, counter + 1)
                    self.move(self.followers[index], follower_to_push_away, 'F')
                    return

    def update_map(self, follower, old_position):
        self.map[old_position[0]][old_position[1]] = '.'
        self.map[follower.position[0]][follower.position[1]] = follower.sign

    def load_leaders(self, config_file):
        new_leaders = []
        file = open(config_file, "r")
        i = 0
        for line in file:
            a = 100 - self.params.informed_leaders
            b = random.randint(1, 100)
            inf = True
            if b < a:
                inf = False
            leader = LeadingAgent(self.params.leader_sight, i, self.params.min_swarm_denominator, inf,
                                  self.params.leader_conflict_distance)
            coords_str = line.split(",")
            leader.position = [int(coords_str[0], 10), int(coords_str[1], 10)]
            new_leaders.append(leader)
            i += 1
        file.close()
        return new_leaders

    def load_followers(self, config_file):
        new_followers = []
        file = open(config_file, "r")
        for line in file:
            follower = FollowingAgent(self.params.follower_sight, self.params.follower_obedience)
            coords_str = line.split(",")
            follower.position = [int(coords_str[0], 10), int(coords_str[1], 10)]
            follower.known_exit = random.choice(copy.deepcopy(self.exits))
            new_followers.append(follower)
        file.close()
        return new_followers

    def load_exits(self, config_file):
        file = open(config_file, "r")
        for line in file:
            coords_str = line.split(",")
            coords = [int(coords_str[0], 10), int(coords_str[1], 10)]
            self.map[coords[0]][coords[1]] = 'E'
            self.exits.append(coords)
        file.close()

    """
    find an index of a follower in list of followers on given position
    """
    def find_follower_on(self, position):
        for i, follower in enumerate(self.followers):
            if follower.position == position:
                return i
        return None

    """
    assign a list of followers to each leader
    """
    def assign_swarms(self):
        for index, leader in enumerate(self.leaders):
            followers_positions = leader.find_nearby_followers(self.map)
            for follower in followers_positions:
                f_index = self.find_follower_on(follower)
                # agent only chooses to add a follower to its swarm if it's not already a part of a swarm
                if self.followers[f_index].leader is None:
                    self.leaders[index].swarm.append(f_index)
                    self.followers[f_index].leader = index

    """
    return a list of leaders who are all informed/not informed
    """
    def choose_leaders(self, is_informed):
        l = []
        for leader in self.leaders:
            if leader.is_informed == is_informed:
                l.append(leader)
        return l

    """
    initialize agents, map and exits from their respective files
    """
    def initialize(self):
        print("Number of agents (10 - 225):")
        a = int(input())
        self.open_map('maps/building1.map')
        self.load_exits('exits/building1_exits.txt')
        self.leaders = self.load_leaders('scenarios/class_1L.txt')
        for leader in self.leaders:
            self.place_agent(leader)

        self.followers = self.load_followers('scenarios/class_F' + str(a) + '.txt')
        for follower in self.followers:
            self.place_agent(follower)
        self.print_map()
        self.assign_swarms()

    def run(self):
        b = self.params.experiment_number
        filename = "experiments/" + str(b) + ".csv"
        f = open(filename, "w", encoding="utf-8")
        self.initialize()
        step_count = 0
        no_evacuated = 0
        informed_leaders = self.choose_leaders(True)
        noninformed_leaders = self.choose_leaders(False)
        while True:
            step_count += 1
            print("step no. " + str(step_count) + ":")
            tree = CBSTree(self.map, informed_leaders, self.followers)
            solution = tree.cbs()
            noninf_solution = []
            for leader in noninformed_leaders:
                noninf_solution.append(leader.find_path(self.map, [], self.followers, 0))
            for follower in self.followers:
                if not follower.evacuated:
                    for exit in self.exits:
                        if distance_from_agent(follower.position, exit) <= 2:
                            no_evacuated += 1
                            follower.evacuated = True
                            follower.sign = '.'
                            self.update_map(follower, follower.position)
                            follower.position = copy.deepcopy(exit)
                            break
                    if not follower.evacuated:
                        where_to_move = follower.agent_function(self.map, self.leaders)
                        self.move(follower, where_to_move, 'F')
            for index, agent_path in enumerate(solution):
                if len(agent_path) < 2 or distance_from_agent(informed_leaders[index].position, informed_leaders[index].exit) <= 2:
                    if not informed_leaders[index].evacuated:
                        no_evacuated += 1
                        informed_leaders[index].evacuated = True
                        informed_leaders[index].sign = '.'
                        self.update_map(informed_leaders[index], informed_leaders[index].position)
                        informed_leaders[index].position = copy.deepcopy(informed_leaders[index].exit)
                        informed_leaders[index].sign = 'E'
                    self.update_map(informed_leaders[index], informed_leaders[index].position)
                else:
                    self.move(informed_leaders[index], agent_path[1], 'L')

            for index, agent_path in enumerate(noninf_solution):
                if len(agent_path) < 2 or distance_from_agent(noninformed_leaders[index].position, noninformed_leaders[index].exit) <= 2:
                    if not noninformed_leaders[index].evacuated:
                        no_evacuated += 1
                        noninformed_leaders[index].evacuated = True
                        noninformed_leaders[index].sign = '.'
                        self.update_map(noninformed_leaders[index], noninformed_leaders[index].position)
                        noninformed_leaders[index].position = copy.deepcopy(noninformed_leaders[index].exit)
                        noninformed_leaders[index].sign = 'E'
                    self.update_map(noninformed_leaders[index], noninformed_leaders[index].position)
                else:
                    self.move(noninformed_leaders[index], agent_path[1], 'L')
            self.print_map()
            print(
                "number of evacuated: " + str(no_evacuated) + " out of " + str(len(self.followers) + len(self.leaders)))
            f.write(str(step_count) + ';' + str(no_evacuated) + '\n')
            if no_evacuated == len(self.followers) + len(self.leaders):
                break
        f.close()
