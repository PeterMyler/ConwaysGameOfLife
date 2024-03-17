# Conways Game of Life
This is my best effort at implementing a somewhat efficient "Conways Game of Life" program in Python with some extra functionalities such as: editing/drawing, pausing, fps limiting and extra modes.\
(I know Python is the last language I should've used for an "efficent" program, but hey. I love Python. So just let me be)

## Requirements
This project requires Pygame and Numpy to run
```
pip install pygame
pip install numpy
```

## Game Rules
You probably already know them

## Controls
### Keyboard:
 - *r* - generate random game array
 - *c* - clear array
 - *p* - hold to pause game
 - *esc* - exit
### Mouse:
 - *Right click* - set the cell at the cursor to alive
 - *Left click* - set the cell at the cursor to dead
 - *Middle click* - set all cells in a square around the cursor to dead
