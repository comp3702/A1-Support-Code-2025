"""
game_state.py

This file contains a class representing an Untitled Dragon Game state. You should make use of this class in your solver.

COMP3702 Assignment 1 "Dragon Game" Support Code

Last updated by njc 07/08/23
"""


class GameState:
    """
    Instance of an Untitled Dragon Game state. row and col represent the current player position. gem_status is 1 for
    each collected gem, and 0 for each remaining gem.

    You may use this class and its functions. You may add your own code to this class (e.g. get_successors function,
    get_heuristic function, etc), but should avoid removing or renaming existing variables and functions to ensure
    Tester functions correctly.
    """

    def __init__(self, row, col, gem_status):
        self.row = row
        self.col = col
        assert isinstance(gem_status, tuple), '!!! gem_status should be a tuple !!!'
        self.gem_status = gem_status

    def __eq__(self, other):
        if not isinstance(other, GameState):
            return False
        return self.row == other.row and self.col == other.col and self.gem_status == other.gem_status

    def __hash__(self):
        return hash((self.row, self.col, *self.gem_status))

    def __repr__(self):
        return f'row: {self.row},\t\t col: {self.col},\t\t gem status: {self.gem_status}'

    def deepcopy(self):
        return GameState(self.row, self.col, self.gem_status)



