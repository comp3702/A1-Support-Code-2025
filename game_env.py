from game_state import GameState

"""
game_env.py

This file contains a class representing an Untitled Dragon Game environment. You should make use of this class in your
solver.

COMP3702 Assignment 1 "Dragon Game" Support Code

Last updated by njc 07/08/23
"""


class GameEnv:
    """
    Instance of an Untitled Dragon Game environment. Stores the dimensions of the environment, initial player position,
    exit position, number of gems and position of each gem, time limit, cost target, the tile type of each grid
    position, and a list of all available actions.

    The grid is indexed top to bottom, left to right (i.e. the top left corner has coordinates (0, 0) and the bottom
    right corner has coordinates (n_rows-1, n_cols-1)).

    You may use and modify this class however you want. Note that evaluation on GradeScope will use an unmodified
    GameEnv instance as a simulator.
    """

    # input file symbols
    SOLID_TILE = 'X'
    LADDER_TILE = '='
    AIR_TILE = ' '
    TRAPDOOR = 'T'
    DRAWBRIDGE = 'D'
    GOAL_TILE = 'G'
    PLAYER_TILE = 'P'
    LEVER_1 = 'A'
    LEVER_2 = 'B'
    LEVER_3 = 'C'
    LEVERS = {LEVER_1, LEVER_2, LEVER_3}
    VALID_TILES = {SOLID_TILE, LADDER_TILE, AIR_TILE, TRAPDOOR, DRAWBRIDGE, GOAL_TILE, PLAYER_TILE}

    # action symbols (i.e. output file symbols)
    WALK_LEFT = 'wl'
    WALK_RIGHT = 'wr'
    CLIMB = 'c'
    DROP = 'd'
    ACTIVATE = 'a'
    ACTIONS = {WALK_LEFT, WALK_RIGHT, CLIMB, DROP, ACTIVATE}
    ACTION_COST = {WALK_LEFT: 1.0, WALK_RIGHT: 1.0, CLIMB: 2.0, DROP: 0.5, ACTIVATE: 1.0}

    # perform action return statuses
    SUCCESS = 0
    COLLISION = 1
    GAME_OVER = 2

    def __init__(self, filename):
        """
        Process the given input file and create a new game environment instance based on the input file.
        :param filename: name of input file
        """
        try:
            f = open(filename, 'r')
        except FileNotFoundError:
            assert False, '/!\\ ERROR: Testcase file not found'

        lever_map_icons = {}
        grid_data = []
        i = 0
        for line in f:
            # skip annotations in input file
            if line.strip()[0] == '#':
                continue

            if i == 0:
                try:
                    self.n_rows, self.n_cols = \
                        tuple([int(x) for x in line.strip().split(',')])
                except ValueError:
                    assert False, f'/!\\ ERROR: Invalid input file - n_rows and n_cols (line {i})'
            elif i == 1:
                try:
                    # cost targets - used for both UCS and A*
                    self.cost_min_tgt, self.cost_max_tgt = \
                        tuple([float(x) for x in line.strip().split(',')])
                except ValueError:
                    assert False, f'/!\\ ERROR: Invalid input file - cost targets (line {i})'
            elif i == 2:
                try:
                    # nodes expanded targets - used for A* heuristic eval only
                    self.nodes_min_tgt, self.nodes_max_tgt = \
                        tuple([float(x) for x in line.strip().split(',')])
                except ValueError:
                    assert False, f'/!\\ ERROR: Invalid input file - nodes targets (line {i})'
            elif i == 3:
                try:
                    self.ucs_time_min_tgt, self.ucs_time_max_tgt = \
                        tuple([float(x) for x in line.strip().split(',')])
                except ValueError:
                    assert False, f'/!\\ ERROR: Invalid input file - UCS time targets (line {i})'
            elif i == 4:
                try:
                    self.a_star_time_min_tgt, self.a_star_time_max_tgt = \
                        tuple([float(x) for x in line.strip().split(',')])
                except ValueError:
                    assert False, f'/!\\ ERROR: Invalid input file - A* time targets (line {i})'
            elif i == 5:
                try:
                    entries = line.strip().split(',')  # Split by comma
                    for entry in entries:
                        lever, trap = entry.strip().split(':')
                        lever_map_icons[lever.strip()] = trap.strip()
                except ValueError:
                    assert False, f'/!\\ ERROR: Invalid input file - lever to trap map (line {i})'

            elif len(line.strip()) > 0:
                grid_data.append(list(line.strip()))
                assert len(grid_data[-1]) == self.n_cols,\
                    f'/!\\ ERROR: Invalid input file - incorrect map row length (line {i})'

            i += 1

        # extract initial, goal, and trap positions
        trap_positions = []
        lever_positions = []
        lever_map_positions = {}
        traps_map = {}
        self.init_row, self.init_col = None, None
        self.goal_row, self.goal_col = None, None
        for r in range(self.n_rows):
            for c in range(self.n_cols):
                if grid_data[r][c] == self.PLAYER_TILE:
                    assert self.init_row is None and self.init_col is None, \
                        '/!\\ ERROR: Invalid input file - more than one initial player position'
                    self.init_row, self.init_col = r, c
                    # assume player starts on air tile
                    grid_data[r][c] = self.AIR_TILE
                elif grid_data[r][c] == self.GOAL_TILE:
                    assert self.goal_row is None and self.goal_col is None, \
                        '/!\\ ERROR: Invalid input file - more than one exit position'
                    self.goal_row, self.goal_col = r, c
                    # assume exit is placed on air tile
                    grid_data[r][c] = self.AIR_TILE
                elif grid_data[r][c] == self.DRAWBRIDGE:
                    # TODO: Treat drawbridges differently to traps (should be a
                    #  solid tile above the bridge or something to block the player from crossing)
                    # assume all drawbridges are placed on air tiles
                    grid_data[r][c] = self.AIR_TILE
                    trap_positions.append((r, c))
                    traps_map[self.DRAWBRIDGE] = (r, c)
                elif grid_data[r][c] == self.TRAPDOOR:
                    # assume all trapdoors are placed on air tiles
                    grid_data[r][c] = self.AIR_TILE
                    trap_positions.append((r, c))
                    traps_map[self.TRAPDOOR] = (r, c)
                elif grid_data[r][c] in self.LEVERS:
                    lever_positions.append((r, c))

        assert self.init_row is not None and self.init_col is not None, \
            '/!\\ ERROR: Invalid input file - No player initial position'
        assert self.goal_row is not None and self.goal_col is not None, \
            '/!\\ ERROR: Invalid input file - No exit position'

        for lever_position in lever_positions:
            lever_map_positions[lever_position] = traps_map[lever_map_icons[grid_data[lever_position[0]][lever_position[1]]]]
        self.lever_map_positions = lever_map_positions
        self.traps_map = traps_map
        self.trap_positions = trap_positions

        assert len(grid_data) == self.n_rows, f'/!\\ ERROR: Invalid input file - incorrect number of map rows'
        self.grid_data = grid_data

    def get_init_state(self):
        """
        Get a state representation instance for the initial state.
        :return: initial state
        """
        return GameState(self.init_row, self.init_col, tuple(0 for _ in self.trap_positions))

    def perform_action(self, state, action):
        """
        Perform the given action on the given state, and return whether the action was successful (i.e. valid and
        collision free) and the resulting new state.
        :param state: current GameState
        :param action: an element of self.ACTIONS
        :return: (successful [True/False], next_state [GameState])
        """

        # check walkable ground prerequisite if applicable
        if action in (self.WALK_LEFT, self.WALK_RIGHT) and \
                self.grid_data[state.row + 1][state.col] not in (self.SOLID_TILE, self.LADDER_TILE):
            # prerequisite not satisfied - on a walkable surface
            return False, state.deepcopy()
        elif action is self.CLIMB and self.grid_data[state.row][state.col] != self.LADDER_TILE:
            return False, state.deepcopy()

        next_trap_status = list(state.trap_status)
        # get coordinates for next state
        if action == self.WALK_LEFT:
            next_row, next_col = (state.row, state.col - 1)         # left 1

        elif action == self.WALK_RIGHT:
            next_row, next_col = (state.row, state.col + 1)         # right 1

        elif action == self.CLIMB:
            next_row, next_col = (state.row - 1, state.col)         # up 1

        elif action == self.DROP:
            next_row, next_col = (state.row + 1, state.col)         # down 1

        elif action == self.ACTIVATE:
            # check if player is on a lever tile
            # activate trap if they are on a lever tile
            next_row, next_col = state.row, state.col
            if (state.row, state.col) in self.lever_map_positions.keys():
                trap_pos = self.lever_map_positions[(state.row, state.col)]
                if state.trap_status[self.trap_positions.index(trap_pos)] == 0:
                    self.grid_data[self.lever_map_positions[(state.row, state.col)][0]][self.lever_map_positions[(state.row, state.col)][1]] = self.SOLID_TILE
                    next_trap_status[self.trap_positions.index(self.lever_map_positions[(state.row, state.col)])] = 1
                else:
                    self.grid_data[self.lever_map_positions[(state.row, state.col)][0]][self.lever_map_positions[(state.row, state.col)][1]] = self.AIR_TILE
                    next_trap_status[self.trap_positions.index(self.lever_map_positions[(state.row, state.col)])] = 0

        else:
            assert False, '/!\\ ERROR: Invalid action given to perform_action()'

        # check that next_state is within bounds
        if not (0 <= next_row < self.n_rows and 0 <= next_col < self.n_cols):
            # next state is out of bounds
            return False, state.deepcopy()

        # check for a collision (with either next state or a clear zone state)
        if self.grid_data[next_row][next_col] is self.SOLID_TILE:
            # next state results in collision
            return False, state.deepcopy()

        return True, GameState(next_row, next_col, tuple(next_trap_status))

    def is_solved(self, state):
        """
        Check if the game has been solved (i.e. player at exit and all gems collected)
        :param state: current GameState
        :return: True if solved, False otherwise
        """
        return state.row == self.goal_row and state.col == self.goal_col

    def render(self, state):
        """
        Render the map's current state to terminal
        """
        for r in range(self.n_rows):
            line = ''
            for c in range(self.n_cols):
                if state.row == r and state.col == c:
                    # current tile is player
                    line += self.grid_data[r][c] + 'P' + self.grid_data[r][c]
                elif self.goal_row == r and self.goal_col == c:
                    # current tile is exit
                    line += self.grid_data[r][c] + 'G' + self.grid_data[r][c]
                else:
                    line += self.grid_data[r][c] * 3
            print(line)
        print('\n' * 2)
