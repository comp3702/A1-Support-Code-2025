"""
game_state.py

This file contains a class representing a Cheese Hunter state. You should make use of this class in your solver.

COMP3702 Assignment 1 "Cheese Hunter" Support Code, 2025
"""


class GameState:
    """
    Instance of a Cheese Hunter state. row and col represent the current player position. trap_status is 1 for
    each activated lever/trap, and 0 for each remaining lever/trap.

    You may use this class and its functions. You may add your own code to this class (e.g. get_successors function,
    get_heuristic function, etc), but should avoid removing or renaming existing variables and functions to ensure
    Tester functions correctly.
    """

    def __init__(self, row, col, trap_status):
        self.row = row
        self.col = col
        assert isinstance(trap_status, tuple), '!!! trap_status should be a tuple !!!'
        self.trap_status = trap_status

    def __eq__(self, other):
        if not isinstance(other, GameState):
            return False
        return self.row == other.row and self.col == other.col and self.trap_status == other.trap_status

    def __hash__(self):
        return hash((self.row, self.col, self.trap_status))

    def __repr__(self):
        return f'row: {self.row},\t\t col: {self.col}, \t\t trap status: {self.trap_status}'

    def deepcopy(self):
        return GameState(self.row, self.col, self.trap_status)
