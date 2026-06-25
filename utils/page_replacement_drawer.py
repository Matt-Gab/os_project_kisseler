import tkinter as tk

PR_BOX_SIZE = 30
PR_FONT = ("Arial", 9)
PR_TIME_FONT = ("Arial", 8, "bold")
PR_LEFT_MARGIN = 10
PR_TOP_MARGIN = 30
PR_COUNTER_FONT = ("Arial", 7)

def draw_page_frames(canvas, reference_string, states, num_frames, counters=None):
    """
    Draws a table: columns = reference steps, rows = frames.
    If counters is provided (list of dicts), draws counter line below the boxes.
    """
    canvas.delete("all")
    if not reference_string or not states:
        return

    num_steps = len(reference_string)
    extra_height = 0
    if counters:
        extra_height = 15   # space for one line of text

    total_width = PR_LEFT_MARGIN + num_steps * PR_BOX_SIZE + 50
    total_height = PR_TOP_MARGIN + num_frames * PR_BOX_SIZE + extra_height + 50
    canvas.config(scrollregion=(0, 0, total_width, total_height))

    for step, (page, state) in enumerate(zip(reference_string, states)):
        x = PR_LEFT_MARGIN + step * PR_BOX_SIZE

        # Reference page number at top
        canvas.create_text(x + PR_BOX_SIZE // 2, 5,
                           text=str(page), font=PR_TIME_FONT, anchor="n")

        # Frame contents
        for f in range(num_frames):
            y = PR_TOP_MARGIN + f * PR_BOX_SIZE
            fill = "white"
            text = ""
            if f < len(state) and state[f] is not None:
                fill = "lightblue"
                text = str(state[f])
            canvas.create_rectangle(x, y, x + PR_BOX_SIZE, y + PR_BOX_SIZE,
                                    fill=fill, outline="black")
            if text:
                canvas.create_text(x + PR_BOX_SIZE // 2, y + PR_BOX_SIZE // 2,
                                   text=text, font=PR_FONT)

        # Counter line (if available)
        if counters and step < len(counters):
            counter_dict = counters[step]
            # build a small string like "1:0 2:0 3:1"
            items = sorted(counter_dict.items())
            counter_text = " ".join(f"{k}:{v}" for k, v in items)
            y_counter = PR_TOP_MARGIN + num_frames * PR_BOX_SIZE + 5
            canvas.create_text(x + PR_BOX_SIZE // 2, y_counter,
                               text=counter_text, font=PR_COUNTER_FONT, anchor="n")

    canvas.update_idletasks()
    bbox = canvas.bbox("all")
    if bbox:
        canvas.config(scrollregion=bbox)