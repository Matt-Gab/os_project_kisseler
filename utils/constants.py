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

# Memory drawing constants
MEM_MIN_PART_HEIGHT = 40
MEM_COLOR_OS = "#E0E0E0"
MEM_COLOR_FREE = "white"
MEM_COLOR_JOB = "lightblue"
MEM_ARROW_FONT = ("Arial", 8)
MEM_LABEL_FONT = ("Arial", 8)
MEM_TIME_FONT = ("Arial", 9, "bold")
MEM_LEFT_MARGIN = 30
MEM_SNAPSHOT_WIDTH = 100
MEM_ARROW_AREA_WIDTH = 40