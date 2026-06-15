# views/cpu_scheduling/cpu_scheduling_tab.py (updated)
import tkinter as tk
from tkinter import ttk, messagebox
from utils.gantt_drawer import draw_gantt_chart
from utils.process_row import ProcessRow, ExtraFieldDef

class CPUSchedulingTab(ttk.Frame):
    def __init__(self, parent, extra_fields=None, global_controls=None):
        super().__init__(parent)
        self.rows: list[ProcessRow] = []
        self.extra_fields = extra_fields if extra_fields is not None else []
        self.global_controls = global_controls if global_controls is not None else []
        self.global_widgets = {}
        self.create_widgets()

    def create_widgets(self):
        top_container = ttk.Frame(self)
        top_container.pack(fill="x", padx=5, pady=5)
        top_container.grid_columnconfigure(0, weight=2)
        top_container.grid_columnconfigure(1, weight=1)

        # ===== LEFT: Process List =====
        left_frame = ttk.LabelFrame(top_container, text="Processes", padding=10)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0,2))
        left_frame.grid_columnconfigure(0, weight=1)          # canvas
        left_frame.grid_columnconfigure(1, weight=0)          # scrollbar
        if self.global_controls:
            left_frame.grid_columnconfigure(2, weight=0)      # global controls column

        # Column headers – span ONLY the canvas column (0) so they match the process entries
        header_frame = ttk.Frame(left_frame)
        header_frame.grid(row=0, column=0, columnspan=1, sticky="ew", pady=(0,5))

        base_cols = ["Process", "Arrival Time", "Burst Time"]
        total_cols = len(base_cols) + len(self.extra_fields)
        for i in range(total_cols):
            header_frame.grid_columnconfigure(i, weight=1, uniform="headcols")
        for i, text in enumerate(base_cols):
            ttk.Label(header_frame, text=text, anchor="center").grid(row=0, column=i, sticky="ew")
        for i, (label, key, width, default, validator) in enumerate(self.extra_fields):
            ttk.Label(header_frame, text=label, anchor="center").grid(row=0, column=len(base_cols)+i, sticky="ew")

        # Row index for canvas, scrollbar, and optional controls
        row_idx = 1
        left_frame.grid_rowconfigure(row_idx, weight=1)

        # Canvas and scrollbar
        self.row_canvas = tk.Canvas(left_frame, borderwidth=0, highlightthickness=0, height=130)
        self.row_canvas.grid(row=row_idx, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=self.row_canvas.yview)
        scrollbar.grid(row=row_idx, column=1, sticky="ns")
        self.row_frame = ttk.Frame(self.row_canvas)
        self.row_frame.bind("<Configure>",
                            lambda e: self.row_canvas.configure(scrollregion=self.row_canvas.bbox("all")))
        self.row_canvas.create_window((0, 0), window=self.row_frame, anchor="nw", tags="row_window")
        self.row_canvas.bind("<Configure>", self._on_canvas_configure)
        self.row_canvas.configure(yscrollcommand=scrollbar.set)

        # Global controls (e.g. Time Quantum) → to the right of the scrollbar, top‑aligned
        if self.global_controls:
            ctrl_frame = ttk.Frame(left_frame)
            ctrl_frame.grid(row=row_idx, column=2, sticky="n", padx=(10,0), pady=5)
            for ctrl in self.global_controls:
                lbl = ttk.Label(ctrl_frame, text=ctrl["label"] + ":")
                lbl.pack(anchor="w", pady=(0,2))
                if ctrl["type"] == "spinbox":
                    var = tk.IntVar(value=ctrl.get("default", 1))
                    spin = ttk.Spinbox(ctrl_frame, from_=ctrl.get("from",1), to=ctrl.get("to",100),
                                    textvariable=var, width=5, justify="center")
                    spin.pack(anchor="w")
                else:
                    var = tk.StringVar(value=str(ctrl.get("default", "")))
                    entry = ttk.Entry(ctrl_frame, textvariable=var, width=5, justify="center")
                    entry.pack(anchor="w")
                self.global_widgets[ctrl["key"]] = var

        # First empty row
        self.add_row()

        # ===== RIGHT: Results (unchanged) =====
        # ...

        # --- Bottom: Gantt chart (unchanged) ---
        # ...

        # ===== RIGHT: Results (unchanged) =====
        right_frame = ttk.LabelFrame(top_container, text="Results", padding=10)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(2,0))
        med_font = ("Arial", 10)
        self.avg_tat_label = ttk.Label(right_frame, text="Avg Turnaround: ---", font=med_font)
        self.avg_tat_label.pack(anchor="w", pady=2)
        self.avg_wt_label = ttk.Label(right_frame, text="Avg Waiting: ---", font=med_font)
        self.avg_wt_label.pack(anchor="w", pady=2)
        self.avg_rt_label = ttk.Label(right_frame, text="Avg Response: ---", font=med_font)
        self.avg_rt_label.pack(anchor="w", pady=2)
        self.cpu_util_label = ttk.Label(right_frame, text="CPU Utilization: ---", font=med_font)
        self.cpu_util_label.pack(anchor="w", pady=2)
        self.throughput_label = ttk.Label(right_frame, text="Throughput: ---", font=med_font)
        self.throughput_label.pack(anchor="w", pady=2)

        # --- Bottom: Gantt chart (unchanged) ---
        gantt_frame = ttk.LabelFrame(self, text="Gantt Chart", padding=5)
        gantt_frame.pack(fill="both", expand=True, padx=5, pady=(0,5))
        self.generate_btn = ttk.Button(gantt_frame, text="Generate Gantt Chart")
        self.generate_btn.pack(anchor="w", pady=(0,5))
        self.canvas = tk.Canvas(gantt_frame, bg="white", height=200)
        self.canvas.pack(fill="x", expand=False)
        self.h_scrollbar = ttk.Scrollbar(gantt_frame, orient="horizontal", command=self.canvas.xview)
        self.h_scrollbar.pack(fill="x")
        self.canvas.configure(xscrollcommand=self.h_scrollbar.set)

    def _on_canvas_configure(self, event):
        canvas_width = event.width
        self.row_canvas.itemconfig("row_window", width=canvas_width)

    def add_row(self):
        row = ProcessRow(self.row_frame, self, extra_fields=self.extra_fields)
        self.rows.append(row)

    def on_row_change(self):
        empty_rows = [r for r in self.rows if r.is_empty()]
        if len(empty_rows) == 0:
            self.add_row()
        elif len(empty_rows) > 1:
            keep = empty_rows[0]
            for row in empty_rows[1:]:
                row.destroy()
                self.rows.remove(row)

    # ---------- Controller methods ----------
    def set_generate_command(self, command):
        self.generate_btn.config(command=command)

    def get_all_jobs(self):
        job_dicts = []
        for row in self.rows:
            base = row.get_base_job_dict()
            if base is not None:
                extra = row.get_extra_values()
                job_dicts.append({
                    "name": base["name"],
                    "arrival": base["arrival"],
                    "burst": base["burst"],
                    "extra": extra
                })
        return job_dicts

    def display_gantt(self, events):
        canvas_height = self.canvas.winfo_height()
        if canvas_height < 50:
            canvas_height = None
        draw_gantt_chart(self.canvas, events, canvas_height)

    def display_results(self, avg_tat, avg_wt, avg_rt, cpu_util, throughput):
        self.avg_tat_label.config(text=f"Avg Turnaround: {avg_tat:.2f}")
        self.avg_wt_label.config(text=f"Avg Waiting: {avg_wt:.2f}")
        self.avg_rt_label.config(text=f"Avg Response: {avg_rt:.2f}")
        self.cpu_util_label.config(text=f"CPU Utilization: {cpu_util:.1f}%")
        self.throughput_label.config(text=f"Throughput: {throughput:.3f} jobs/unit time")

    def show_error(self, message):
        messagebox.showerror("Error", message)

    def show_info(self, title, message):
        messagebox.showinfo(title, message)
        
    def get_global_value(self, key):
        """Return the value of a global control (as int or string)."""
        var = self.global_widgets.get(key)
        if var is None:
            return None
        return var.get()