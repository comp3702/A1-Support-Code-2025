import sys
import time

from game_env import GameEnv
from control.game_env import GameEnv as ControlEnv
from solution import Solver

"""
Tester script.

Use this script to debug and/or evaluate your solution. You may modify this file if desired.

COMP3702 Assignment 1 "Cheese Hunter" Support Code, 2025
"""

VISUALISE_TIME_PER_STEP = 0.7


def print_usage():
    print("Usage: python tester.py [search_type] [testcase_file] [-v (optional)]")
    print("    search_type = 'ucs' or 'a_star'")
    print("    testcase_file = filename of a valid testcase file (e.g. level_1.txt)")
    print("    if -v is specified, the solver's trajectory will be visualised")


def main(arglist):
    if len(arglist) != 2 and len(arglist) != 3:
        print_usage()
        return

    search_type = arglist[0]
    if search_type not in ['ucs', 'a_star']:
        print("/!\\ ERROR: Invalid search_type given")
        print_usage()
        return

    # Load environment
    testcase_file = arglist[1]
    game_env = GameEnv(testcase_file)

    if len(arglist) == 3:
        if arglist[2] == '-v':
            visualise = True
        else:
            print(f"/!\\ ERROR: Invalid option given: {arglist[2]}")
            print_usage()
            return
    else:
        visualise = False

    # For small environments, take average time over multiple trials
    if game_env.ucs_time_min_tgt < 0.01:
        trials = 50
    elif game_env.ucs_time_min_tgt < 0.1:
        trials = 5
    else:
        trials = 1

    # Run search
    actions = None
    t0 = time.time()
    for _ in range(trials):
        solver = Solver(game_env)
        if search_type == 'ucs':
            actions = solver.search_ucs()
        else:
            solver.preprocess_heuristic()
            actions = solver.search_a_star()
    run_time = (time.time() - t0) / trials

    # Evaluate solution
    control_env = ControlEnv(testcase_file)
    persistent_state = control_env.get_init_state()
    total_cost = 0.0
    error_occurred = False
    if visualise:
        try:
            from gui import GUI
            gui = GUI(game_env)
        except ModuleNotFoundError:
            gui = None
            control_env.render(persistent_state)
            time.sleep(VISUALISE_TIME_PER_STEP)
    else:
        gui = None
    for i in range(len(actions)):
        a = actions[i]
        try:
            total_cost += game_env.ACTION_COST[a]
            success, persistent_state = game_env.perform_action(persistent_state, a)
            if not success:
                print("/!\\ ERROR: Action resulting in Collision performed at step " + str(i))
                error_occurred = True
            if visualise:
                if gui is not None:
                    gui.update_state(persistent_state)
                else:
                    control_env.render(persistent_state)
                    time.sleep(VISUALISE_TIME_PER_STEP)
        except KeyError:
            print("/!\\ ERROR: Unrecognised action performed at step " + str(i))
            error_occurred = True

    if error_occurred:
        print("/!\\ ERROR: Collision, Game Over or Unrecognised Action Occurred")

    if game_env.is_solved(persistent_state):
        print(f"Level completed! Solution cost = {round(total_cost, 1)}; Runtime = {round(run_time, 10)} seconds")
    else:
        print("/!\\ ERROR: Level not completed after all actions performed.")
        return


if __name__ == '__main__':
    main(sys.argv[1:])

