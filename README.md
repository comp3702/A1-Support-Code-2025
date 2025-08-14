# Assignment 1 Support Code

This is the support code for COMP3702 Assignment 1 "Cheese Hunter", 2025.

The following files are provided:

**game_env.py**

This file contains a class representing a Cheese Hunter level environment, storing the dimensions of the environment, initial player position, exit (cheese) position, lever positions, trap positions, mapping of levers to traps, targets for path cost, run time and number of nodes expanded, the tile type of each grid position, and a list of all available actions.

This file contains a number of functions which will be useful in developing your solver:

~~~~~
__init__(filename)
~~~~~
Constructs a new instance based on the given input filename.


~~~~~
get_init_state()
~~~~~
Returns a GameState object (see below) representing the initial state of the level.


~~~~~
perform_action(state, action)
~~~~~
Simulates the outcome of performing the given 'action' starting from the given 'state', where 'action' is an element of GameEnv.ACTIONS and 'state' is a GameState object. Returns a tuple (success, next_state), where success is True (if the action is valid and does not collide) or False (if the action is invalid or collides), and next_state is a GameState
object.


~~~~~
is_solved(state)
~~~~~
Checks whether the given 'state' (a GameState object) is solved (i.e. all traps/levers are activated and player at exit). Returns True (solved) or False (not solved).


~~~~~
render(state)
~~~~~
Prints a graphical representation of the given 'state' (a GameState object) to the terminal - you may find this useful for debugging.


**game_state.py**

This file contains a class representing a Cheese Hunter state, storing the position of the player and the status of all levers/traps in the level (1 for activated, 0 for unactivated).

~~~~~
__init__(row, col, trap_status)
~~~~~
Constructs a new GameState instance, where row and column are integers between 0 and n_rows, n_cols respectively, and trap_status is a tuple of length n_traps, where each element is 1 or 0.


**play_game.py**


This file contains a script which launches an interactive game session when run. Becoming familiar with the game mechanics may be helpful in designing your solution.

To start playing, try:
`python play_game.py testcases/level_1.txt`

The script takes 1 command line argument:
- input_filename, which must be a valid testcase file (e.g. one of the provided files in the testcases directory)

When prompted for an action, type one of the available action strings (e.g. wr, wl, etc) and press enter to perform the entered action (make sure the terminal and not the display window is selected when entering actions).


**solution.py**

Template file for you to implement your solution to Assignment 1.

You should implement each of the method stubs contained in this file. You may add additional methods and/or classes to this file if you wish. You may also create additional source files and import to this file if you wish.

We recommend you implement UCS first, then attempt A* after your UCS implementation is working.


**tester.py**

This file contains a script which can be used to debug and/or evaluate your solution.

The script takes up to 3 command line arguments:
- search_type, which should be "ucs" or "a_star"
- testcase_filename, which must be a valid testcase file (e.g. one of the provided files in the testcases directory)
- (optional) "-v" to enable visualisation of the resulting trajectory


**testcases**

A directory containing input files which can be used to evaluate your solution.

The format of a testcase file is:
~~~~~
num_rows, num_cols
cost targets (min score target, max score target)
nodes targets (min score target, max score target)
UCS run time targets (min score target, max score target)
A* run time targets (min score target, max score target)
grid_data (row 1)
...
grid_data (row num_rows)
~~~~~

Testcase files can contain comments, starting with '#', which are ignored by the input file parser.


### Lever-Trap System

For levels containing levers (L) and traps (T for trapdoors, D for drawbridges), the game uses a **schematic-based mapping system**:

**Level Format:**
```
# Standard level data as above
grid_data (row 1)
...
grid_data (row num_rows)
# Schematic
schematic_row_1
...
schematic_row_num_rows
```

- The schematic section uses numeric IDs (1, 2, 3, etc.) to connect levers to traps
- Positions with the same ID number are connected - activating a lever toggles its paired trap
- Example: If the schematic has '1' at position (2,5) and '1' at position (7,3), then the lever at (2,5) controls the trap at (7,3)

Available Methods:
- `env.get_lever_trap_id(row, col)` - Get the connection ID for a position (0 if not connected)
- `env.get_related_positions(row, col)` - Get all positions connected to this one
- `env.is_lever_trap_position(row, col)` - Check if position is part of lever-trap system

These methods can be useful for pathfinding algorithms to understand trap dependencies (perhaps).
