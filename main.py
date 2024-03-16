import pygame as pg
import numpy as np
from random import random
from time import time
pg.font.init()
font = pg.font.SysFont('Comic Sans', 30)  # gotta be Comic Sans

# constants:
SCREEN_SIZE = 1000  # n*n pixel window
SCALE = 10  # scale/zoom constant
ARRAY_SIZE = int(SCREEN_SIZE // SCALE)  # size of the array, based on the scale factor
LIVE_CELL_COLOUR = (0, 190, 0)  # (R, G, B)
CELL_GEN_CHANCE = 0.5  # chance of cell being live

# fps constants:
limit_fps = False
max_fps = 10  # fps limit
ttime = -1
time_taken = 0
fps = 0

# rule types:
classic = (3, 2, 3)
chaotic = (2, 2, 3)
trippin = (2, 1, 5)  # best with manual start
flicker = (1, 4, 5)  # best with manual start
tv_noise = (2, 4, 5)

rule_type = classic

# set up pygame:
window = pg.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
pg.display.set_caption('ConwaysGameOfLife')
window.fill(0)
INT_RGB = sum(LIVE_CELL_COLOUR[2-i] * (256 ** i) for i in range(3))

arr = np.array([[0] * ARRAY_SIZE] * ARRAY_SIZE, dtype=int)  # initialising main array; 0 - dead cell, 1 - live cell
all_positions = [[y, x] for y in range(ARRAY_SIZE) for x in range(ARRAY_SIZE)]

# all offsets from a center (vectors to get adjacent cells)
offsets = np.array([[[i, j] for i in range(0, 2) for j in range(0, 2) if not i == j == 0]])


running = True
paused = False

################################################


def lower_limit(value):
    if value < 0: return 0
    else: return value


def upper_limit(value, limit):
    if value > limit: return limit
    else: return value


def clear_game_array():
    arr[:] = 0


def randomize_game_array():
    clear_game_array()
    for j in range(ARRAY_SIZE):
        for i in range(ARRAY_SIZE):
            if random() <= CELL_GEN_CHANCE: arr[j, i] = 1


################################################

print("running")
t = time()
while running:
    ################################################
    # check if game-window is closed
    if pg.QUIT in [event.type for event in pg.event.get()]: break

    ################################################
    # keyboard controls

    keys = pg.key.get_pressed()  # get keys pressed
    paused = keys[pg.K_p]                    # p   -> game is paused
    if keys[pg.K_c]: clear_game_array()      # c   -> clear game
    if keys[pg.K_r]: randomize_game_array()  # r   -> randomize game
    if keys[pg.K_ESCAPE]: break              # esc -> exit game

    ################################################
    # mouse inputs

    mouse_buttons = pg.mouse.get_pressed()
    if True in mouse_buttons:
        mouse_pos = pg.mouse.get_pos()
        posX = int(mouse_pos[1] / SCALE)
        posY = int(mouse_pos[0] / SCALE)

        if mouse_buttons[0]:  # for creating live cells (left click)
            arr[posY, posX] = 1

        elif mouse_buttons[2]:  # for erasing (right click)
            arr[posY, posX] = 0

        elif mouse_buttons[1]:  # for big eraser (middle click)
            length = int(ARRAY_SIZE / 5)

            x1, x2 = lower_limit(posX - length // 2), upper_limit(posX + round(length / 2), ARRAY_SIZE)
            y1, y2 = lower_limit(posY - length // 2), upper_limit(posY + round(length / 2), ARRAY_SIZE)

            arr[y1:y2, x1:x2] = 0

    ################################################
    # update the screen
    pg.surfarray.blit_array(window, np.kron(arr, np.full((SCALE, SCALE), INT_RGB)))

    text_surface = font.render(f"FPS: {fps}", False, (255, 255, 255))
    window.blit(text_surface, (0, 0))

    pg.display.update()

    ################################################

    # play mode:
    ones = np.argwhere(arr == 1)  # all the locations of live cells (ones)
    ones_len = len(ones)
    ones_percentage = ones_len / (ARRAY_SIZE * ARRAY_SIZE)

    if not paused and ones_len != 0 and (not limit_fps or time() - ttime >= 1/max_fps):
        ttime = time()

        # making a list of cells to check the rules for:
        # only live cells and the ones around them need to be checked
        # HOWEVER, if there are a lot of live cells then we just check every cell (its faster trust me bro)
        # I just chose the values through some experimentation
        if ones_percentage < (0.14 - 0.015 * (rule_type[2] - rule_type[1] + 1)):
            to_check = []
            for offset in offsets:
                to_check.extend(np.add(ones, [offset] * ones_len))
                # (check for valid coordinates of each offset cell is performed later)

            # adding the live sells themselves (the centers)
            to_check.extend(ones)
            to_check = list(set(map(lambda k: tuple(k), to_check)))  # removing duplicate cell positions
        else:
            to_check = all_positions.copy()

        ################################################

        # applying the rules of the game and changing a copy of the array:
        arr_c = np.copy(arr)  # copying array
        for posY, posX in to_check:
            # making sure cell isn't off-screen:
            if not (0 <= posX <= ARRAY_SIZE - 1 and 0 <= posY <= ARRAY_SIZE - 1): continue

            # getting number of neighbours:
            adjacent_cells_arr = arr_c[lower_limit(posY-1):posY + 2, lower_limit(posX-1):posX + 2]
            neighbours = int(np.count_nonzero(adjacent_cells_arr))  # number of non-zero values in grid
            # (1 extra neighbour if current cell is live, accounted for later)

            # applying the rules:
            # dead cell -> live cell, if it has 3 neighbours
            if arr_c[posY, posX] == 0 and neighbours == rule_type[0]:
                arr[posY, posX] = 1

            # live cells -> dead cells, if it doesn't have 2 or 3 neighbors
            # ("-1" because we previously count the cell as its own neighbour)
            if arr_c[posY, posX] == 1 and not (rule_type[1] <= neighbours - 1 <= rule_type[2]):
                arr[posY, posX] = 0

    time_taken = time() - t
    if time_taken != 0:
        fps = round(1/time_taken, 2)
    else:
        fps = 0
    t = time()
