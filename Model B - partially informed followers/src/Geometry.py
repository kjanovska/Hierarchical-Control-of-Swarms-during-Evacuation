from Agent import *
import random
from math import sqrt

class Geometry:
    def __init__(self, agent1_pos, agent2_pos, map_list):
        self.agent1 = agent1_pos
        self.agent2 = agent2_pos
        self.map_list = map_list
        self.possible_intersection_points = []
        self.intersection_points = []
        self.df_line_parameters = [1, 1, 1]
        self.deviation = [float(0), float(0)]
        self.set_state()

    def agent1_sees_agent2(self):
        if self.sees_through_intersections():
            return True
        else:
            return False

    def set_state(self):
        self.select_deviation()
        # 2. calculate the line general equation of the line of which the two agents lay
        self.df_line_general_equation()
        # 3. select points, that may be intersected by the line
        self.select_possible_intersection()
        # 4. select points, that are actually intersected by the line
        self.intersects()

    def select_possible_intersection(self):
        for index_0, column in enumerate(self.map_list):
            for index_1, row in enumerate(column):
                if min(self.agent1[0], self.agent2[0]) <= index_0 <= max(self.agent1[0], self.agent2[0]) \
                        and min(self.agent1[1], self.agent2[1]) <= index_1 <= max(self.agent1[1],
                                                                                  self.agent2[1]):
                    if [index_0, index_1] != self.agent1 and [index_0, index_1] != self.agent2:
                        self.possible_intersection_points.append([index_0, index_1])

    def intersects(self):
        for square in self.possible_intersection_points:
            self.intersects_square(square, square, [square[0] + 1, square[1]])  # left side
            self.intersects_square(square, [square[0], square[1] + 1], [square[0] + 1, square[1] + 1])  # right side
            self.intersects_square(square, square, [square[0], square[1] + 1])  # top side
            self.intersects_square(square, [square[0] + 1, square[1]], [square[0] + 1, square[1] + 1])  # bottom side

    def intersects_square(self, square, point1, point2):
        gen_equation1 = point1[0] * self.df_line_parameters[0] + point1[1] * self.df_line_parameters[1] + self.df_line_parameters[2]
        gen_equation2 = point2[0] * self.df_line_parameters[0] + point2[1] * self.df_line_parameters[1] + self.df_line_parameters[2]
        if (gen_equation1 < 0 and gen_equation2 > 0) or (gen_equation1 > 0 and gen_equation2 < 0) or gen_equation1 == 0 or gen_equation2 == 0:
            self.intersection_points.append(square)

    """
    count the distance between a point and the line on which the two agents lay
    """
    def distance_point_line(self, point):
        return abs(
            self.df_line_parameters[0] * point[0] + self.df_line_parameters[1] * point[1] + self.df_line_parameters[
                2]) / \
               sqrt(pow(self.df_line_parameters[0], 2) + pow(self.df_line_parameters[1], 2))

    def df_line_general_equation(self):
        # A1(x1, y1) a A2(x2, y2)
        # agent1 = always LEADER -> always deviation = [0.5, 0.5]
        # a = y2 - y1
        a = self.agent1[1] + 0.5 - (self.agent2[1] + self.deviation[1])
        # b = x1 - x2
        b = (self.agent2[0] + self.deviation[0]) - self.agent1[0] - 0.5
        # -c = a*x + b*y
        c = a * (self.agent1[0] + 0.5) + b * (self.agent1[1] + 0.5)
        self.df_line_parameters = [a, b, -1 * c]

    def select_deviation(self):
        pass

    def sees_through_intersections(self):
        pass


class LFGeometry(Geometry):  # follower sees leader
    def __init__(self, leader_pos, follower_pos, map_list):
        super().__init__(leader_pos, follower_pos, map_list)

    def select_deviation(self):
        self.deviation[0] = random.uniform(0.15, 0.85)
        self.deviation[1] = random.uniform(0.15, 0.85)

    def sees_through_intersections(self):
        for square in self.intersection_points:
            if self.map_list[square[0]][square[1]] == '@':
                return False
            elif self.map_list[square[0]][square[1]] == 'F':
                if self.distance_point_line([square[0] + random.uniform(0.15, 0.85), square[1] + random.uniform(0.15, 0.85)]) <= 0.15:
                    return False
        return True

class FLGeometry(Geometry): # leader sees follower
    def __init__(self, leader_pos, follower_pos, map_list):
        super().__init__(leader_pos, follower_pos, map_list)

    def select_deviation(self):
        self.deviation[0] = random.uniform(0.15, 0.85)
        self.deviation[1] = random.uniform(0.15, 0.85)

    def sees_through_intersections(self):
        for square in self.intersection_points:
            if self.map_list[square[0]][square[1]] == '@':
                return False
        return True


class LLGeometry(Geometry):
    def __init__(self, leader1_pos, leader2_pos, map_list, conflict_distance):
        super().__init__(leader1_pos, leader2_pos, map_list)
        self.conflict_distance = conflict_distance

    def select_deviation(self):
        self.deviation[0] = 0.5
        self.deviation[1] = 0.5

    def sees_through_intersections(self):
        for square in self.intersection_points:
            if self.map_list[square[0]][square[1]] == '@':
                return False
        if distance_from_agent(self.agent1, self.agent2) < self.conflict_distance:
            return True
        else:
            return False
