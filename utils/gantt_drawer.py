# utils/gantt_drawer.py
import tkinter as tk
from .constants import *

def draw_gantt_chart(canvas: tk.Canvas, events: list, canvas_height: int = None):
    """
    events: list of (start_time, end_time, job) where job can be None (idle).
    Merges consecutive events with the same job, draws fixed‑size squares,
    and automatically sets the scrollregion based on actual content.
    """
    canvas.delete("all")
    if not events:
        return

    # ---- Merge consecutive events with the same job ----
    merged = []
    for start, end, job in events:
        if merged and merged[-1][2] is job and merged[-1][1] == start:
            merged[-1] = (merged[-1][0], end, job)
        else:
            merged.append((start, end, job))

    events = sorted(merged, key=lambda e: e[0])

    boundary_times = [events[0][0]]
    for _, end, _ in events:
        boundary_times.append(end)

    # ---- Calculate vertical centering ----
    axis_gap = 5
    tick_height = 5
    label_height = 15
    total_chart_height = JOB_HEIGHT + axis_gap + tick_height + label_height
    if canvas_height and canvas_height > total_chart_height:
        top_margin = (canvas_height - total_chart_height) // 2
    else:
        top_margin = TOP_MARGIN

    y1 = top_margin
    y2 = y1 + JOB_HEIGHT

    # ---- Draw squares ----
    for i, (start, end, job) in enumerate(events):
        x1 = LEFT_OFFSET + i * SQUARE_SIZE
        x2 = x1 + SQUARE_SIZE

        if job is None:
            fill_color = IDLE_FILL_COLOR
            text_color = IDLE_TEXT_COLOR
            label = "Idle"
        else:
            fill_color = ""
            text_color = "black"
            label = job.name if len(job.name) <= 4 else job.name[:4] + "…"

        canvas.create_rectangle(x1, y1, x2, y2,
                                fill=fill_color, outline=JOB_OUTLINE_COLOR, width=1)
        canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2,
                           text=label, font=LABEL_FONT, fill=text_color)

    # ---- Time axis ----
    axis_y = y2 + axis_gap
    for i, t in enumerate(boundary_times):
        x = LEFT_OFFSET + i * SQUARE_SIZE
        canvas.create_line(x, axis_y, x, axis_y + tick_height, fill=AXIS_TICK_COLOR)
        canvas.create_text(x, axis_y + tick_height + 5, text=str(t),
                           font=LABEL_FONT, anchor="n")

    # ---- Set scroll region to exactly contain all drawn items ----
    canvas.update_idletasks()          # ensure canvas geometry is up to date
    bbox = canvas.bbox("all")
    if bbox:
        # Add a tiny right padding so the last time label isn't clipped
        x1, y1, x2, y2 = bbox
        canvas.config(scrollregion=(0, 0, x2 + 20, 0))
    else:
        canvas.config(scrollregion=(0, 0, 0, 0))

    # Optional: reset scroll position to start
    canvas.xview_moveto(0)