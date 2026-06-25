# utils/disk_drawer.py
import tkinter as tk
from utils.constants import *

def draw_disk_movement(canvas, sequence, max_track):
    """
    Draws the disk head movement chart.
    sequence: list of track numbers (start + each request in order)
    max_track: ignored.
    """
    canvas.delete("all")
    if not sequence:
        return

    # ---- Unique tracks and equal spacing ----
    unique_tracks = sorted(set(sequence))
    # Map each track to an index (0 .. len-1)
    track_to_index = {track: idx for idx, track in enumerate(unique_tracks)}
    # Desired horizontal spacing between adjacent unique tracks
    SPACING = 40   # pixels

    def track_to_x(track):
        idx = track_to_index[track]
        return DISK_LEFT_MARGIN + idx * SPACING

    # ---- Canvas size ----
    total_width = track_to_x(unique_tracks[-1]) + 60
    total_height = DISK_TOP_MARGIN + len(sequence) * DISK_STEP_Y + 30
    canvas.config(scrollregion=(0, 0, total_width, total_height))

    # ---- Axis line ----
    x_start = track_to_x(unique_tracks[0]) - 20
    x_end = track_to_x(unique_tracks[-1]) + 20
    canvas.create_line(x_start, DISK_TOP_MARGIN,
                       x_end, DISK_TOP_MARGIN, fill="black")

    # ---- Axis ticks and labels (only at unique tracks) ----
    for t in unique_tracks:
        x = track_to_x(t)
        canvas.create_line(x, DISK_TOP_MARGIN - 5, x, DISK_TOP_MARGIN, fill="black")
        canvas.create_text(x, DISK_TOP_MARGIN - 10, text=str(t),
                           font=DISK_AXIS_FONT, anchor="s")

    # ---- Head movement path ----
    points = []
    for i, track in enumerate(sequence):
        x = track_to_x(track)
        y = DISK_TOP_MARGIN + i * DISK_STEP_Y + DISK_STEP_Y // 2
        points.append((x, y))

    if len(points) >= 2:
        for i in range(len(points) - 1):
            x1, y1 = points[i]
            x2, y2 = points[i+1]
            canvas.create_line(x1, y1, x2, y2, fill="black", width=2)

    r = DISK_POINT_RADIUS
    for x, y in points:
        canvas.create_oval(x - r, y - r, x + r, y + r,
                           fill="black", outline="black")

    # ---- Finalize scroll region ----
    canvas.update_idletasks()
    bbox = canvas.bbox("all")
    if bbox:
        canvas.config(scrollregion=bbox)