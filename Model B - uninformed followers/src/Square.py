import sys


class Square:
    sign = '.'
    state = 'FRESH'
    x_pos = 0
    y_pos = 0
    len_from_start = sys.maxsize
    heuristics = 0

    def __init__(self):
        state = 'FRESH'
        sign = '.'
        x_pos = 0
        y_pos = 0

    def __lt__(self, other):
        return (self.len_from_start + self.heuristics/2) < (other.len_from_start + other.heuristics/2)
