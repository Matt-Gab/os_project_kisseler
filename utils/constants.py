# utils/constants.py

# Gantt chart drawing dimensions
SQUARE_SIZE = 40         # width and height of each job block (perfect square)
JOB_HEIGHT = SQUARE_SIZE # same as SQUARE_SIZE
TOP_MARGIN = 20
LEFT_OFFSET = SQUARE_SIZE // 2   # spacer before the first square
AXIS_HEIGHT = 25
LABEL_FONT = ("Arial", 8)

# Colors
JOB_OUTLINE_COLOR = "black"
AXIS_TICK_COLOR = "gray"

IDLE_FILL_COLOR = "black"
IDLE_TEXT_COLOR = "white"