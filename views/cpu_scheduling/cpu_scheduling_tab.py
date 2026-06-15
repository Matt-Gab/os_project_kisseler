import tkinter as tk
from tkinter import ttk, messagebox
from utils.gantt_drawer import draw_gantt_chart
from utils.process_row import ProcessRow

class CPUSchedulingTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.rows: list[ProcessRow] = []
        self.create_widgets()

    def create_widgets(self):
        top_container = ttk.Frame(self)
        top_container.pack(fill="x", padx=5, pady=5)
        top_container.grid_columnconfigure(0, weight=2)
        top_container.grid_columnconfigure(1, weight=1)

        # ===== LEFT: Process List =====
        left_frame = ttk.LabelFrame(top_container, text="Processes", padding=10)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0,2))
        left_frame.grid_rowconfigure(1, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)

        header_frame = ttk.Frame(left_frame)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0,5))
        for i in range(3):
            header_frame.grid_columnconfigure(i, weight=1, uniform="headcols")
        ttk.Label(header_frame, text="Process", anchor="center").grid(row=0, column=0, sticky="ew")
        ttk.Label(header_frame, text="Arrival Time", anchor="center").grid(row=0, column=1, sticky="ew")
        ttk.Label(header_frame, text="Burst Time", anchor="center").grid(row=0, column=2, sticky="ew")

        self.row_canvas = tk.Canvas(left_frame, borderwidth=0, highlightthickness=0, height=120)
        self.row_canvas.grid(row=1, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=self.row_canvas.yview)
        scrollbar.grid(row=1, column=1, sticky="ns")
        self.row_frame = ttk.Frame(self.row_canvas)
        self.row_frame.bind("<Configure>",
                            lambda e: self.row_canvas.configure(scrollregion=self.row_canvas.bbox("all")))
        self.row_canvas.create_window((0, 0), window=self.row_frame, anchor="nw", tags="row_window")
        self.row_canvas.bind("<Configure>", self._on_canvas_configure)
        self.row_canvas.configure(yscrollcommand=scrollbar.set)
        self.add_row()

        # ===== RIGHT: Results =====
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

        # --- Bottom: Gantt chart (fills remaining space) ---
        gantt_frame = ttk.LabelFrame(self, text="Gantt Chart", padding=5)
        # Pack AFTER top_container so it takes the rest of the window
        gantt_frame.pack(fill="both", expand=True, padx=5, pady=(0,5))

        self.generate_btn = ttk.Button(gantt_frame, text="Generate Gantt Chart")
        self.generate_btn.pack(anchor="w", pady=(0,5))

        # Canvas fills the whole gantt_frame, scrollbar at bottom
        self.canvas = tk.Canvas(gantt_frame, bg="white")
        self.canvas.pack(fill="both", expand=True)
        self.h_scrollbar = ttk.Scrollbar(gantt_frame, orient="horizontal", command=self.canvas.xview)
        self.h_scrollbar.pack(fill="x")
        self.canvas.configure(xscrollcommand=self.h_scrollbar.set)

    def _on_canvas_configure(self, event):
        """Resize the inner row frame to match canvas width."""
        canvas_width = event.width
        self.row_canvas.itemconfig("row_window", width=canvas_width)

    # --- Row management (same as before) ---
    def add_row(self, extra_fields=None):
        if extra_fields is None:
            extra_fields = []
        row = ProcessRow(self.row_frame, self, extra_fields)
        self.rows.append(row)

    def on_row_change(self):
        # Trigger new row only when the LAST empty row becomes VALID
        empty_rows = [r for r in self.rows if r.is_empty()]
        if len(empty_rows) == 0:
            self.add_row()
        elif len(empty_rows) > 1:
            keep = empty_rows[0]
            for row in empty_rows[1:]:
                row.destroy()
                self.rows.remove(row)

    # If you want spawn on valid, add this extra check:
    # last_row = self.rows[-1] if self.rows else None
    # if last_row and last_row.is_valid():
    #    self.add_row()

    # --- Methods for controller ---
    def set_generate_command(self, command):
        self.generate_btn.config(command=command)

    def get_all_jobs(self):
        """Return a list of dictionaries with job data (no model dependency)."""
        job_dicts = []
        for row in self.rows:
            base = row.get_base_job_dict()      # dict with name, arrival, burst
            if base is not None:
                extra = row.get_extra_values()
                job_dicts.append({
                    "name": base["name"],
                    "arrival": base["arrival"],
                    "burst": base["burst"],
                    "extra": extra
                })
        return job_dicts

    def add_job_to_tree(self, job):
        """Add a job object (must have .name, .arrival, .burst) to the display."""
        self.tree.insert("", "end", values=(job.name, job.arrival, job.burst))

    def clear_entries(self):
        self.name_entry.delete(0, "end")
        self.arrival_entry.delete(0, "end")
        self.burst_entry.delete(0, "end")

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