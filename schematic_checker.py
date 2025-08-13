#!/usr/bin/env python3

"""
Game Grid and Schematic Visualization Tool

Renders the game grid with schematic numbers overlaid to help debug
lever-trap mapping issues and visualize level structure.
"""

import sys
from game_env import GameEnv


def render_game_with_schematic(filename):
    """
    Render the game grid with schematic numbers overlaid.
    
    Args:
        filename: Path to level file
    """
    print(f"=== Level: {filename} ===\n")
    
    try:
        # Read the file manually to get basic data
        with open(filename, 'r') as f:
            lines = [line.rstrip() for line in f.readlines()]
        
        # Parse basic info
        n_rows, n_cols = map(int, lines[1].split(', '))
        
        # Find grid data section
        grid_start_idx = None
        schematic_start_idx = None
        
        for i, line in enumerate(lines):
            if line.strip() == "# grid data":
                grid_start_idx = i + 1
            elif line.strip() == "# Schematic":
                schematic_start_idx = i + 1
                break
        
        # Extract grid data
        grid_data = []
        if grid_start_idx:
            for i in range(grid_start_idx, grid_start_idx + n_rows):
                if i < len(lines):
                    grid_data.append(list(lines[i]))
        
        # Extract schematic data
        schematic_data = []
        if schematic_start_idx:
            for i in range(schematic_start_idx, len(lines)):
                schematic_data.append(list(lines[i]))
        
        print("GAME GRID:")
        for i, row in enumerate(grid_data):
            print(f"{i:2d}: {''.join(row)}")
        
        print(f"\nSCHEMATIC DATA:")
        for i, row in enumerate(schematic_data):
            print(f"{i:2d}: {''.join(row)}")
        
        print(f"\nOVERLAY (Game + Schematic):")
        print("Grid chars with schematic numbers where they exist:")
        
        for r in range(n_rows):
            line = f"{r:2d}: "
            for c in range(n_cols):
                game_char = grid_data[r][c] if r < len(grid_data) and c < len(grid_data[r]) else ' '
                
                # Get schematic character if it exists
                schematic_char = ' '
                if r < len(schematic_data) and c < len(schematic_data[r]):
                    schematic_char = schematic_data[r][c]
                
                # Show game char with schematic overlay
                if schematic_char != ' ' and schematic_char.isdigit():
                    line += f"{game_char}{schematic_char}"
                else:
                    line += f"{game_char} "
            print(line)
        
        # Find lever and trap positions manually
        lever_positions = []
        trap_positions = []
        
        for r in range(len(grid_data)):
            for c in range(len(grid_data[r])):
                if grid_data[r][c] == 'L':
                    lever_positions.append((r, c))
                elif grid_data[r][c] in ['T', 'D']:
                    trap_positions.append((r, c))
        
        print(f"\nLEVER POSITIONS: {lever_positions}")
        print(f"TRAP POSITIONS: {trap_positions}")
        
        # Try to show which levers can't be mapped
        print(f"\nMANUAL MAPPING ANALYSIS:")
        mapped_count = 0
        for lever_pos in lever_positions:
            lever_row, lever_col = lever_pos
            schematic_char = ' '
            if lever_row < len(schematic_data) and lever_col < len(schematic_data[lever_row]):
                schematic_char = schematic_data[lever_row][lever_col]
            
            if schematic_char.isdigit() and schematic_char != '0':
                # Try to find matching trap
                found_trap = False
                for trap_pos in trap_positions:
                    trap_row, trap_col = trap_pos
                    trap_schematic = ' '
                    if trap_row < len(schematic_data) and trap_col < len(schematic_data[trap_row]):
                        trap_schematic = schematic_data[trap_row][trap_col]
                    
                    if trap_schematic == schematic_char:
                        print(f"  ✓ Lever at {lever_pos} (ID {schematic_char}) -> Trap at {trap_pos}")
                        mapped_count += 1
                        found_trap = True
                        break
                
                if not found_trap:
                    print(f"  ✗ Lever at {lever_pos} (ID {schematic_char}) -> NO MATCHING TRAP")
            else:
                print(f"  ✗ Lever at {lever_pos} -> NO SCHEMATIC ID (found '{schematic_char}')")
        
        print(f"\nSUMMARY: {mapped_count}/{len(lever_positions)} levers mapped successfully")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Render game grid with schematic overlay."""
    if len(sys.argv) != 2:
        print("Usage: python lever_trap_mapper.py <level_file>")
        print("Example: python lever_trap_mapper.py testcases/level_6.txt")
        return
    
    filename = sys.argv[1]
    render_game_with_schematic(filename)


if __name__ == "__main__":
    main()