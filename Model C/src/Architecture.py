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
                position_to_move = self.followers[index].random_free_neighbour(self.map)  # select new position for the follower
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
        for index_x, line in enumerate(self.map):
            for index_y, pixel in enumerate(line):
                if self.map[index_x][index_y] == 'E':
                    self.map[index_x][index_y] = '.'
        for exit in self.exits:
            self.map[exit[0]][exit[1]] = 'E'

    def load_leaders(self, config_file):
        new_leaders = []
        file = open(config_file, "r")
        i = 0
        for line in file:
            leader = LeadingAgent(self.params.leader_sight, i, self.params.min_swarm_denominator,
                                  self.params.leader_conflict_distance, self.exits)
            coords_str = line.split(",")
            leader.position = [int(coords_str[0], 10), int(coords_str[1], 10)]
            leader.find_exit()
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
            follower.exit = random.choice(copy.deepcopy(self.exits))
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

    def direction(self, leader, new_position):
        if leader.position[1] > new_position[1] or (leader.position[1] - leader.exit[1] < 3 and leader.position[1] - leader.exit[1] >= 0):
            return 'left'
        elif leader.position[1] < new_position[1] or (leader.exit[1] - leader.position[1] < 3 and leader.exit[1] - leader.position[1] >= 0):
            return 'right'
        else:
            return 'stay'

    """
    initialize agents, map and exits from their respective files
    """
    def initialize(self):
        if self.params.map == "plane1":
            print("Number of agents (10 - 165):")
            a = int(input())
        else:
            a = ""
        self.open_map('maps/'+ str(self.params.map) +'.map')
        self.load_exits('exits/'+ str(self.params.map) +'_exits.txt')
        self.leaders = self.load_leaders('scenarios/'+ str(self.params.map) + '_L.txt')
        for leader in self.leaders:
            self.place_agent(leader)

        self.followers = self.load_followers('scenarios/'+ str(self.params.map) +'_F' + str(a) + '.txt')
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
        while True:
            step_count += 1
            print("step no. " + str(step_count) + ":")
            tree = CBSTree(self.map, self.leaders, self.followers)
            solution = tree.cbs()
            directions = []
            # 1. LEADER CHOOSES DIRECTION FOR FOLLOWERS TO GO
            for index, agent_path in enumerate(solution):
                if len(agent_path) >= 2:
                    directions.append(self.direction(self.leaders[index], agent_path[1]))
                else:
                    directions.append(self.direction(self.leaders[index], agent_path[0]))
            # 2. FOLLOWER MOVES ACCORDING TO HIS POSITION AND LEADER'S ORDERS
            for follower in self.followers:
                if not follower.evacuated:
                    for exit in self.exits:
                        if distance_from_agent(follower.position, exit) <= 1:
                            no_evacuated += 1
                            follower.evacuated = True
                            follower.sign = '.'
                            self.update_map(follower, follower.position)
                            follower.position = copy.deepcopy(exit)
                            break
                    if not follower.evacuated:
                        where_to_move = follower.agent_function(self.map, self.leaders, directions)
                        self.move(follower, where_to_move, 'F')
            # 3. LEADER MOVES, BUT ONLY IF HE WOULDN'T BLOCK AN AISLE FOR FOLLOWERS THAT HAVE YET TO EVACUATE
            for index, agent_path in enumerate(solution):
                new_pos = []
                if len(agent_path) >= 2:
                    new_pos = agent_path[1]
                else:
                    new_pos = agent_path[0]
                if self.leaders[index].can_move(self.map, new_pos, self.followers):
                    if len(agent_path) < 2 or distance_from_agent(self.leaders[index].position, self.leaders[index].exit) <= 1:
                        if not self.leaders[index].evacuated:
                            no_evacuated += 1
                            self.leaders[index].evacuated = True
                            self.leaders[index].sign = '.'
                            self.update_map(self.leaders[index], self.leaders[index].position)
                            self.leaders[index].position = copy.deepcopy(self.leaders[index].exit)
                            self.leaders[index].sign = 'E'
                        self.update_map(self.leaders[index], self.leaders[index].position)
                    else:
                        self.move(self.leaders[index], new_pos, 'L')
            self.print_map()
            print(
                "number of evacuated: " + str(no_evacuated) + " out of " + str(len(self.followers) + len(self.leaders)))
            f.write(str(step_count) + ';' + str(no_evacuated) + '\n')
            if no_evacuated == len(self.followers) + len(self.leaders):
                break
        f.close()
