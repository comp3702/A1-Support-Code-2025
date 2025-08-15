from game_state import GameState

"""
game_env.py

This file contains a class representing a Cheese Hunter environment. You should make use of this class in your
solver.

COMP3702 Assignment 1 "Cheese Hunter" Support Code, 2025
"""


class GameEnv:
    """
    Instance of a Cheese Hunter environment. Stores the dimensions of the environment, initial player position,
    goal position, lever positions, trap positions, mapping of levers to traps, time limit, cost target,
    the tile type of each grid position, and a list of all available actions.

    The grid is indexed top to bottom, left to right (i.e. the top left corner has coordinates (0, 0) and the bottom
    right corner has coordinates (n_rows-1, n_cols-1)).

    You may use and modify this class however you want. Note that evaluation on GradeScope will use an unmodified
    GameEnv instance as a simulator.
    """

    # Input file symbols
    SOLID_TILE = "X"
    LADDER_TILE = "="
    AIR_TILE = " "
    TRAPDOOR = "T"
    DRAWBRIDGE = "D"
    GOAL_TILE = "G"
    PLAYER_TILE = "P"
    LEVER = "L"
    VALID_TILES = {
        SOLID_TILE,
        LADDER_TILE,
        AIR_TILE,
        TRAPDOOR,
        DRAWBRIDGE,
        GOAL_TILE,
        PLAYER_TILE,
    }

    # Action symbols (i.e. output file symbols)
    WALK_LEFT = "wl"
    WALK_RIGHT = "wr"
    CLIMB = "c"
    DROP = "d"
    ACTIVATE = "a"
    JUMP = "j"
    SPRINT_LEFT = "sl"
    SPRINT_RIGHT = "sr"
    ACTIONS = {
        WALK_LEFT,
        WALK_RIGHT,
        CLIMB,
        DROP,
        ACTIVATE,
        JUMP,
        SPRINT_LEFT,
        SPRINT_RIGHT,
    }
    ACTION_COST = {
        WALK_LEFT: 1.0,
        WALK_RIGHT: 1.0,
        CLIMB: 2.0,
        DROP: 0.5,
        ACTIVATE: 1.0,
        JUMP: 2.0,
        SPRINT_LEFT: 1.9,
        SPRINT_RIGHT: 1.9,
    }

    def __init__(self, filename):
        """
        Process the given input file and create a new game environment instance based on the input file.
        :param filename: name of input file
        """
        try:
            f = open(filename, "r")
        except FileNotFoundError:
            assert False, "/!\\ ERROR: Testcase file not found"

        grid_data = []
        schematic_data = []
        reading_schematic = False
        i = 0
        for line in f:
            # Check if we've hit the schematic section
            if line.strip().startswith("# Schematic"):
                reading_schematic = True
                continue

            # Skip annotations in input file
            if line.strip().startswith("#"):
                continue

            if reading_schematic:
                # Read schematic grid data
                if len(line.rstrip()) <= self.n_cols:
                    schematic_data.append(list(line.rstrip().ljust(self.n_cols)))
                continue

            if i == 0:
                try:
                    # Number of rows and columns in lever
                    self.n_rows, self.n_cols = tuple(
                        [int(x) for x in line.strip().split(",")]
                    )
                except ValueError:
                    assert False, (
                        f"/!\\ ERROR: Invalid input file - n_rows and n_cols (line {i})"
                    )

            elif i == 1:
                try:
                    # Cost targets - used for both UCS and A*
                    self.cost_min_tgt, self.cost_max_tgt = tuple(
                        [float(x) for x in line.strip().split(",")]
                    )
                except ValueError:
                    assert False, (
                        f"/!\\ ERROR: Invalid input file - cost targets (line {i})"
                    )

            elif i == 2:
                try:
                    # Nodes expanded targets - used for A* heuristic eval only
                    self.nodes_min_tgt, self.nodes_max_tgt = tuple(
                        [float(x) for x in line.strip().split(",")]
                    )
                except ValueError:
                    assert False, (
                        f"/!\\ ERROR: Invalid input file - nodes targets (line {i})"
                    )

            elif i == 3:
                try:
                    # UCS target times
                    self.ucs_time_min_tgt, self.ucs_time_max_tgt = tuple(
                        [float(x) for x in line.strip().split(",")]
                    )
                except ValueError:
                    assert False, (
                        f"/!\\ ERROR: Invalid input file - UCS time targets (line {i})"
                    )

            elif i == 4:
                try:
                    # A* target times
                    self.a_star_time_min_tgt, self.a_star_time_max_tgt = tuple(
                        [float(x) for x in line.strip().split(",")]
                    )
                except ValueError:
                    assert False, (
                        f"/!\\ ERROR: Invalid input file - A* time targets (line {i})"
                    )

            elif len(line.strip()) > 0:
                grid_data.append(list(line.strip()))
                assert len(grid_data[-1]) == self.n_cols, (
                    f"/!\\ ERROR: Invalid input file - incorrect map row length (line {i})"
                )

            i += 1

        # Extract initial, goal, trap, and lever positions
        trap_positions = []  # Record positions of traps
        lever_positions = []  # Record positions of levers
        self.init_row, self.init_col = None, None
        self.goal_row, self.goal_col = None, None
        for r in range(self.n_rows):
            for c in range(self.n_cols):
                if grid_data[r][c] == self.PLAYER_TILE:
                    assert self.init_row is None and self.init_col is None, (
                        "/!\\ ERROR: Invalid input file - more than one initial player position"
                    )
                    self.init_row, self.init_col = r, c
                    # assume player starts on air tile
                    grid_data[r][c] = self.AIR_TILE
                elif grid_data[r][c] == self.GOAL_TILE:
                    assert self.goal_row is None and self.goal_col is None, (
                        "/!\\ ERROR: Invalid input file - more than one exit position"
                    )
                    self.goal_row, self.goal_col = r, c
                    # assume exit is placed on air tile
                    grid_data[r][c] = self.AIR_TILE
                elif grid_data[r][c] == self.DRAWBRIDGE:
                    trap_positions.append((r, c))
                elif grid_data[r][c] == self.TRAPDOOR:
                    trap_positions.append((r, c))
                elif grid_data[r][c] == self.LEVER:
                    lever_positions.append((r, c))

        assert self.init_row is not None and self.init_col is not None, (
            "/!\\ ERROR: Invalid input file - No player initial position"
        )
        assert self.goal_row is not None and self.goal_col is not None, (
            "/!\\ ERROR: Invalid input file - No exit position"
        )

        # Store schematic data if available
        self.schematic_data = schematic_data if schematic_data else None

        # Map lever positions to trap positions using schematic data
        assert self.schematic_data is not None, (
            "/!\\ ERROR: Lever-trap mapping requires schematic data in level file"
        )
        lever_map_positions = self._create_schematic_mapping(
            lever_positions, trap_positions
        )

        self.lever_positions = lever_positions
        self.lever_map_positions = lever_map_positions
        self.trap_positions = [
            lever_map_positions[lever_position] for lever_position in lever_positions
        ]

        # Create lever-trap mapping grid
        self.lever_trap_mapping = self._create_lever_trap_mapping_grid()

        assert len(grid_data) == self.n_rows, (
            "/!\\ ERROR: Invalid input file - incorrect number of map rows"
        )
        self.grid_data = grid_data

    def get_init_state(self):
        """
        Get a state representation instance for the initial state.
        :return: initial state
        """
        return GameState(
            self.init_row, self.init_col, tuple(0 for _ in self.trap_positions)
        )

    def check_valid_action(self, state, action):
        """Check a given action is able to be performed in a given state.
        :param state: current GameState
        :param action: an element of self.ACTIONS
        :return: successful [True/False]
        """
        floor_tile = self.grid_data[state.row + 1][state.col]
        if action in (
            self.WALK_LEFT,
            self.WALK_RIGHT,
            self.SPRINT_LEFT,
            self.SPRINT_RIGHT,
            self.JUMP,
        ):
            if action == self.SPRINT_LEFT:
                if (
                    self.grid_data[state.row + 1][state.col - 1]
                    in (self.TRAPDOOR, self.DRAWBRIDGE)
                    and state.trap_status[
                        self.trap_positions.index((state.row + 1, state.col - 1))
                    ]
                    == 0
                ):
                    # Cannot sprint over open trap
                    return False
                elif self.grid_data[state.row][state.col - 1] not in (
                    self.AIR_TILE,
                    self.LADDER_TILE,
                    self.LEVER,
                ):
                    # Cannot sprint through solid block
                    return False
                elif self.grid_data[state.row + 1][state.col - 1] not in (
                    self.SOLID_TILE,
                    self.DRAWBRIDGE,
                    self.TRAPDOOR,
                    self.LADDER_TILE,
                ):
                    # Cannot sprint over air
                    return False
            elif action == self.SPRINT_RIGHT:
                if (
                    self.grid_data[state.row + 1][state.col + 1]
                    in (self.TRAPDOOR, self.DRAWBRIDGE)
                    and state.trap_status[
                        self.trap_positions.index((state.row + 1, state.col + 1))
                    ]
                    == 0
                ):
                    # Cannot sprint over open trap
                    return False
                elif self.grid_data[state.row][state.col + 1] not in (
                    self.AIR_TILE,
                    self.LADDER_TILE,
                    self.LEVER,
                ):
                    # Cannot sprint through solid block
                    return False
                elif self.grid_data[state.row + 1][state.col + 1] not in (
                    self.SOLID_TILE,
                    self.DRAWBRIDGE,
                    self.TRAPDOOR,
                    self.LADDER_TILE,
                ):
                    # Cannot sprint over air
                    return False

            if (
                floor_tile in (self.TRAPDOOR, self.DRAWBRIDGE)
                and state.trap_status[
                    self.trap_positions.index((state.row + 1, state.col))
                ]
                == 0
            ):
                # Cannot walk on a trap that is not locked
                return False
            elif floor_tile == self.LADDER_TILE and self.grid_data[state.row][state.col] == self.LADDER_TILE and action == self.JUMP:
                # Cannot jump while climbing a ladder
                return False
            elif floor_tile not in (self.SOLID_TILE, self.DRAWBRIDGE, self.TRAPDOOR, self.LADDER_TILE):
                # Cannot walk on invalid surface (tiles not listed)
                return False
        elif action == self.DROP:
            if (
                floor_tile in (self.TRAPDOOR, self.DRAWBRIDGE)
                and state.trap_status[
                    self.trap_positions.index((state.row + 1, state.col))
                ]
                == 1
            ):
                # Cannot drop through locked trap
                return False
            elif floor_tile not in (
                self.LADDER_TILE,
                self.AIR_TILE,
                self.DRAWBRIDGE,
                self.TRAPDOOR,
                self.LEVER,
            ):
                # Cannot drop through invalid tile (tiles not listed)
                return False
        elif (
            action == self.CLIMB
            and self.grid_data[state.row][state.col] != self.LADDER_TILE
        ):
            # Cannot climb on invalid tile (can only climb on ladders)
            return False

        return True

    def check_collision(self, next_position, next_trap_status):
        """Check a given action is able to be performed in a given state.
        :param next_position: next position of player based on action
        :param next_trap_status: trap status of new state
        :return: collision [True/False]
        """
        next_row, next_col = next_position
        # Check that next_state is within bounds
        if not (0 <= next_row < self.n_rows and 0 <= next_col < self.n_cols):
            # Next state is out of bounds
            return True

        # Check for a collision (with either next state or a closed drawbridge)
        if self.grid_data[next_row][next_col] == self.SOLID_TILE:
            # Collision with a solid tile
            return True

        elif (
            self.grid_data[next_row + 1][next_col] == self.DRAWBRIDGE
            and next_trap_status[self.trap_positions.index((next_row + 1, next_col))]
            == 0
        ):
            # Collision with a closed drawbridge
            return True

        return False

    def perform_action(self, state, action):
        """
        Perform the given action on the given state, and return whether the
        action was successful (i.e. valid and collision free) and the resulting
        new state.
        :param state: current GameState
        :param action: an element of self.ACTIONS
        :return: (successful [True/False], next_state [GameState])
        """

        # Check action is valid
        if not self.check_valid_action(state, action):
            return False, state.deepcopy()

        next_trap_status = list(state.trap_status)
        # Get coordinates for next state
        if action == self.WALK_LEFT:
            next_row, next_col = (state.row, state.col - 1)  # left

        elif action == self.WALK_RIGHT:
            next_row, next_col = (state.row, state.col + 1)  # right

        elif action == self.SPRINT_LEFT:
            next_row, next_col = (state.row, state.col - 2)  # left 2

        elif action == self.SPRINT_RIGHT:
            next_row, next_col = (state.row, state.col + 2)  # right 2

        elif action == self.JUMP:
            next_row, next_col = (state.row - 1, state.col)  # up (jump)

        elif action == self.CLIMB:
            next_row, next_col = (state.row - 1, state.col)  # up (climb)

        elif action == self.DROP:
            next_row, next_col = (state.row + 1, state.col)  # down

        elif action == self.ACTIVATE:  # activate lever
            # Check if player is on a lever tile
            # Activate trap if they are on a lever tile
            next_row, next_col = state.row, state.col

            if (state.row, state.col) in self.lever_map_positions.keys():
                # Player is on a lever
                trap_pos = self.lever_map_positions[(state.row, state.col)]

                if state.trap_status[self.trap_positions.index(trap_pos)] == 0:
                    # Activate lever
                    next_trap_status[
                        self.trap_positions.index(
                            self.lever_map_positions[(state.row, state.col)]
                        )
                    ] = 1
                else:
                    # Deactivate lever
                    next_trap_status[
                        self.trap_positions.index(
                            self.lever_map_positions[(state.row, state.col)]
                        )
                    ] = 0

        else:
            assert False, "/!\\ ERROR: Invalid action given to perform_action()"

        if self.check_collision((next_row, next_col), next_trap_status):
            return False, state.deepcopy()

        return True, GameState(next_row, next_col, tuple(next_trap_status))

    def is_solved(self, state):
        """
        Check if the game has been solved (i.e. player at exit and all levers activated)
        :param state: current GameState
        :return: True if solved, False otherwise
        """
        all_traps_activated = True
        for status in state.trap_status:
            if status == 0:
                all_traps_activated = False
                break
        return (
            state.row == self.goal_row
            and state.col == self.goal_col
            and all_traps_activated
        )

    def render(self, state):
        """
        Render the map's current state to terminal
        """
        for r in range(self.n_rows):
            line = ""
            for c in range(self.n_cols):
                if state.row == r and state.col == c:
                    # Current tile is player
                    line += self.grid_data[r][c] + "P" + self.grid_data[r][c]
                elif self.goal_row == r and self.goal_col == c:
                    # Current tile is exit
                    line += self.grid_data[r][c] + "G" + self.grid_data[r][c]
                else:
                    line += self.grid_data[r][c] * 3
            print(line)
        print("\n" * 2)

    def _create_schematic_mapping(self, lever_positions, trap_positions):
        """
        Create lever-to-trap mapping based on schematic data.

        Args:
            lever_positions: List of lever coordinate tuples
            trap_positions: List of trap coordinate tuples

        Returns:
            dict: Mapping from lever positions to trap positions
        """
        lever_map_positions = {}

        # Map levers to traps based on shared IDs in schematic
        for lever_pos in lever_positions:
            lever_row, lever_col = lever_pos
            if lever_row < len(self.schematic_data) and lever_col < len(
                self.schematic_data[lever_row]
            ):
                schematic_char = self.schematic_data[lever_row][lever_col]
                # Find the trap with the same ID
                for trap_pos in trap_positions:
                    trap_row, trap_col = trap_pos
                    if (
                        trap_row < len(self.schematic_data)
                        and trap_col < len(self.schematic_data[trap_row])
                        and self.schematic_data[trap_row][trap_col] == schematic_char
                    ):
                        lever_map_positions[lever_pos] = trap_pos
                        break

        # Ensure all levers are mapped
        assert len(lever_map_positions) == len(lever_positions), (
            f"/!\\ ERROR: Not all levers could be mapped via schematic. "
            f"Mapped {len(lever_map_positions)} of {len(lever_positions)} levers."
        )

        return lever_map_positions

    def _create_lever_trap_mapping_grid(self):
        """
        Create a mapping grid where lever-trap pairs share the same ID number.

        Returns:
            2D list where non-zero values indicate lever-trap relationships
        """
        # Initialize mapping grid with zeros
        mapping_grid = [[0 for _ in range(self.n_cols)] for _ in range(self.n_rows)]

        # Assign unique IDs to each lever-trap pair
        pair_id = 1

        for lever_pos in self.lever_positions:
            trap_pos = self.lever_map_positions[lever_pos]

            # Assign same ID to both lever and trap positions
            mapping_grid[lever_pos[0]][lever_pos[1]] = pair_id
            mapping_grid[trap_pos[0]][trap_pos[1]] = pair_id

            pair_id += 1

        return mapping_grid

    def get_lever_trap_id(self, row, col):
        """
        Get the lever-trap pair ID for a given position.

        Args:
            row, col: Grid coordinates

        Returns:
            int: Pair ID (0 if position not part of any lever-trap system)
        """
        if 0 <= row < self.n_rows and 0 <= col < self.n_cols:
            return self.lever_trap_mapping[row][col]
        return 0

    def get_related_positions(self, row, col):
        """
        Get all positions related to the given position via lever-trap relationships.

        Args:
            row, col: Grid coordinates

        Returns:
            list: List of (row, col) tuples that are connected via lever-trap system
        """
        pair_id = self.get_lever_trap_id(row, col)
        if pair_id == 0:
            return []

        related_positions = []
        for r in range(self.n_rows):
            for c in range(self.n_cols):
                if self.lever_trap_mapping[r][c] == pair_id:
                    related_positions.append((r, c))

        return related_positions

    def is_lever_trap_position(self, row, col):
        """
        Check if a position is part of any lever-trap system.

        Args:
            row, col: Grid coordinates

        Returns:
            bool: True if position is a lever or trap
        """
        return self.get_lever_trap_id(row, col) != 0