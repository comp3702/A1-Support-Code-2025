from control.game_state import GameState

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
    LAVA_TILE = '*'
    GEM_TILE = 'G'
    EXIT_TILE = 'E'
    PLAYER_TILE = 'P'
    VALID_TILES = {SOLID_TILE, LADDER_TILE, AIR_TILE, LAVA_TILE, GEM_TILE, EXIT_TILE, PLAYER_TILE}

    # action symbols (i.e. output file symbols)
    WALK_LEFT = 'wl'
    WALK_RIGHT = 'wr'
    JUMP = 'j'
    GLIDE_LEFT_1 = 'gl1'
    GLIDE_LEFT_2 = 'gl2'
    GLIDE_LEFT_3 = 'gl3'
    GLIDE_RIGHT_1 = 'gr1'
    GLIDE_RIGHT_2 = 'gr2'
    GLIDE_RIGHT_3 = 'gr3'
    DROP_1 = 'd1'
    DROP_2 = 'd2'
    DROP_3 = 'd3'
    ACTIONS = {WALK_LEFT, WALK_RIGHT, JUMP, GLIDE_LEFT_1, GLIDE_LEFT_2, GLIDE_LEFT_3,
               GLIDE_RIGHT_1, GLIDE_RIGHT_2, GLIDE_RIGHT_3, DROP_1, DROP_2, DROP_3}
    ACTION_COST = {WALK_LEFT: 1.0, WALK_RIGHT: 1.0, JUMP: 2.0, GLIDE_LEFT_1: 0.7, GLIDE_LEFT_2: 1.0, GLIDE_LEFT_3: 1.2,
                   GLIDE_RIGHT_1: 0.7, GLIDE_RIGHT_2: 1.0, GLIDE_RIGHT_3: 1.2, DROP_1: 0.3, DROP_2: 0.4, DROP_3: 0.5}

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

            elif len(line.strip()) > 0:
                grid_data.append(list(line.strip()))
                assert len(grid_data[-1]) == self.n_cols,\
                    f'/!\\ ERROR: Invalid input file - incorrect map row length (line {i})'

            i += 1

        # extract gem, exit and initial positions
        gem_positions = []
        self.init_row, self.init_col = None, None
        self.exit_row, self.exit_col = None, None
        for r in range(self.n_rows):
            for c in range(self.n_cols):
                if grid_data[r][c] == self.PLAYER_TILE:
                    assert self.init_row is None and self.init_col is None, \
                        '/!\\ ERROR: Invalid input file - more than one initial player position'
                    self.init_row, self.init_col = r, c
                    # assume player starts on air tile
                    grid_data[r][c] = self.AIR_TILE
                elif grid_data[r][c] == 'E':
                    assert self.exit_row is None and self.exit_col is None, \
                        '/!\\ ERROR: Invalid input file - more than one exit position'
                    self.exit_row, self.exit_col = r, c
                    # assume exit is placed on air tile
                    grid_data[r][c] = self.AIR_TILE
                elif grid_data[r][c] == self.GEM_TILE:
                    gem_positions.append((r, c))
                    # assume all gems are placed on air tiles
                    grid_data[r][c] = self.AIR_TILE
        self.n_gems = len(gem_positions)
        assert self.init_row is not None and self.init_col is not None, \
            '/!\\ ERROR: Invalid input file - No player initial position'
        assert self.exit_row is not None and self.exit_col is not None, \
            '/!\\ ERROR: Invalid input file - No exit position'

        assert len(grid_data) == self.n_rows, f'/!\\ ERROR: Invalid input file - incorrect number of map rows'

        self.gem_positions = gem_positions
        self.grid_data = grid_data

        self.all_gems_tuple = tuple([1 for _ in range(self.n_gems)])    # !!! added

    def get_init_state(self):
        """
        Get a state representation instance for the initial state.
        :return: initial state
        """
        return GameState(self.init_row, self.init_col, tuple(0 for g in self.gem_positions))

    def perform_action(self, state, action):
        """
        Perform the given action on the given state, and return whether the action was successful (i.e. valid and
        collision free) and the resulting new state.
        :param state: current GameState
        :param action: an element of self.ACTIONS
        :return: (successful [True/False], next_state [GameState])
        """
        # check walkable ground prerequisite if applicable
        if action in (self.WALK_LEFT, self.WALK_RIGHT, self.JUMP) and \
                self.grid_data[state.row + 1][state.col] not in (self.SOLID_TILE, self.LADDER_TILE):
            # prerequisite not satisfied - on a walkable surface
            return False, state.deepcopy()

        # get coordinates for next state and clear zone states
        clear_zone = []

        if action == self.WALK_LEFT:
            next_row, next_col = (state.row, state.col - 1)         # left 1

        elif action == self.WALK_RIGHT:
            next_row, next_col = (state.row, state.col + 1)         # right 1

        elif action == self.JUMP:
            next_row, next_col = (state.row - 1, state.col)         # up 1

        elif action == self.GLIDE_LEFT_1:
            clear_zone.append((state.row, state.col - 1))           # left 1
            clear_zone.append((state.row + 1, state.col))           # down 1
            next_row, next_col = (state.row + 1, state.col - 1)     # left 1, down 1

        elif action == self.GLIDE_LEFT_2:
            clear_zone.append((state.row, state.col - 1))           # left 1
            clear_zone.append((state.row, state.col - 2))           # left 2
            clear_zone.append((state.row + 1, state.col))           # down 1
            clear_zone.append((state.row + 1, state.col - 1))       # left 1, down 1
            next_row, next_col = (state.row + 1, state.col - 2)     # left 2, down 1

        elif action == self.GLIDE_LEFT_3:
            clear_zone.append((state.row, state.col - 1))           # left 1
            clear_zone.append((state.row, state.col - 2))           # left 2
            clear_zone.append((state.row, state.col - 3))           # left 3
            clear_zone.append((state.row + 1, state.col))           # down 1
            clear_zone.append((state.row + 1, state.col - 1))       # left 1, down 1
            clear_zone.append((state.row + 1, state.col - 2))       # left 2, down 1
            next_row, next_col = (state.row + 1, state.col - 3)     # left 3, down 1

        elif action == self.GLIDE_RIGHT_1:
            clear_zone.append((state.row, state.col + 1))           # right 1
            clear_zone.append((state.row + 1, state.col))           # down 1
            next_row, next_col = (state.row + 1, state.col + 1)     # right 1, down 1

        elif action == self.GLIDE_RIGHT_2:
            clear_zone.append((state.row, state.col + 1))           # right 1
            clear_zone.append((state.row, state.col + 2))           # right 2
            clear_zone.append((state.row + 1, state.col))           # down 1
            clear_zone.append((state.row + 1, state.col + 1))       # right 1, down 1
            next_row, next_col = (state.row + 1, state.col + 2)     # right 2, down 1

        elif action == self.GLIDE_RIGHT_3:
            clear_zone.append((state.row, state.col + 1))           # right 1
            clear_zone.append((state.row, state.col + 2))           # right 2
            clear_zone.append((state.row, state.col + 3))           # right 3
            clear_zone.append((state.row + 1, state.col))           # down 1
            clear_zone.append((state.row + 1, state.col + 1))       # right 1, down 1
            clear_zone.append((state.row + 1, state.col + 2))       # right 2, down 1
            next_row, next_col = (state.row + 1, state.col + 3)     # right 3, down 1

        elif action == self.DROP_1:
            next_row, next_col = (state.row + 1, state.col)         # down 1

        elif action == self.DROP_2:
            clear_zone.append((state.row + 1, state.col))           # down 1
            next_row, next_col = (state.row + 2, state.col)         # down 2

        elif action == self.DROP_3:
            clear_zone.append((state.row + 1, state.col))           # down 1
            clear_zone.append((state.row + 2, state.col))           # down 2
            next_row, next_col = (state.row + 3, state.col)         # down 3

        else:
            assert False, '/!\\ ERROR: Invalid action given to perform_action()'

        # check that next_state is within bounds
        if not (0 <= next_row < self.n_rows and 0 <= next_col < self.n_cols):
            # next state is out of bounds
            return False, state.deepcopy()

        # check for a collision (with either next state or a clear zone state)
        if self.grid_data[next_row][next_col] in (self.SOLID_TILE, self.LAVA_TILE):
            # next state results in collision
            return False, state.deepcopy()
        for (r, c) in clear_zone:
            if self.grid_data[r][c] in (self.SOLID_TILE, self.LAVA_TILE):
                # moving through clear zone to next state results in collision
                return False, state.deepcopy()

        # check if a gem is collected
        if (next_row, next_col) in self.gem_positions and \
                state.gem_status[self.gem_positions.index((next_row, next_col))] == 0:
            next_gem_status = list(state.gem_status)
            next_gem_status[self.gem_positions.index((next_row, next_col))] = 1
            next_gem_status = tuple(next_gem_status)
        else:
            next_gem_status = state.gem_status

        return True, GameState(next_row, next_col, next_gem_status)

    def is_solved(self, state):
        """
        Check if the game has been solved (i.e. player at exit and all gems collected)
        :param state: current GameState
        :return: True if solved, False otherwise
        """
        all_gems_collected = True
        for g in state.gem_status:
            if g == 0:
                all_gems_collected = False
        return state.row == self.exit_row and state.col == self.exit_col and all_gems_collected

    def is_game_over(self, state):
        """
        Check if a game over situation has occurred (i.e. player has landed on a lava tile)
        :param state: current GameState
        :return: True if game over, False otherwise
        """
        assert 0 < state.row < self.n_rows - 1 and 0 < state.col < self.n_cols - 1, '!!! invalid player coordinates !!!'
        return self.grid_data[state.row + 1][state.col] == self.LAVA_TILE

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
                elif self.exit_row == r and self.exit_col == c:
                    # current tile is exit
                    line += self.grid_data[r][c] + 'E' + self.grid_data[r][c]
                elif (r, c) in self.gem_positions and \
                        state.gem_status[self.gem_positions.index((r, c))] == 0:
                    # current tile is an uncollected gem
                    line += self.grid_data[r][c] + 'G' + self.grid_data[r][c]
                else:
                    line += self.grid_data[r][c] * 3
            print(line)
        print('\n' * 2)
