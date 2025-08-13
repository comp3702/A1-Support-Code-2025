import tkinter as tk
import time

from game_env import GameEnv

"""
Graphical Visualiser for Cheese Hunter. You may modify this file if desired.

COMP3702 Assignment 1 "Cheese Hunter" Support Code, 2025
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
        self.lever_images = None
        self.trap_images = None
        self.game_env = game_env
        init_state = game_env.get_init_state()
        self.last_state = init_state

        # Choose small or large mode
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

        self.window.title("Cheese Hunter Visualiser")
        self.window.geometry(
            f"{self.game_env.n_cols * self.tile_w}x{self.game_env.n_rows * self.tile_h}"
        )

        self.canvas = tk.Canvas(self.window)
        self.canvas.configure(bg="white")
        self.canvas.pack(fill="both", expand=True)

        self.trapdoors_locked = {}
        self.trapdoors_closed = {}
        self.trapdoors_open = {}
        self.drawbridges_closed = {}
        self.drawbridges_open = {}
        self.trapdoor_levers_open = {}
        self.trapdoor_levers_closed = {}
        self.drawbridge_levers_open = {}
        self.drawbridge_levers_closed = {}

        # Load images
        if small_mode:
            self.background = tk.PhotoImage(file="gui_assets/Small/background_wall.png")
            self.tile_player = tk.PhotoImage(file="gui_assets/Small/player_mouse.png")
            self.tile_cheese = tk.PhotoImage(file="gui_assets/Small/goal_cheese.png")
            self.tile_ladder = tk.PhotoImage(file="gui_assets/Small/ladder.png")
            self.tile_stone = tk.PhotoImage(file="gui_assets/Small/solid_wall.png")

            for i in range(10):
                self.trapdoors_locked[i] = tk.PhotoImage(
                    file=f"gui_assets/Small/trapdoors/locked_trapdoor_{i}.png"
                )
                self.trapdoors_closed[i] = tk.PhotoImage(
                    file=f"gui_assets/Small/trapdoors/closed_trapdoor_{i}.png"
                )
                self.trapdoors_open[i] = tk.PhotoImage(
                    file=f"gui_assets/Small/trapdoors/open_trapdoor_{i}.png"
                )
                self.drawbridges_closed[i] = tk.PhotoImage(
                    file=f"gui_assets/Small/drawbridges/closed_drawbridge_{i}.png"
                )
                self.drawbridges_open[i] = tk.PhotoImage(
                    file=f"gui_assets/Small/drawbridges/open_drawbridge_{i}.png"
                )

                self.trapdoor_levers_closed[i] = tk.PhotoImage(
                    file=f"gui_assets/Small/trapdoors/closed_trapdoor_lever_{i}.png"
                )
                self.trapdoor_levers_open[i] = tk.PhotoImage(
                    file=f"gui_assets/Small/trapdoors/open_trapdoor_lever_{i}.png"
                )
                self.drawbridge_levers_closed[i] = tk.PhotoImage(
                    file=f"gui_assets/Small/drawbridges/closed_drawbridge_lever_{i}.png"
                )
                self.drawbridge_levers_open[i] = tk.PhotoImage(
                    file=f"gui_assets/Small/drawbridges/open_drawbridge_lever_{i}.png"
                )

        else:
            self.background = tk.PhotoImage(file="gui_assets/background_wall.png")
            self.tile_player = tk.PhotoImage(file="gui_assets/player_mouse.png")
            self.tile_cheese = tk.PhotoImage(file="gui_assets/goal_cheese.png")
            self.tile_ladder = tk.PhotoImage(file="gui_assets/ladder.png")
            self.tile_stone = tk.PhotoImage(file="gui_assets/solid_wall.png")

            for i in range(10):
                self.trapdoors_locked[i] = tk.PhotoImage(
                    file=f"gui_assets/trapdoors/locked_trapdoor_{i}.png"
                )
                self.trapdoors_closed[i] = tk.PhotoImage(
                    file=f"gui_assets/trapdoors/closed_trapdoor_{i}.png"
                )
                self.trapdoors_open[i] = tk.PhotoImage(
                    file=f"gui_assets/trapdoors/open_trapdoor_{i}.png"
                )
                self.drawbridges_closed[i] = tk.PhotoImage(
                    file=f"gui_assets/drawbridges/closed_drawbridge_{i}.png"
                )
                self.drawbridges_open[i] = tk.PhotoImage(
                    file=f"gui_assets/drawbridges/open_drawbridge_{i}.png"
                )

                self.trapdoor_levers_closed[i] = tk.PhotoImage(
                    file=f"gui_assets/trapdoors/closed_trapdoor_lever_{i}.png"
                )
                self.trapdoor_levers_open[i] = tk.PhotoImage(
                    file=f"gui_assets/trapdoors/open_trapdoor_lever_{i}.png"
                )
                self.drawbridge_levers_closed[i] = tk.PhotoImage(
                    file=f"gui_assets/drawbridges/closed_drawbridge_lever_{i}.png"
                )
                self.drawbridge_levers_open[i] = tk.PhotoImage(
                    file=f"gui_assets/drawbridges/open_drawbridge_lever_{i}.png"
                )

        # Draw background (all permanent features, i.e. everything except player, traps, and levers)
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
                elif self.game_env.grid_data[r][c] in (
                    GameEnv.AIR_TILE,
                    GameEnv.TRAPDOOR,
                    GameEnv.DRAWBRIDGE,
                    GameEnv.LEVER,
                ):
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
                        image=self.tile_cheese,
                        anchor=tk.NW,
                    )

        # Draw player for initial state
        self.player_image = None
        self.draw_player(init_state.row, init_state.col)

        # Draw traps and levers for inital state
        self.lever_images = None
        self.trap_images = None
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

        # Remove and re-draw player
        self.canvas.delete(self.player_image)
        self.draw_player(state.row, state.col)

        # Tween player to new position
        for i in range(1, self.TWEEN_STEPS + 1):
            time.sleep(self.TWEEN_DELAY)
            self.canvas.delete(self.player_image)
            r1 = self.last_state.row + (i / self.TWEEN_STEPS) * (
                state.row - self.last_state.row
            )
            c1 = self.last_state.col + (i / self.TWEEN_STEPS) * (
                state.col - self.last_state.col
            )
            # Remove old player position, draw new player position
            self.draw_player(r1, c1)
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
        drawbridge_id = 0
        trapdoor_id = 0

        for i, t in enumerate(state.trap_status):
            if (
                self.game_env.grid_data[self.game_env.trap_positions[i][0]][
                    self.game_env.trap_positions[i][1]
                ]
                == self.game_env.DRAWBRIDGE
            ):
                # Draw open or closed drawbridge and lever based on trap status
                if t == 1:
                    trap_img = self.canvas.create_image(
                        (self.game_env.trap_positions[i][1] * self.tile_w),
                        ((self.game_env.trap_positions[i][0] - 1) * self.tile_h),
                        image=self.drawbridges_open[drawbridge_id],
                        anchor=tk.NW,
                    )
                    lever_img = self.canvas.create_image(
                        (self.game_env.lever_positions[i][1] * self.tile_w),
                        (self.game_env.lever_positions[i][0] * self.tile_h),
                        image=self.drawbridge_levers_open[drawbridge_id],
                        anchor=tk.NW,
                    )
                else:
                    trap_img = self.canvas.create_image(
                        (self.game_env.trap_positions[i][1] * self.tile_w),
                        ((self.game_env.trap_positions[i][0] - 1) * self.tile_h),
                        image=self.drawbridges_closed[drawbridge_id],
                        anchor=tk.NW,
                    )
                    lever_img = self.canvas.create_image(
                        (self.game_env.lever_positions[i][1] * self.tile_w),
                        (self.game_env.lever_positions[i][0] * self.tile_h),
                        image=self.drawbridge_levers_closed[drawbridge_id],
                        anchor=tk.NW,
                    )
                drawbridge_id += 1
            else:
                # Draw open or closed trapdoor and lever based on trap status
                # and player position (open trapdoor if player is above or on it)
                if t == 1:  # trapdoor locked
                    lever_img = self.canvas.create_image(
                        (self.game_env.lever_positions[i][1] * self.tile_w),
                        (self.game_env.lever_positions[i][0] * self.tile_h),
                        image=self.trapdoor_levers_open[trapdoor_id],
                        anchor=tk.NW,
                    )
                    trap_img = self.canvas.create_image(
                        (self.game_env.trap_positions[i][1] * self.tile_w),
                        (self.game_env.trap_positions[i][0] * self.tile_h),
                        image=self.trapdoors_locked[trapdoor_id],
                        anchor=tk.NW,
                    )
                else:  # trapdoor unlocked
                    lever_img = self.canvas.create_image(
                        (self.game_env.lever_positions[i][1] * self.tile_w),
                        (self.game_env.lever_positions[i][0] * self.tile_h),
                        image=self.trapdoor_levers_closed[trapdoor_id],
                        anchor=tk.NW,
                    )
                    if (state.row + 1, state.col) == self.game_env.trap_positions[
                        i
                    ] or (state.row, state.col) == self.game_env.trap_positions[i]:
                        trap_img = self.canvas.create_image(
                            (self.game_env.trap_positions[i][1] * self.tile_w),
                            (self.game_env.trap_positions[i][0] * self.tile_h),
                            image=self.trapdoors_open[trapdoor_id],
                            anchor=tk.NW,
                        )
                    else:
                        trap_img = self.canvas.create_image(
                            (self.game_env.trap_positions[i][1] * self.tile_w),
                            (self.game_env.trap_positions[i][0] * self.tile_h),
                            image=self.trapdoors_closed[trapdoor_id],
                            anchor=tk.NW,
                        )
                trapdoor_id += 1

            self.trap_images.append(trap_img)
            self.lever_images.append(lever_img)

    def draw_player(self, row, col):
        self.player_image = self.canvas.create_image(
            (col * self.tile_w),
            (row * self.tile_h),
            image=self.tile_player,
            anchor=tk.NW,
        )
