#!/usr/bin/env python3

"""
Lever-Trap Mapping Visualization Tool

Creates a secondary mapping grid showing relationships between levers and traps.
Each lever-trap pair gets assigned the same unique ID number in both positions.
"""

from game_env import GameEnv


def create_lever_trap_mapping_grid(env):
    """
    Create a mapping grid where lever-trap pairs share the same ID number.
    
    Args:
        env: GameEnv instance
        
    Returns:
        2D list where non-zero values indicate lever-trap relationships
    """
    # Initialize mapping grid with zeros
    mapping_grid = [[0 for _ in range(env.n_cols)] for _ in range(env.n_rows)]
    
    # Assign unique IDs to each lever-trap pair
    pair_id = 1
    
    for lever_pos in env.lever_positions:
        trap_pos = env.lever_map_positions[lever_pos]
        
        # Assign same ID to both lever and trap positions
        mapping_grid[lever_pos[0]][lever_pos[1]] = pair_id
        mapping_grid[trap_pos[0]][trap_pos[1]] = pair_id
        
        pair_id += 1
    
    return mapping_grid


def print_mapping_grids(env, mapping_grid):
    """
    Print both the original grid and the mapping grid side by side.
    """
    print("Original Grid:")
    for row in env.grid_data:
        print(''.join(row))
    
    print("\nLever-Trap Mapping Grid:")
    print("(Numbers show lever-trap pairs, 0 = no relationship)")
    for row in mapping_grid:
        print(' '.join(f'{cell:2d}' for cell in row))
    
    print("\nMapping Details:")
    for i, lever_pos in enumerate(env.lever_positions, 1):
        trap_pos = env.lever_map_positions[lever_pos]
        lever_symbol = env.grid_data[lever_pos[0]][lever_pos[1]]
        print(f"ID {i}: Lever '{lever_symbol}' at {lever_pos} -> Trap at {trap_pos}")


def main():
    """Test the mapping concept with the traps testcase."""
    env = GameEnv('testcases/traps_test.txt')
    mapping_grid = create_lever_trap_mapping_grid(env)
    print_mapping_grids(env, mapping_grid)
    
    # Show how this could be useful for pathfinding algorithms
    print(f"\nPathfinding Benefits:")
    print(f"- Quick lookup: Is position (r,c) part of a lever-trap system? Check if mapping_grid[r,c] != 0")
    print(f"- Find related positions: All positions with same ID are connected")
    print(f"- State representation: Include mapping_grid values in state for more informed search")


if __name__ == "__main__":
    main()