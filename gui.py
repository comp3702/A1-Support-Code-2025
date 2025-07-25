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
        screen_width, screen_height = self.window.winfo_screenwidth(), self.window.winfo_screenheight()
        if (screen_width < self.game_env.n_cols * self.TILE_W) or (screen_height < self.game_env.n_rows * self.TILE_H):
            small_mode = True
            self.tile_w = self.TILE_W_SMALL
            self.tile_h = self.TILE_H_SMALL
        else:
            small_mode = False
            self.tile_w = self.TILE_W
            self.tile_h = self.TILE_H

        self.window.title("Dragon Game Visualiser")
        self.window.geometry(f'{self.game_env.n_cols * self.tile_w}x{self.game_env.n_rows * self.tile_h}')

        self.canvas = tk.Canvas(self.window)
        self.canvas.configure(bg="white")
        self.canvas.pack(fill="both", expand=True)

        # load images
        if small_mode:
            self.tile_dirt = tk.PhotoImage(file='gui_assets/game_tile_dirt_small.png')
            self.tile_dragon = tk.PhotoImage(file='gui_assets/game_tile_dragon_small.png')
            self.tile_exit = tk.PhotoImage(file='gui_assets/game_tile_exit_small.png')
            self.tile_ladder = tk.PhotoImage(file='gui_assets/game_tile_ladder_small.png')
            self.tile_lava = tk.PhotoImage(file='gui_assets/game_tile_lava_small.png')
            self.tile_stone = tk.PhotoImage(file='gui_assets/game_tile_stone_small.png')
            self.tile_gems = [tk.PhotoImage(file='gui_assets/game_tile_gem_red_small.png'),
                              tk.PhotoImage(file='gui_assets/game_tile_gem_green_small.png'),
                              tk.PhotoImage(file='gui_assets/game_tile_gem_blue_small.png'),
                              tk.PhotoImage(file='gui_assets/game_tile_gem_yellow_small.png')]
        else:
            self.tile_dirt = tk.PhotoImage(file='gui_assets/game_tile_dirt.png')
            self.tile_dragon = tk.PhotoImage(file='gui_assets/game_tile_dragon.png')
            self.tile_exit = tk.PhotoImage(file='gui_assets/game_tile_exit.png')
            self.tile_ladder = tk.PhotoImage(file='gui_assets/game_tile_ladder.png')
            self.tile_lava = tk.PhotoImage(file='gui_assets/game_tile_lava.png')
            self.tile_stone = tk.PhotoImage(file='gui_assets/game_tile_stone.png')
            self.tile_gems = [tk.PhotoImage(file='gui_assets/game_tile_gem_red.png'),
                              tk.PhotoImage(file='gui_assets/game_tile_gem_green.png'),
                              tk.PhotoImage(file='gui_assets/game_tile_gem_blue.png'),
                              tk.PhotoImage(file='gui_assets/game_tile_gem_yellow.png')]

        # draw background (all permanent features, i.e. everything except dragon and gems)
        for r in range(self.game_env.n_rows):
            for c in range(self.game_env.n_cols):
                if self.game_env.grid_data[r][c] == GameEnv.SOLID_TILE:
                    self.canvas.create_image((c * self.tile_w), (r * self.tile_h), image=self.tile_stone, anchor=tk.NW)
                elif self.game_env.grid_data[r][c] == GameEnv.LADDER_TILE:
                    self.canvas.create_image((c * self.tile_w), (r * self.tile_h), image=self.tile_dirt, anchor=tk.NW)
                    self.canvas.create_image((c * self.tile_w), (r * self.tile_h), image=self.tile_ladder, anchor=tk.NW)
                if self.game_env.grid_data[r][c] == GameEnv.AIR_TILE:
                    self.canvas.create_image((c * self.tile_w), (r * self.tile_h), image=self.tile_dirt, anchor=tk.NW)
                if self.game_env.grid_data[r][c] == GameEnv.LAVA_TILE:
                    self.canvas.create_image((c * self.tile_w), (r * self.tile_h), image=self.tile_lava, anchor=tk.NW)
                if r == self.game_env.exit_row and c == self.game_env.exit_col:
                    self.canvas.create_image((c * self.tile_w), (r * self.tile_h), image=self.tile_exit, anchor=tk.NW)

        # draw gems for initial state
        self.gem_images = None
        self.draw_gems(init_state)

        # draw dragon position for initial state
        self.dragon_image = None
        self.draw_dragon(init_state.row, init_state.col)

        self.window.update()
        self.last_update_time = time.time()

    def update_state(self, state):
        # remove all gems and re-add uncollected gems
        for g in self.gem_images:
            self.canvas.delete(g)
        self.draw_gems(state)
        # remove and re-draw dragon
        self.canvas.delete(self.dragon_image)
        self.draw_dragon(state.row, state.col)

        # tween dragon to new position
        for i in range(1, self.TWEEN_STEPS + 1):
            time.sleep(self.TWEEN_DELAY)
            self.canvas.delete(self.dragon_image)
            r1 = self.last_state.row + (i / self.TWEEN_STEPS) * (state.row - self.last_state.row)
            c1 = self.last_state.col + (i / self.TWEEN_STEPS) * (state.col - self.last_state.col)
            # remove old dragon position, draw new dragon position
            self.draw_dragon(r1, c1)
            self.window.update()
        self.last_state = state

        # delay until next update
        self.window.update()

        time_since_last_update = time.time() - self.last_update_time
        time.sleep(max(self.UPDATE_DELAY - time_since_last_update, 0))
        self.last_update_time = time.time()

    def draw_gems(self, state):
        self.gem_images = []
        for i, (gr, gc) in enumerate(self.game_env.gem_positions):
            if state.gem_status[i] == 0:
                tile_gem = self.tile_gems[i % len(self.tile_gems)]
                img = self.canvas.create_image((gc * self.tile_w), (gr * self.tile_h), image=tile_gem, anchor=tk.NW)
                self.gem_images.append(img)

    def draw_dragon(self, row, col):
        self.dragon_image = self.canvas.create_image((col * self.tile_w), (row * self.tile_h),
                                                     image=self.tile_dragon, anchor=tk.NW)








