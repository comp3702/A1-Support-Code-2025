import tkinter as tk
import time

from game_env import GameEnv

"""
Graphical Visualiser for Dragon Game. You may modify this file if desired.

COMP3702 Assignment 1 "Dragon Game" Support Code

Last updated by njc 15/08/22
"""


class GUI:
    TILE_W = 32
    TILE_H = 32
    TILE_W_SMALL = 16
    TILE_H_SMALL = 16

    UPDATE_DELAY = 0.5
    TWEEN_STEPS = 16
    TWEEN_DELAY = 0.005

    def __init__(self, game_env):
        self.game_env = game_env
        init_state = game_env.get_init_state()
        self.last_state = init_state

        # choose small or large mode
        self.window = tk.Tk()
        screen_width, screen_height = (
            self.window.winfo_screenwidth(),
            self.window.winfo_screenheight(),
        )
        if (screen_width < self.game_env.n_cols * self.TILE_W) or (
            screen_height < self.game_env.n_rows * self.TILE_H
        ):
            small_mode = True
            self.tile_w = self.TILE_W_SMALL
            self.tile_h = self.TILE_H_SMALL
        else:
            small_mode = False
            self.tile_w = self.TILE_W
            self.tile_h = self.TILE_H

        self.window.title("Dragon Game Visualiser")
        self.window.geometry(
            f"{self.game_env.n_cols * self.tile_w}x{self.game_env.n_rows * self.tile_h}"
        )

        self.canvas = tk.Canvas(self.window)
        self.canvas.configure(bg="white")
        self.canvas.pack(fill="both", expand=True)

        # load images
        if small_mode:
            self.background = tk.PhotoImage(file="gui_assets/background_small.png")
            self.tile_dragon = tk.PhotoImage(
                file="gui_assets/game_tile_dragon_small.png"
            )
            self.tile_exit = tk.PhotoImage(file="gui_assets/game_tile_exit_small.png")
            self.tile_ladder = tk.PhotoImage(
                file="gui_assets/game_tile_ladder_small.png"
            )
            self.tile_stone = tk.PhotoImage(file="gui_assets/game_tile_stone_small.png")
            self.tile_open_drawbridge = tk.PhotoImage(
                file="gui_assets/drawbridge_open_small.png"
            )
            self.tile_closed_drawbridge = tk.PhotoImage(
                file="gui_assets/drawbridge_open_small.png"
            )
            self.tile_open_trapdoor = tk.PhotoImage(
                file="gui_assets/trapdoor_open_small.png"
            )
            self.tile_closed_trapdoor = tk.PhotoImage(
                file="gui_assets/trapdoor_closed_small.png"
            )
            self.tile_open_lever_1 = tk.PhotoImage(
                file="gui_assets/lever_1_closed_small.png"
            )
            self.tile_closed_lever_1 = tk.PhotoImage(
                file="gui_assets/lever_1_closed_small.png"
            )
            self.tile_open_lever_2 = tk.PhotoImage(
                file="gui_assets/lever_2_open_small.png"
            )
            self.tile_closed_lever_2 = tk.PhotoImage(
                file="gui_assets/lever_2_open_small.png"
            )

        else:
            self.background = tk.PhotoImage(file="gui_assets/background.png")
            self.tile_dragon = tk.PhotoImage(file="gui_assets/game_tile_dragon.png")
            self.tile_exit = tk.PhotoImage(file="gui_assets/game_tile_exit.png")
            self.tile_ladder = tk.PhotoImage(file="gui_assets/game_tile_ladder.png")
            self.tile_stone = tk.PhotoImage(file="gui_assets/game_tile_stone.png")
            self.tile_open_drawbridge = tk.PhotoImage(
                file="gui_assets/drawbridge_open.png"
            )
            self.tile_closed_drawbridge = tk.PhotoImage(
                file="gui_assets/drawbridge_closed.png"
            )
            self.tile_open_trapdoor = tk.PhotoImage(file="gui_assets/trapdoor_open.png")
            self.tile_closed_trapdoor = tk.PhotoImage(
                file="gui_assets/trapdoor_closed.png"
            )
            self.tile_open_lever_1 = tk.PhotoImage(file="gui_assets/lever_1_open.png")
            self.tile_closed_lever_1 = tk.PhotoImage(
                file="gui_assets/lever_1_closed.png"
            )
            self.tile_open_lever_2 = tk.PhotoImage(file="gui_assets/lever_2_open.png")
            self.tile_closed_lever_2 = tk.PhotoImage(
                file="gui_assets/lever_2_closed.png"
            )

        # draw background (all permanent features, i.e. everything except dragon and gems)
        for r in range(self.game_env.n_rows):
            for c in range(self.game_env.n_cols):
                if self.game_env.grid_data[r][c] == GameEnv.SOLID_TILE:
                    self.canvas.create_image(
                        (c * self.tile_w),
                        (r * self.tile_h),
                        image=self.tile_stone,
                        anchor=tk.NW,
                    )
                elif self.game_env.grid_data[r][c] == GameEnv.LADDER_TILE:
                    self.canvas.create_image(
                        (c * self.tile_w),
                        (r * self.tile_h),
                        image=self.background,
                        anchor=tk.NW,
                    )
                    self.canvas.create_image(
                        (c * self.tile_w),
                        (r * self.tile_h),
                        image=self.tile_ladder,
                        anchor=tk.NW,
                    )
                if self.game_env.grid_data[r][c] == GameEnv.AIR_TILE:
                    self.canvas.create_image(
                        (c * self.tile_w),
                        (r * self.tile_h),
                        image=self.background,
                        anchor=tk.NW,
                    )
                if self.game_env.grid_data[r][c] == GameEnv.TRAPDOOR:
                    self.canvas.create_image(
                        (c * self.tile_w),
                        (r * self.tile_h),
                        image=self.background,
                        anchor=tk.NW,
                    )
                if self.game_env.grid_data[r][c] == GameEnv.DRAWBRIDGE:
                    self.canvas.create_image(
                        (c * self.tile_w),
                        (r * self.tile_h),
                        image=self.background,
                        anchor=tk.NW,
                    )

                if r == self.game_env.goal_row and c == self.game_env.goal_col:
                    self.canvas.create_image(
                        (c * self.tile_w),
                        (r * self.tile_h),
                        image=self.tile_exit,
                        anchor=tk.NW,
                    )

        # draw dragon position for initial state
        self.dragon_image = None
        self.draw_dragon(init_state.row, init_state.col)

        # Draw background before levers and trap assets
        for lever in self.game_env.lever_positions:
            self.canvas.create_image(
                (lever[1] * self.tile_w),
                (lever[0] * self.tile_h),
                image=self.background,
                anchor=tk.NW,
            )
        for trap in self.game_env.trap_positions:
            self.canvas.create_image(
                (trap[1] * self.tile_w),
                (trap[0] * self.tile_h),
                image=self.background,
                anchor=tk.NW,
            )

        self.draw_traps_and_levers(init_state)

        self.window.update()
        self.last_update_time = time.time()

    def update_state(self, state):
        # Delete then redraw all traps and levers
        for trap in self.trap_images:
            self.canvas.delete(trap)

        for lever in self.lever_images:
            self.canvas.delete(lever)

        self.draw_traps_and_levers(state)

        # Remove and re-draw dragon
        self.canvas.delete(self.dragon_image)
        self.draw_dragon(state.row, state.col)

        # Tween dragon to new position
        for i in range(1, self.TWEEN_STEPS + 1):
            time.sleep(self.TWEEN_DELAY)
            self.canvas.delete(self.dragon_image)
            r1 = self.last_state.row + (i / self.TWEEN_STEPS) * (
                state.row - self.last_state.row
            )
            c1 = self.last_state.col + (i / self.TWEEN_STEPS) * (
                state.col - self.last_state.col
            )
            # Remove old dragon position, draw new dragon position
            self.draw_dragon(r1, c1)
            self.window.update()
        self.last_state = state

        # Delay until next update
        self.window.update()

        time_since_last_update = time.time() - self.last_update_time
        time.sleep(max(self.UPDATE_DELAY - time_since_last_update, 0))
        self.last_update_time = time.time()

    def draw_traps_and_levers(self, state):
        self.trap_images = []
        self.lever_images = []

        for i, t in enumerate(state.trap_status):
            if self.game_env.trap_icons[i] == self.game_env.DRAWBRIDGE:
                # Draw open or closed drawbridge and lever based on trap status
                if t == 1:
                    trap_img = self.canvas.create_image(
                        (self.game_env.trap_positions[i][1] * self.tile_w),
                        ((self.game_env.trap_positions[i][0] - 1) * self.tile_h),
                        image=self.tile_open_drawbridge,
                        anchor=tk.NW,
                    )
                    lever_img = self.canvas.create_image(
                        (self.game_env.lever_positions[i][1] * self.tile_w),
                        (self.game_env.lever_positions[i][0] * self.tile_h),
                        image=self.tile_open_lever_2,
                        anchor=tk.NW,
                    )
                else:
                    trap_img = self.canvas.create_image(
                        (self.game_env.trap_positions[i][1] * self.tile_w),
                        ((self.game_env.trap_positions[i][0] - 1) * self.tile_h),
                        image=self.tile_closed_drawbridge,
                        anchor=tk.NW,
                    )
                    lever_img = self.canvas.create_image(
                        (self.game_env.lever_positions[i][1] * self.tile_w),
                        (self.game_env.lever_positions[i][0] * self.tile_h),
                        image=self.tile_closed_lever_2,
                        anchor=tk.NW,
                    )
            else:
                # Draw open or closed trapdoor and lever based on trap status
                # and player position (open trapdoor if player is on it)
                if t == 1:
                    lever_img = self.canvas.create_image(
                        (self.game_env.lever_positions[i][1] * self.tile_w),
                        (self.game_env.lever_positions[i][0] * self.tile_h),
                        image=self.tile_open_lever_1,
                        anchor=tk.NW,
                    )
                    trap_img = self.canvas.create_image(
                        (self.game_env.trap_positions[i][1] * self.tile_w),
                        (self.game_env.trap_positions[i][0] * self.tile_h),
                        image=self.tile_closed_trapdoor,
                        anchor=tk.NW,
                    )
                else:
                    lever_img = self.canvas.create_image(
                        (self.game_env.lever_positions[i][1] * self.tile_w),
                        (self.game_env.lever_positions[i][0] * self.tile_h),
                        image=self.tile_closed_lever_1,
                        anchor=tk.NW,
                    )
                    if (state.row + 1, state.col) == self.game_env.trap_positions[i]:
                        trap_img = self.canvas.create_image(
                            (self.game_env.trap_positions[i][1] * self.tile_w),
                            (self.game_env.trap_positions[i][0] * self.tile_h),
                            image=self.tile_open_trapdoor,
                            anchor=tk.NW,
                        )
                    else:
                        trap_img = self.canvas.create_image(
                            (self.game_env.trap_positions[i][1] * self.tile_w),
                            (self.game_env.trap_positions[i][0] * self.tile_h),
                            image=self.tile_closed_trapdoor,
                            anchor=tk.NW,
                        )

            self.trap_images.append(trap_img)
            self.lever_images.append(lever_img)

    def draw_dragon(self, row, col):
        self.dragon_image = self.canvas.create_image(
            (col * self.tile_w),
            (row * self.tile_h),
            image=self.tile_dragon,
            anchor=tk.NW,
        )
