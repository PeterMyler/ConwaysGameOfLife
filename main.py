import pygame as pg
import numpy as np
from random import random
from time import time, sleep
pg.font.init()

# constants:
CELL_SIZE = 5  # size of each cell (CHANGE THIS ONE)
SCREEN_SIZE = 1000  # n*n pixel window
ARRAY_SIZE = int(SCREEN_SIZE // CELL_SIZE)  # size of the array, based on the scale factor
LIVE_CELL_COLOUR = (0, 190, 0)  # (R, G, B)
CELL_GEN_CHANCE = 0.4  # chance of cell being alive
MAX_FPS = 0  # fps limit (0 = no limit)
ERASER_SIZE = 5  # cells eraser size (square of side 1/n of the array size)
WRAP = False  # wrapping is ~3x slower

# rule types:
classic = (3, 2, 3)
chaotic = (2, 2, 3)
trippin = (2, 1, 5)  # best with manual start
flicker = (1, 4, 5)  # best with manual start
tv_noise = (2, 4, 5)
rule_type = classic

# other variables
INT_RGB = sum(LIVE_CELL_COLOUR[2 - i] * (256 ** i) for i in range(3))
arr = np.array([[0] * ARRAY_SIZE] * ARRAY_SIZE, dtype=int)  # main array; 0 - dead cell, 1 - live cell
all_positions = [(y, x) for y in range(ARRAY_SIZE) for x in range(ARRAY_SIZE)]  # array of all positions
offsets = np.array([[i, j] for i in range(-1, 2) for j in range(-1, 2)])

ttime = -1
time_taken = 0
fps = 0
paused = False
font = pg.font.SysFont('Comic Sans', 30)  # cus it's gotta be Comic Sans

# set up pygame:
window = pg.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
pg.display.set_caption("Peter\'s Game Of Life")
window.fill(0)

# initial state:
pattern = np.array([[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0],
                    [1,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                    [1,1,0,0,0,0,0,0,0,0,1,0,0,0,1,0,1,1,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]])
pos = (3, 3)
arr[pos[0]:pos[0]+pattern.shape[1], pos[1]:pos[1]+pattern.shape[0]] = pattern.transpose()

################################################
# functions


def hard_limit(value: int, lower: int = 0, upper: int = ARRAY_SIZE - 1) -> int:
    if value < lower:
        return lower
    elif value > upper:
        return upper
    else:
        return value


def numpy_wrap(o: int, ax: int, array):
    return array.take(range(-1 + o, 2 + o), mode='wrap', axis=ax)


def clear_game_array() -> None:
    arr[:] = 0


def randomize_game_array() -> None:
    clear_game_array()
    for j in range(ARRAY_SIZE):
        for i in range(ARRAY_SIZE):
            if random() <= CELL_GEN_CHANCE: arr[j, i] = 1


################################################
# main game loop

print("running")
t = time()
while True:
    # break if game-window is closed
    if pg.QUIT in [event.type for event in pg.event.get()]: break

    ################################################
    # keyboard inputs

    keys = pg.key.get_pressed()  # get the state of all keys
    if keys[pg.K_c]: clear_game_array()  # c   -> clear array
    if keys[pg.K_r]: randomize_game_array()  # r   -> randomize array
    if keys[pg.K_ESCAPE]: break  # esc -> exit game
    if keys[pg.K_p]:  # p   -> pause/unpause game
        paused = not paused
        while pg.key.get_pressed()[pg.K_p]: pg.display.update()

    ################################################
    # mouse inputs

    mouse_buttons = pg.mouse.get_pressed()
    if True in mouse_buttons:
        mouse_pos = pg.mouse.get_pos()
        posX = mouse_pos[1] // CELL_SIZE
        posY = mouse_pos[0] // CELL_SIZE

        if not (0 <= posX < ARRAY_SIZE and 0 <= posY < ARRAY_SIZE): continue

        if mouse_buttons[0]:  # for creating live cells (left click)
            arr[posY, posX] = 1
        elif mouse_buttons[2]:  # for deleting live cells (right click)
            arr[posY, posX] = 0
        elif mouse_buttons[1]:  # for big eraser (middle click)
            length = int(ARRAY_SIZE / ERASER_SIZE)

            x1 = hard_limit(posX - length // 2)
            y1 = hard_limit(posY - length // 2)

            arr[y1:y1 + length + 1, x1:x1 + length + 1] = 0

    ################################################
    # play mode

    ones = np.argwhere(arr == 1)  # all the locations of live cells (ones)
    ones_len = len(ones)
    ones_percentage = ones_len / (ARRAY_SIZE * ARRAY_SIZE)
    fps = MAX_FPS

    if not paused and ones_len != 0 and not (MAX_FPS and (time() - ttime < 1 / MAX_FPS)):
        ttime = time()

        # making a list of cells to check the rules for
        # only live cells and ones around them need to be checked
        # HOWEVER, if there are a lot of live cells
        # we just check every cell (it's faster, trust me bro)
        # (I chose the value through some experimentation)
        to_check = []
        if ones_percentage <= 0.1:
            for offset in offsets:
                to_check.extend(np.add(ones, [offset] * ones_len))
            # (wrapping/discarding of invalid positions is preformed later)

            # removing duplicate cell positions
            to_check = list(set(map(tuple, to_check)))

        ################################################

        # creating a copy of the game array and changing the main array
        changes = []
        for posY, posX in (to_check or all_positions):
            if WRAP:
                # wrap coords:
                posX %= ARRAY_SIZE
                posY %= ARRAY_SIZE

                adjacent_cells_arr = numpy_wrap(posX, 1, numpy_wrap(posY, 0, arr))
            else:
                if not (0 <= posX < ARRAY_SIZE and 0 <= posY < ARRAY_SIZE):
                    continue

                adjacent_cells_arr = arr[max(posY - 1, 0):posY + 2, max(posX - 1, 0):posX + 2]

            # getting number of neighbours (subtract 1 if current cell is alive)
            neighbours = int(np.count_nonzero(adjacent_cells_arr)) - int(arr[posY, posX] == 1)

            # applying the rules:
            # dead cell -> live cell, if it has rule_type[0] (default: 3) neighbours
            if arr[posY, posX] == 0:
                if neighbours == rule_type[0]:
                    changes.append((posY, posX))
            else:
                # live cells -> dead cells, if it doesn't have
                # from rule_type[1] to rule_type[2] neighbors (default: 2 to 3)
                if not (rule_type[1] <= neighbours <= rule_type[2]):
                    changes.append((posY, posX))

        # perform changes:
        for posY, posX in changes:
            arr[posY, posX] ^= 1

        # fps calculations:
        time_taken = time() - t
        if time_taken != 0:
            fps = round(1 / time_taken, 2)
        t = time()


    ################################################
    # update the screen
    pg.surfarray.blit_array(window, np.kron(arr, np.full((CELL_SIZE, CELL_SIZE), INT_RGB)))

    text_surface = font.render(f"FPS: {fps} {'(paused)' if paused else ''}", False, (255, 255, 255))
    window.blit(text_surface, (SCREEN_SIZE-170, 0))

    pg.display.update()

    ################################################
    # print(f"fps: {fps}; {round(ones_percentage*100, 1)}%")
