import tkinter as tk
from tkinter import ttk, messagebox
from utils.page_replacement_drawer import draw_page_frames

class ReferenceStringRow:
    """Horizontal trailing buffer of page‑number entries."""
    def __init__(self, parent, app):
        self.app = app
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill="x")

        self.entries = []
        self.vars = []

        self.add_entry()

    def add_entry(self):
        var = tk.StringVar()
        entry = ttk.Entry(self.frame, textvariable=var, width=3,
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

    def get_reference_string(self):
        refs = []
        for i, var in enumerate(self.vars[:-1]):
            val = var.get().strip()
            if val:
                try:
                    refs.append(int(val))
                except ValueError:
                    return None
        return refs

    def destroy(self):
        self.frame.destroy()


class PageReplacementTab(ttk.Frame):
    def __init__(self, parent, algorithm_name, extra_controls=None):
        super().__init__(parent)
        self.algorithm_name = algorithm_name
        self.extra_controls = extra_controls if extra_controls is not None else []
        self.extra_widgets = {}
        self.ref_row = None
        self.create_widgets()

    def create_widgets(self):
        # ----- Top: Reference string input -----
        top_frame = ttk.LabelFrame(self, text="Reference String", padding=10)
        top_frame.pack(fill="x", padx=5, pady=5)
        self.ref_row = ReferenceStringRow(top_frame, self)

        # ----- Bottom: two columns (settings + simulation) -----
        bottom_panel = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        bottom_panel.pack(fill="both", expand=True, padx=5, pady=5)

        # --- Left: Settings (centred) ---
        settings_frame = ttk.LabelFrame(bottom_panel, text="Settings", padding=10)
        bottom_panel.add(settings_frame, weight=0)

        ttk.Label(settings_frame, text="Number of Frames:").pack(anchor="center", pady=(0, 5))
        self.frames_var = tk.StringVar(value="3")
        ttk.Entry(settings_frame, textvariable=self.frames_var, width=5,
                  justify="center").pack(anchor="center", pady=(0, 10))

        # Extra controls (e.g., policy dropdown for Counting-Based)
        for ctrl in self.extra_controls:
            lbl = ttk.Label(settings_frame, text=ctrl["label"] + ":")
            lbl.pack(anchor="center", pady=(0, 2))
            if ctrl["type"] == "combobox":
                var = tk.StringVar(value=ctrl.get("default", ctrl["values"][0]))
                combo = ttk.Combobox(settings_frame, textvariable=var,
                                     values=ctrl["values"], state="readonly", width=10,
                                     justify="center")
                combo.pack(anchor="center", pady=(0, 10))
            else:
                var = tk.StringVar()
                entry = ttk.Entry(settings_frame, textvariable=var, width=10,
                                  justify="center")
                entry.pack(anchor="center", pady=(0, 10))
            self.extra_widgets[ctrl["key"]] = var

        self.run_btn = ttk.Button(settings_frame, text="Run Simulation",
                                  command=self.run_simulation)
        self.run_btn.pack(anchor="center", pady=(0, 10))

        self.page_faults_label = ttk.Label(settings_frame, text="Page Faults: ---",
                                           font=("Arial", 10))
        self.page_faults_label.pack(anchor="center")

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
        refs = self.ref_row.get_reference_string()
        if refs is None:
            messagebox.showerror("Error", "Invalid reference string. Only integers allowed.")
            return
        try:
            num_frames = int(self.frames_var.get().strip())
            if num_frames < 1:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Number of frames must be a positive integer.")
            return

        if not hasattr(self, '_simulate_func'):
            messagebox.showerror("Error", "No simulation function set.")
            return
        result = self._simulate_func(refs, num_frames)
        if isinstance(result, tuple) and len(result) == 2:
            states, counters = result
        else:
            states = result
            counters = None

        faults = self._count_faults(refs, states)
        self.page_faults_label.config(text=f"Page Faults: {faults}")
        draw_page_frames(self.canvas, refs, states, num_frames, counters)

    def _count_faults(self, refs, states):
        faults = 0
        for i in range(len(refs)):
            if i == 0 or refs[i] not in states[i-1]:
                faults += 1
        return faults

    def set_simulate_function(self, func):
        self._simulate_func = func