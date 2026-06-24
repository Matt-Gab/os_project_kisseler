import tkinter as tk
from utils.constants import *

def draw_memory_timeline(canvas, events, partition_sizes):
    canvas.delete("all")
    if not events or not partition_sizes:
        return

    num_partitions = len(partition_sizes)
    scaled_heights = []
    for size in partition_sizes:
        scaled_heights.append(max(MEM_MIN_PART_HEIGHT, size // 10))
    total_height = sum(scaled_heights)

    base_y = total_height + 20   # top margin
    y_positions = []
    current_y = base_y
    for h in scaled_heights:
        y_positions.append((current_y - h, current_y))
        current_y -= h

    num_snapshots = len(events)
    total_width = num_snapshots * (MEM_SNAPSHOT_WIDTH + MEM_ARROW_AREA_WIDTH) + MEM_LEFT_MARGIN

    # Draw each snapshot
    for i, event in enumerate(events):
        x_base = MEM_LEFT_MARGIN + i * (MEM_SNAPSHOT_WIDTH + MEM_ARROW_AREA_WIDTH)

        # ---- Arrow area ----
        for pidx in range(num_partitions):
            top_y, bottom_y = y_positions[pidx]
            mid_y = (top_y + bottom_y) // 2
            load_action = False
            unload_action = False
            load_job = unload_job = ""

            for (job_name, action_type, part_idx) in event["actions"]:
                if part_idx == pidx:
                    if action_type == "load":
                        load_action = True
                        load_job = job_name
                    elif action_type == "unload":
                        unload_action = True
                        unload_job = job_name

            if load_action and unload_action:
                text = f"{unload_job} ←\n{load_job} →"
                canvas.create_text(x_base + MEM_ARROW_AREA_WIDTH//2, mid_y,
                                   text=text, font=MEM_ARROW_FONT, justify="center")
            elif load_action:
                canvas.create_text(x_base + MEM_ARROW_AREA_WIDTH//2, mid_y,
                                   text=f"{load_job} →", font=MEM_ARROW_FONT)
            elif unload_action:
                canvas.create_text(x_base + MEM_ARROW_AREA_WIDTH//2, mid_y,
                                   text=f"{unload_job} ←", font=MEM_ARROW_FONT)

        # ---- Memory snapshot ----
        for pidx in range(num_partitions):
            top_y, bottom_y = y_positions[pidx]
            x1 = x_base + MEM_ARROW_AREA_WIDTH
            x2 = x1 + MEM_SNAPSHOT_WIDTH
            occ = event["partitions"][pidx].occupied_by
            if pidx == 0:
                fill = MEM_COLOR_OS
                label = "OS"
            elif occ is not None:
                fill = MEM_COLOR_JOB
                label = occ
            else:
                fill = MEM_COLOR_FREE
                label = ""
            canvas.create_rectangle(x1, top_y, x2, bottom_y,
                                    fill=fill, outline="black")
            if label:
                canvas.create_text((x1+x2)//2, (top_y+bottom_y)//2,
                                   text=label, font=MEM_LABEL_FONT)

        # ---- Partition boundary lines + address labels ----
        for pidx in range(num_partitions):
            top_y, bottom_y = y_positions[pidx]
            x1 = x_base + MEM_ARROW_AREA_WIDTH
            x2 = x1 + MEM_SNAPSHOT_WIDTH
            # line at top of partition
            canvas.create_line(x1, top_y, x2, top_y, fill="black")
            addr = sum(partition_sizes[:pidx+1])
            canvas.create_text(x_base + MEM_ARROW_AREA_WIDTH - 5, top_y,
                               text=str(addr), anchor="e", font=MEM_ARROW_FONT)

        # ---- Time label ----
        canvas.create_text(x_base + MEM_ARROW_AREA_WIDTH + MEM_SNAPSHOT_WIDTH//2,
                           y_positions[-1][0] - 20, text=f"T={event['time']}",
                           font=MEM_TIME_FONT, anchor="s")

        # ---- Hold queue ----
        if event["hold_queue"]:
            hold_text = "Hold: " + ", ".join(event["hold_queue"])
            canvas.create_text(x_base + MEM_ARROW_AREA_WIDTH//2,
                               y_positions[-1][0] - 20,
                               text=hold_text, font=MEM_ARROW_FONT, anchor="s")

    # ---- Set scroll region (both directions) ----
    canvas.update_idletasks()
    bbox = canvas.bbox("all")
    if bbox:
        x1, y1, x2, y2 = bbox
        canvas.config(scrollregion=(0, 0, x2 + 30, y2 + 20))
    else:
        canvas.config(scrollregion=(0, 0, 0, 0))
    canvas.xview_moveto(0)