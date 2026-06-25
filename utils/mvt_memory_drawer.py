import tkinter as tk
from dataclasses import dataclass

# Constants
MVT_MIN_BLOCK_HEIGHT = 20
MVT_SNAPSHOT_WIDTH = 120
MVT_ARROW_WIDTH = 50
MVT_LEFT_MARGIN = 30
MVT_RIGHT_PAD = 40

MVT_COLORS = {
    "OS": "#E0E0E0",
    None: "white",
}
MVT_JOB_COLORS = ["lightblue", "lightgreen", "lightcoral", "plum", "wheat", "cyan"]
MVT_FONT = ("Arial", 8)
MVT_TIME_FONT = ("Arial", 9, "bold")

@dataclass
class FreeBlock:
    base: int = 0
    size: int = 0
    occupied_by: str = None

def draw_mvt_timeline(canvas, events, max_memory: int):
    canvas.delete("all")
    if not events:
        return

    num_snapshots = len(events)
    scale = 0.5

    y_positions_list = []
    for event in events:
        blocks = list(event["blocks"])
        used = sum(b.size for b in blocks)
        free_top = max_memory - used
        if free_top > 0:
            highest_base = blocks[-1].base + blocks[-1].size if blocks else 0
            blocks.append(FreeBlock(highest_base, free_top, None))

        heights = [max(MVT_MIN_BLOCK_HEIGHT, b.size * scale) for b in blocks]
        max_total_height = sum(heights)
        top_margin = 30
        base_y = max_total_height + top_margin
        y_pos = []
        current_y = base_y
        for h in reversed(heights):
            y_pos.insert(0, (current_y - h, current_y))
            current_y -= h
        y_positions_list.append((y_pos, blocks, base_y))

    max_base_y = max(b for _, _, b in y_positions_list)
    total_width = num_snapshots * (MVT_SNAPSHOT_WIDTH + MVT_ARROW_WIDTH) + MVT_LEFT_MARGIN + MVT_RIGHT_PAD
    canvas.config(scrollregion=(0, 0, total_width, max_base_y + 20))

    for i, event in enumerate(events):
        x_base = MVT_LEFT_MARGIN + i * (MVT_SNAPSHOT_WIDTH + MVT_ARROW_WIDTH)
        y_positions, blocks, base_y = y_positions_list[i]

        # ---- T= label ----
        canvas.create_text(
            x_base + MVT_ARROW_WIDTH + MVT_SNAPSHOT_WIDTH // 2,
            5,
            text=f"T = {event['time']}",
            font=MVT_TIME_FONT,
            anchor="n"
        )

        # ---- Arrow area ----
        # Build a mapping from base address to (top, bottom) for easy lookup
        base_to_rect = {b.base: (top, bottom) for b, (top, bottom) in zip(blocks, y_positions)}

        for action in event["actions"]:
            job_name, act_type = action[0], action[1]
            if act_type == "load":
                # Load actions: find the block currently occupied by this job
                for block, (top, bottom) in zip(blocks, y_positions):
                    if block.occupied_by == job_name:
                        mid_y = (top + bottom) // 2
                        canvas.create_text(x_base + MVT_ARROW_WIDTH // 2, mid_y,
                                           text=f"{job_name} →", font=MVT_FONT)
                        break
            elif act_type == "unload":
                base = action[2]   # the base address passed from model
                if base is not None and base in base_to_rect:
                    top, bottom = base_to_rect[base]
                    mid_y = (top + bottom) // 2
                    canvas.create_text(x_base + MVT_ARROW_WIDTH // 2, mid_y,
                                       text=f"{job_name} ←", font=MVT_FONT)
            # We ignore "compaction" for now

        # ---- Memory blocks ----
        for j, (block, (top, bottom)) in enumerate(zip(blocks, y_positions)):
            x1 = x_base + MVT_ARROW_WIDTH
            x2 = x1 + MVT_SNAPSHOT_WIDTH
            occ = block.occupied_by
            if occ == "OS":
                fill = MVT_COLORS["OS"]
                label = "OS"
            elif occ is None:
                fill = MVT_COLORS[None]
                label = ""
            else:
                idx = hash(occ) % len(MVT_JOB_COLORS)
                fill = MVT_JOB_COLORS[idx]
                label = occ
            canvas.create_rectangle(x1, top, x2, bottom, fill=fill, outline="black")
            if label:
                canvas.create_text((x1 + x2) // 2, (top + bottom) // 2,
                                   text=label, font=MVT_FONT)

        # ---- Partition boundaries and address labels ----
        x_line_left = x_base + MVT_ARROW_WIDTH
        x_line_right = x_line_left + MVT_SNAPSHOT_WIDTH
        for j, (block, (top, bottom)) in enumerate(zip(blocks, y_positions)):
            canvas.create_line(x_line_left, top, x_line_right, top, fill="black")
            addr = block.base + block.size
            canvas.create_text(x_base + MVT_ARROW_WIDTH - 5, top, text=str(addr),
                               anchor="e", font=MVT_FONT)
        bottom_y = y_positions[0][1]
        canvas.create_line(x_line_left, bottom_y, x_line_right, bottom_y, fill="black")
        canvas.create_text(x_base + MVT_ARROW_WIDTH - 5, bottom_y, text="0",
                           anchor="e", font=MVT_FONT)