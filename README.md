# Conways Game of Life
This is my best effort at implementing a somewhat efficient "Conways Game of Life" program in Python, with some extra functionalities such as: editing/drawing, pausing, fps limiting and extra modes.\
(I know Python is probably the last language I should've used for an "efficient" program, but hey - I love Python, so just let me be)

## Requirements
This project requires Pygame and Numpy to run
```
pip install pygame
pip install numpy
```

## Game Rules
1. Survival: Any live cell with 2 or 3 live neighbors stays alive.
2. Death by underpopulation: Any live cell with fewer than 2 live neighbors dies.
3. Death by overpopulation: Any live cell with more than 3 live neighbors dies.
4. Birth: Any dead cell with exactly 3 live neighbors becomes a live cell.

## Controls
### Keyboard:
 - *r* - generate random game array
 - *c* - clear array
 - *p* - pause/unpause game
 - *esc* - exit
### Mouse:
 - *Right click* - set the cell at the cursor to alive
 - *Left click* - set the cell at the cursor to dead
 - *Middle click* - set all cells in a square around the cursor to dead
