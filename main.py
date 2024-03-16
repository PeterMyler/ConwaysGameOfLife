import pygame as pg
import numpy as np
from random import randint
from time import time
pg.font.init()
font = pg.font.SysFont('Comic Sans MS', 30)

screen_size = 1000  # n*n pixel window
scale = 10  # scale/zoom constant
size = int(screen_size // scale)  # size of the array, based on the scale factor

live_colour = 0*256 + 255*256 + 190*256

# rule types:
classic = (3, 2, 3)
chaotic = (2, 2, 3)
trippin = (2, 1, 5)  # best with manual start
flicker = (1, 4, 5)  # cool with manual start
tv_noise = (2, 4, 5)

rule_type = classic

# random cell generation:
chance = 50  # chance of cell being live (percent)

# setting up game window:
window = pg.display.set_mode((screen_size, screen_size))
pg.display.set_caption('ConwaysGameOfLife')
window.fill(0)

limit_fps = False
max_fps = 10  # fps limit
ttime = -1
time_taken = 0
fps = 0

arr = np.array([[0] * size] * size, dtype=int)  # initialising main array; 0 - dead cell, 1 - live cell
all_positions = [[y, x] for y in range(size) for x in range(size)]

# all offsets from a center (vectors to get adjacent cells)
offsets = np.array([[-1, -1], [-1, 0], [0, -1], [0, 1], [1, 0], [1, 1], [-1, 1], [1, -1]])

running = True
paused = False

################################################


def lower_limit(value):
    if value < 0: return 0
    else: return value


def upper_limit(value, limit):
    if value > limit: return limit
    else: return value


################################################

print("running")
t = time()
while running:
    # checking if game-window is closed
    if pg.QUIT in [event.type for event in pg.event.get()]: running = False

    ################################################

    # keyboard controls:
    if pg.key.get_pressed()[pg.K_ESCAPE]: running = False  # esc -> exit game
    if pg.key.get_pressed()[pg.K_c]:  # c -> clear screen
        arr[:] = 0
    paused = pg.key.get_pressed()[pg.K_p]  # p -> game is paused
    if pg.key.get_pressed()[pg.K_r]:
        arr[:] = 0
        for j in range(size):
            for i in range(size):
                rand_int = randint(0, 100 // chance)
                if rand_int == 1:
                    arr[j, i] = 1

    ################################################

    # mouse inputs:
    mouse_buttons = pg.mouse.get_pressed()
    if True in mouse_buttons:  # 0 - left, 1 - middle, 2 - right
        mouse_pos = pg.mouse.get_pos()
        posX = int(mouse_pos[1] / scale)
        posY = int(mouse_pos[0] / scale)

        if mouse_buttons[0]:  # for creating live cells (left)
            arr[posY, posX] = 1

        elif mouse_buttons[2]:  # for erasing (right)
            arr[posY, posX] = 0

        elif mouse_buttons[1]:  # for big eraser (middle)
            length = int(size/5)

            x1, x2 = lower_limit(posX - length // 2), upper_limit(posX + round(length / 2), size)
            y1, y2 = lower_limit(posY - length // 2), upper_limit(posY + round(length / 2), size)

            arr[y1:y2, x1:x2] = 0

    ################################################

    # updating the screen and setting the fps limit:
    pg.surfarray.blit_array(window, np.kron(arr, np.full((scale, scale), live_colour)))

    text_surface = font.render(f"FPS: {fps}", False, (255, 255, 255))
    window.blit(text_surface, (0, 0))

    pg.display.update()

    ################################################

    # play mode:
    ones = np.argwhere(arr == 1)  # all the locations of live cells (ones)
    ones_len = len(ones)

    if not paused and ones_len != 0 and (not limit_fps or time() - ttime >= 1/max_fps):
        ttime = time()

        # making a list of cells to check the rules for:
        # (we only need to check live cells and the ones adjacent to them)
        # (if there are loads of live cells then we just check every position, its faster trust me bro)
        if ones_len / (size * size) < (0.14 - 0.015*(rule_type[2]-rule_type[1]+1)):
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
            if not (0 <= posX <= size - 1 and 0 <= posY <= size - 1): continue

            # getting number of neighbours:
            adjacent_cells_arr = arr_c[lower_limit(posY-1):posY + 2, lower_limit(posX-1):posX + 2]
            neighbours = int(np.count_nonzero(adjacent_cells_arr))  # number of non-zero values in grid
            # (1 extra neighbour if current cell is live, accounted for later)

            # applying the rules:
            # dead cell -> live cell, if it has 3 neighbours
            if arr_c[posY, posX] == 0 and neighbours == rule_type[0]:  # classic: 3, chaotic: 2
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
