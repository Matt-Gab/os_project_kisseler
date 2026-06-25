import tkinter as tk
from tkinter import ttk, messagebox
from utils.disk_drawer import draw_disk_movement

class TrackRequestRow:
    """Horizontal trailing buffer of track‑request entries."""
    def __init__(self, parent, app):
        self.app = app
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill="x")

        self.entries = []
        self.vars = []

        self.add_entry()

    def add_entry(self):
        var = tk.StringVar()
        entry = ttk.Entry(self.frame, textvariable=var, width=4,
                          justify="center", font=("Arial", 10))
        if self.entries:
            comma_label = ttk.Label(self.frame, text=",", font=("Arial", 10))
            comma_label.pack(side="left")
            self.entries.append(comma_label)
        entry.pack(side="left", padx=2)
        self.entries.append(entry)
        self.vars.append(var)
        var.trace_add("write", self._on_change)

    def _on_change(self, *args):
        if self.vars[-1].get().strip() != "":
            self.add_entry()
        self.clean_empty_entries()

    def clean_empty_entries(self):
        while len(self.vars) >= 2 and self.vars[-1].get().strip() == "" and self.vars[-2].get().strip() == "":
            if len(self.entries) >= 2:
                self.entries.pop().destroy()
                if self.entries and isinstance(self.entries[-1], ttk.Label):
                    self.entries.pop().destroy()
            self.vars.pop()

    def get_requests(self):
        reqs = []
        for i, var in enumerate(self.vars[:-1]):
            val = var.get().strip()
            if val:
                try:
                    reqs.append(int(val))
                except ValueError:
                    return None
        return reqs

    def destroy(self):
        self.frame.destroy()


class DiskSchedulingTab(ttk.Frame):
    def __init__(self, parent, algorithm_name, extra_controls=None):
        super().__init__(parent)
        self.algorithm_name = algorithm_name
        self.extra_controls = extra_controls if extra_controls is not None else []
        self.extra_widgets = {}
        self.req_row = None
        self.create_widgets()

    def create_widgets(self):
        # ----- Top: Track requests input -----
        top_frame = ttk.LabelFrame(self, text="Track Requests", padding=10)
        top_frame.pack(fill="x", padx=5, pady=5)
        self.req_row = TrackRequestRow(top_frame, self)

        # ----- Bottom: two columns (settings + simulation) -----
        bottom_panel = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        bottom_panel.pack(fill="both", expand=True, padx=5, pady=5)

        # --- Left: Settings ---
        settings_frame = ttk.LabelFrame(bottom_panel, text="Settings", padding=10)
        bottom_panel.add(settings_frame, weight=0)

        ttk.Label(settings_frame, text="Starting Track:").pack(anchor="center", pady=(0, 5))
        self.start_var = tk.StringVar(value="53")
        ttk.Entry(settings_frame, textvariable=self.start_var, width=8,
                  justify="center").pack(anchor="center", pady=(0, 10))

        ttk.Label(settings_frame, text="Max Tracks:").pack(anchor="center", pady=(0, 5))
        self.max_var = tk.StringVar(value="199")
        ttk.Entry(settings_frame, textvariable=self.max_var, width=8,
                  justify="center").pack(anchor="center", pady=(0, 10))

        # Extra controls (e.g., direction for SCAN/C-SCAN/LOOK)
        for ctrl in self.extra_controls:
            lbl = ttk.Label(settings_frame, text=ctrl["label"] + ":")
            lbl.pack(anchor="center", pady=(0, 2))
            if ctrl["type"] == "combobox":
                var = tk.StringVar(value=ctrl.get("default", ctrl["values"][0]))
                combo = ttk.Combobox(settings_frame, textvariable=var,
                                     values=ctrl["values"], state="readonly", width=10,
                                     justify="center")
                combo.pack(anchor="center", pady=(0, 10))
            self.extra_widgets[ctrl["key"]] = var

        self.run_btn = ttk.Button(settings_frame, text="Run Simulation",
                                  command=self.run_simulation)
        self.run_btn.pack(anchor="center", pady=(0, 10))

        self.head_movement_label = ttk.Label(settings_frame,
                                             text="Total Head Movement: ---",
                                             font=("Arial", 10))
        self.head_movement_label.pack(anchor="center")

        # --- Right: Simulation canvas ---
        sim_frame = ttk.LabelFrame(bottom_panel, text="Simulation", padding=5)
        bottom_panel.add(sim_frame, weight=1)

        sim_frame.grid_rowconfigure(0, weight=1)
        sim_frame.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(sim_frame, bg="white")
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.v_scroll = ttk.Scrollbar(sim_frame, orient="vertical",
                                      command=self.canvas.yview)
        self.v_scroll.grid(row=0, column=1, sticky="ns")

        self.h_scroll = ttk.Scrollbar(sim_frame, orient="horizontal",
                                      command=self.canvas.xview)
        self.h_scroll.grid(row=1, column=0, sticky="ew")

        self.canvas.configure(xscrollcommand=self.h_scroll.set,
                              yscrollcommand=self.v_scroll.set)

    def get_extra_value(self, key):
        var = self.extra_widgets.get(key)
        if var is None:
            return None
        return var.get()

    def run_simulation(self):
        reqs = self.req_row.get_requests()
        if reqs is None:
            messagebox.showerror("Error", "Invalid track requests. Only integers allowed.")
            return
        if not reqs:
            messagebox.showerror("Error", "Please enter at least one track request.")
            return
        try:
            start = int(self.start_var.get().strip())
            max_track = int(self.max_var.get().strip())
            if start < 0 or max_track < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Invalid start track or max tracks.")
            return

        if not hasattr(self, '_simulate_func'):
            messagebox.showerror("Error", "No simulation function set.")
            return

        # Collect extra kwargs (e.g., direction)
        extra_kwargs = {}
        for key, var in self.extra_widgets.items():
            extra_kwargs[key] = var.get()

        result = self._simulate_func(reqs, start, max_track, **extra_kwargs)
        sequence, total_movement = result
        self.head_movement_label.config(text=f"Total Head Movement: {total_movement}")

        # Draw on canvas
        draw_disk_movement(self.canvas, sequence, max_track)

    def set_simulate_function(self, func):
        self._simulate_func = func