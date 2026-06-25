import tkinter as tk
from tkinter import ttk, messagebox
from utils.gantt_drawer import draw_gantt_chart
from utils.process_row import ProcessRow

class CPUSchedulingTab(ttk.Frame):
    def __init__(self, parent, extra_fields=None, global_controls=None):
        super().__init__(parent)
        self.rows: list[ProcessRow] = []
        self.extra_fields = extra_fields if extra_fields is not None else []
        self.global_controls = global_controls if global_controls is not None else []
        self.global_widgets = {}
        self.create_widgets()

    def create_widgets(self):
        # ============================================================
        # MAIN LAYOUT: two equal rows (grid, no collapsing)
        # ============================================================
        self.grid_rowconfigure(0, weight=1)   # top half
        self.grid_rowconfigure(1, weight=1)   # bottom half
        self.grid_columnconfigure(0, weight=1)

        # ---- Top frame (processes + results) ----
        top_frame = ttk.Frame(self)
        top_frame.grid(row=0, column=0, sticky="nsew")
        top_frame.grid_propagate(False)

        # ---- Bottom frame (Gantt chart) ----
        bottom_frame = ttk.Frame(self)
        bottom_frame.grid(row=1, column=0, sticky="nsew")
        bottom_frame.grid_propagate(False)

        # ============================================================
        # TOP FRAME: left (processes) and right (results)
        # ============================================================
        top_frame.grid_columnconfigure(0, weight=2)   # left
        top_frame.grid_columnconfigure(1, weight=1)   # right
        top_frame.grid_rowconfigure(0, weight=1)

        # ----- LEFT: Process list (centred vertically, with global controls on the right) -----
        left_frame = ttk.LabelFrame(top_frame, text="Processes", padding=10)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0,2))
        left_frame.grid_rowconfigure(0, weight=1)   # top spacer
        left_frame.grid_rowconfigure(1, weight=0)   # content row
        left_frame.grid_rowconfigure(2, weight=1)   # bottom spacer
        left_frame.grid_columnconfigure(0, weight=1)

                # Container for header + scrollable rows + scrollbar + optional global controls
        outer_content = ttk.Frame(left_frame)
        outer_content.grid(row=1, column=0, sticky="ew")
        outer_content.grid_columnconfigure(0, weight=1)   # canvas column
        # scrollbar column – always present
        outer_content.grid_columnconfigure(1, weight=0)
        if self.global_controls:
            outer_content.grid_columnconfigure(2, weight=0)   # global controls column

        # Column headers (only over the canvas column, column 0)
        header_frame = ttk.Frame(outer_content)
        header_frame.grid(row=0, column=0, columnspan=1, sticky="ew", pady=(0,5))
        base_cols = ["Process", "Arrival Time", "Burst Time"]
        total_cols = len(base_cols) + len(self.extra_fields)
        for i in range(total_cols):
            header_frame.grid_columnconfigure(i, weight=1, uniform="jobcols")
        for i, text in enumerate(base_cols):
            ttk.Label(header_frame, text=text, anchor="center").grid(
                row=0, column=i, sticky="ew", padx=1)
        for i, (label, key, width, default, validator) in enumerate(self.extra_fields):
            ttk.Label(header_frame, text=label, anchor="center").grid(
                row=0, column=len(base_cols)+i, sticky="ew", padx=1)

        # Canvas (column 0) + Scrollbar (column 1)
        self.row_canvas = tk.Canvas(outer_content, borderwidth=0,
                                    highlightthickness=0, height=120)
        self.row_canvas.grid(row=1, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(outer_content, orient="vertical",
                                  command=self.row_canvas.yview)
        scrollbar.grid(row=1, column=1, sticky="ns")
        self.row_frame = ttk.Frame(self.row_canvas)
        self.row_frame.bind("<Configure>",
                            lambda e: self.row_canvas.configure(
                                scrollregion=self.row_canvas.bbox("all")))
        self.row_canvas.create_window((0, 0), window=self.row_frame,
                                      anchor="nw", tags="row_window")
        self.row_canvas.bind("<Configure>", self._on_canvas_configure)
        self.row_canvas.configure(yscrollcommand=scrollbar.set)

        # Global controls (e.g., Time Quantum) – placed in column 2
        if self.global_controls:
            ctrl_frame = ttk.Frame(outer_content)
            ctrl_frame.grid(row=1, column=2, sticky="n", padx=(10,0), pady=0)
            for ctrl in self.global_controls:
                lbl = ttk.Label(ctrl_frame, text=ctrl["label"], justify="center")
                lbl.pack(anchor="center", pady=(0,2))
                if ctrl["type"] == "spinbox":
                    var = tk.IntVar(value=ctrl.get("default", 1))
                    spin = ttk.Spinbox(ctrl_frame,
                                       from_=ctrl.get("from",1),
                                       to=ctrl.get("to",100),
                                       textvariable=var, width=5,
                                       justify="center")
                    spin.pack(anchor="center")
                else:
                    var = tk.StringVar(value=str(ctrl.get("default", "")))
                    entry = ttk.Entry(ctrl_frame, textvariable=var,
                                      width=5, justify="center")
                    entry.pack(anchor="center", fill="x")
                self.global_widgets[ctrl["key"]] = var

        # First empty row
        self.add_row()

        # ----- RIGHT: Results (centred vertically, unchanged) -----
        right_frame = ttk.LabelFrame(top_frame, text="Results", padding=10)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(2,0))
        right_frame.grid_rowconfigure(0, weight=1)   # top spacer
        right_frame.grid_rowconfigure(1, weight=0)   # content
        right_frame.grid_rowconfigure(2, weight=1)   # bottom spacer
        right_frame.grid_columnconfigure(0, weight=1)

        results_container = ttk.Frame(right_frame)
        results_container.grid(row=1, column=0)
        med_font = ("Arial", 10)
        self.avg_tat_label = ttk.Label(results_container, text="Avg Turnaround: ---", font=med_font)
        self.avg_tat_label.pack(anchor="w", pady=2)
        self.avg_wt_label = ttk.Label(results_container, text="Avg Waiting: ---", font=med_font)
        self.avg_wt_label.pack(anchor="w", pady=2)
        self.avg_rt_label = ttk.Label(results_container, text="Avg Response: ---", font=med_font)
        self.avg_rt_label.pack(anchor="w", pady=2)
        self.cpu_util_label = ttk.Label(results_container, text="CPU Utilization: ---", font=med_font)
        self.cpu_util_label.pack(anchor="w", pady=2)
        self.throughput_label = ttk.Label(results_container, text="Throughput: ---", font=med_font)
        self.throughput_label.pack(anchor="w", pady=2)

        # ============================================================
        # BOTTOM FRAME: Gantt chart (fills entire half, chart centred)
        # ============================================================
        bottom_frame.grid_rowconfigure(0, weight=1)
        bottom_frame.grid_columnconfigure(0, weight=1)

        gantt_frame = ttk.LabelFrame(bottom_frame, text="Gantt Chart", padding=5)
        gantt_frame.grid(row=0, column=0, sticky="nsew")
        gantt_frame.grid_rowconfigure(1, weight=1)
        gantt_frame.grid_columnconfigure(0, weight=1)

        self.generate_btn = ttk.Button(gantt_frame, text="Generate Gantt Chart")
        self.generate_btn.grid(row=0, column=0, sticky="w", pady=(0,5))

        self.canvas = tk.Canvas(gantt_frame, bg="white")
        self.canvas.grid(row=1, column=0, sticky="nsew")
        self.h_scrollbar = ttk.Scrollbar(gantt_frame, orient="horizontal", command=self.canvas.xview)
        self.h_scrollbar.grid(row=2, column=0, sticky="ew")
        self.canvas.configure(xscrollcommand=self.h_scrollbar.set)
        
    # ------------------------------------------------------------
    # Canvas width handler
    # ------------------------------------------------------------
    def _on_canvas_configure(self, event):
        canvas_width = event.width
        self.row_canvas.itemconfig("row_window", width=canvas_width)

    # ------------------------------------------------------------
    # Trailing buffer
    # ------------------------------------------------------------
    def add_row(self, extra_fields=None):
        if extra_fields is None:
            extra_fields = self.extra_fields
        row = ProcessRow(self.row_frame, self, extra_fields)
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

    # ------------------------------------------------------------
    # Controller interface
    # ------------------------------------------------------------
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
        self.canvas.update_idletasks()
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
        var = self.global_widgets.get(key)
        if var is None:
            return None
        return var.get()