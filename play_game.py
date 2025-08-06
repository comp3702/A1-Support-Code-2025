import sys

from game_env import GameEnv
from gui import GUI

"""
play_game.py

Running this file launches an interactive game session. Becoming familiar with the game mechanics may be helpful in
designing your solution.

The script takes 1 argument:
- input_filename, which must be a valid testcase file (e.g. one of the provided files in the testcases directory)

When prompted for an action, type one of the available action strings (e.g. wr, wl, etc) and press enter to perform the
entered action.

COMP3702 Assignment 1 "Cheese Hunter" Support Code, 2025
"""


def main(arglist):
    if len(arglist) != 1:
        print("Running this file launches an interactive game session.")
        print("Usage: play_game.py [input_filename]")
        return -1

    input_file = arglist[0]

    game_env = GameEnv(input_file)
    gui = GUI(game_env)
    persistent_state = game_env.get_init_state()
    actions = []
    total_cost = 0

    print('Available actions: wl, wr, sl, sr, j, c, d, a, q[quit]')

    # Run simulation
    while True:
        gui.update_state(persistent_state)
        print('Choose an action >>', end=' ')
        a = input().strip()
        if 'q' in a:
            print('Quitting.')
            break
        if a not in GameEnv.ACTIONS:
            print('Invalid action. Choose again.')
            continue
        actions.append(a)
        total_cost += game_env.ACTION_COST[a]
        success, persistent_state = game_env.perform_action(persistent_state, a)
        if not success:
            print('Collision occurred or invalid action. Please try a different action.')
        if game_env.is_solved(persistent_state):
            gui.update_state(persistent_state)
            print(f'Level completed with total cost of {round(total_cost, 1)}!')
            break

    return 0


if __name__ == '__main__':
    main(sys.argv[1:])
