import tkinter as tk
from tkinter import ttk, messagebox
from utils.mvt_memory_drawer import draw_mvt_timeline
from models.memory_management.mvt_model import simulate_mvt

class MemoryJobRow:
    """Dynamic row for MVT job inputs. Columns: Name, Size, Burst, Priority (if shown)."""
    def __init__(self, parent, app, show_priority):
        self.app = app
        self.show_priority = show_priority
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill="x", pady=1)

        self.name_var = tk.StringVar()
        self.size_var = tk.StringVar()
        self.burst_var = tk.StringVar()
        self.priority_var = tk.StringVar()

        self.name_entry = ttk.Entry(self.frame, textvariable=self.name_var, justify="center")
        self.size_entry = ttk.Entry(self.frame, textvariable=self.size_var, justify="center")
        self.burst_entry = ttk.Entry(self.frame, textvariable=self.burst_var, justify="center")
        self.priority_entry = ttk.Entry(self.frame, textvariable=self.priority_var, justify="center")

        self._configure_columns()
        self._place_widgets()

        for var in (self.name_var, self.size_var, self.burst_var, self.priority_var):
            var.trace_add("write", self._on_change)

    def _configure_columns(self):
        for col in range(4):
            self.frame.grid_columnconfigure(col, weight=0)
        visible = [0, 1, 2]
        if self.show_priority:
            visible.append(3)
        for col in visible:
            self.frame.grid_columnconfigure(col, weight=1, uniform="mvt_jobcols")

    def _place_widgets(self):
        self.name_entry.grid(row=0, column=0, sticky="ew", padx=1, pady=1)
        self.size_entry.grid(row=0, column=1, sticky="ew", padx=1, pady=1)
        self.burst_entry.grid(row=0, column=2, sticky="ew", padx=1, pady=1)
        if self.show_priority:
            self.priority_entry.grid(row=0, column=3, sticky="ew", padx=1, pady=1)
        else:
            self.priority_entry.grid_remove()

    def _on_change(self, *args):
        self.app.on_job_row_change()

    def is_empty(self):
        return (self.name_var.get().strip() == "" and
                self.size_var.get().strip() == "" and
                self.burst_var.get().strip() == "" and
                (not self.show_priority or self.priority_var.get().strip() == ""))

    def is_valid(self):
        name = self.name_var.get().strip()
        if not name: return False
        try:
            size = int(self.size_var.get().strip())
            burst = int(self.burst_var.get().strip())
            return size > 0 and burst > 0
        except ValueError:
            return False

    def get_job(self):
        if not self.is_valid():
            return None
        priority = int(self.priority_var.get().strip() or "99")
        return {
            "name": self.name_var.get().strip(),
            "size": int(self.size_var.get().strip()),
            "burst": int(self.burst_var.get().strip()),
            "priority": priority
        }

    def destroy(self):
        self.frame.destroy()


class MVTTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.job_rows = []
        self.create_widgets()
        self.rebuild_job_area()

    def create_widgets(self):
        main_panel = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_panel.pack(fill="both", expand=True)

        left_frame = ttk.Frame(main_panel)
        right_frame = ttk.Frame(main_panel)
        main_panel.add(left_frame, weight=1)
        main_panel.add(right_frame, weight=2)

        left_frame.grid_columnconfigure(0, weight=2)   # Jobs
        left_frame.grid_columnconfigure(1, weight=1)   # Settings
        left_frame.grid_rowconfigure(0, weight=1)

        # ---- Jobs Column ----
        jobs_frame = ttk.LabelFrame(left_frame, text="Jobs", padding=5)
        jobs_frame.grid(row=0, column=0, sticky="nsew", padx=2)
        jobs_frame.grid_rowconfigure(0, weight=1)
        jobs_frame.grid_columnconfigure(0, weight=1)

        self.job_canvas = tk.Canvas(jobs_frame, borderwidth=0, highlightthickness=0, height=120)
        self.job_canvas.grid(row=0, column=0, sticky="nsew")
        job_scroll = ttk.Scrollbar(jobs_frame, orient="vertical", command=self.job_canvas.yview)
        job_scroll.grid(row=0, column=1, sticky="ns")

        self.job_row_frame = ttk.Frame(self.job_canvas)
        self.job_window_id = self.job_canvas.create_window((0, 0), window=self.job_row_frame, anchor="nw")
        self.job_row_frame.bind("<Configure>",
            lambda e: self.job_canvas.configure(scrollregion=self.job_canvas.bbox("all")))
        self.job_canvas.configure(yscrollcommand=job_scroll.set)
        self.job_canvas.bind("<Configure>", self._on_job_canvas_configure)

        # ---- Settings Column ----
        ctrl_frame = ttk.LabelFrame(left_frame, text="Settings", padding=5)
        ctrl_frame.grid(row=0, column=1, sticky="nsew", padx=2)

        ttk.Label(ctrl_frame, text="OS Size:").pack(anchor="w", pady=(0,2))
        self.os_size_var = tk.StringVar()
        ttk.Entry(ctrl_frame, textvariable=self.os_size_var, width=10, justify="center").pack(anchor="w", pady=(0,8))

        ttk.Label(ctrl_frame, text="Max Memory:").pack(anchor="w", pady=(0,2))
        self.max_mem_var = tk.StringVar()
        ttk.Entry(ctrl_frame, textvariable=self.max_mem_var, width=10, justify="center").pack(anchor="w", pady=(0,8))

        self.compaction_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(ctrl_frame, text="Compaction", variable=self.compaction_var).pack(anchor="w", pady=(0,8))

        ttk.Label(ctrl_frame, text="Scheduling:").pack(anchor="w", pady=(0,2))
        self.sched_var = tk.StringVar(value="FCFS")
        sched_combo = ttk.Combobox(ctrl_frame, textvariable=self.sched_var,
                                   values=["FCFS", "SJF", "HRRN", "Priority NP", "RR"], state="readonly", width=15)
        sched_combo.pack(anchor="w", pady=(0,8))
        sched_combo.bind("<<ComboboxSelected>>", self.on_settings_change)

        ttk.Label(ctrl_frame, text="Allocation Policy:").pack(anchor="w", pady=(0,2))
        self.alloc_var = tk.StringVar(value="first_fit")
        ttk.Combobox(ctrl_frame, textvariable=self.alloc_var,
                     values=["first_fit", "best_fit", "worst_fit"], state="readonly", width=15).pack(anchor="w", pady=(0,8))

        # Time Quantum (only for RR)
        self.quantum_frame = ttk.Frame(ctrl_frame)
        ttk.Label(self.quantum_frame, text="Time Quantum:").pack(anchor="w", pady=(10, 2))
        self.quantum_var = tk.StringVar(value="2")
        ttk.Entry(self.quantum_frame, textvariable=self.quantum_var, width=5,
                  justify="center").pack(anchor="w")

        self.run_btn = ttk.Button(ctrl_frame, text="Run Simulation", command=self.run_simulation)
        self.run_btn.pack(side="bottom", pady=10)

        # ---- Right side: Canvas ----
        canvas_frame = ttk.Frame(right_frame)
        canvas_frame.pack(fill="both", expand=True)
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(canvas_frame, bg="white")
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.h_scroll = ttk.Scrollbar(canvas_frame, orient="horizontal", command=self.canvas.xview)
        self.h_scroll.grid(row=1, column=0, sticky="ew")
        self.v_scroll = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        self.v_scroll.grid(row=0, column=1, sticky="ns")
        self.canvas.configure(xscrollcommand=self.h_scroll.set, yscrollcommand=self.v_scroll.set)

    def _on_job_canvas_configure(self, event):
        self.job_canvas.itemconfig(self.job_window_id, width=event.width)

    # ---- Rebuild jobs area ----
    def rebuild_job_area(self):
        for widget in self.job_row_frame.winfo_children():
            widget.destroy()
        self.job_rows.clear()
        show_prio = (self.sched_var.get() == "Priority NP")
        self._create_job_header(show_prio)
        self._add_job_row(show_prio)
        w = self.job_canvas.winfo_width()
        if w > 10:
            self.job_canvas.itemconfig(self.job_window_id, width=w)

    def _create_job_header(self, show_priority):
        header = ttk.Frame(self.job_row_frame)
        header.pack(fill="x", pady=(0,4))
        cols = [("Name", 0), ("Size", 1), ("Burst", 2)]
        if show_priority:
            cols.append(("Priority", 3))
        for _, col_idx in cols:
            header.grid_columnconfigure(col_idx, weight=1, uniform="mvt_jobcols")
        for label, col_idx in cols:
            ttk.Label(header, text=label, anchor="center").grid(row=0, column=col_idx,
                sticky="ew", padx=1)
        self.job_header_row = header

    def _add_job_row(self, show_priority):
        row = MemoryJobRow(self.job_row_frame, self, show_priority)
        self.job_rows.append(row)
        return row

    def on_settings_change(self, event=None):
        if self.sched_var.get() == "RR":
            self.quantum_frame.pack(anchor="w", before=self.run_btn, pady=(10, 0))
        else:
            self.quantum_frame.pack_forget()
        self.rebuild_job_area()

    def on_job_row_change(self):
        empty = [r for r in self.job_rows if r.is_empty()]
        if len(empty) == 0:
            show_prio = (self.sched_var.get() == "Priority NP")
            self._add_job_row(show_prio)
        elif len(empty) > 1:
            keep = empty[0]
            for r in empty[1:]:
                r.destroy()
                self.job_rows.remove(r)

    def get_jobs(self):
        return [row.get_job() for row in self.job_rows if row.is_valid()]

    def run_simulation(self):
        jobs = self.get_jobs()
        if not jobs:
            messagebox.showerror("Error", "Add at least one valid job.")
            return
        # Duplicate name check
        seen_names = set()
        for job in jobs:
            if job["name"] in seen_names:
                messagebox.showerror("Error", f"Duplicate job name: '{job['name']}'.")
                return
            seen_names.add(job["name"])
        try:
            os_size = int(self.os_size_var.get().strip())
            max_mem = int(self.max_mem_var.get().strip())
            if os_size <= 0 or max_mem <= os_size:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Invalid OS size or Max Memory.")
            return

        quantum = int(self.quantum_var.get().strip() or "1")
        events = simulate_mvt(
            jobs, os_size, max_mem,
            compaction=self.compaction_var.get(),
            scheduling=self.sched_var.get(),
            allocation=self.alloc_var.get(),
            quantum=quantum
        )
        draw_mvt_timeline(self.canvas, events, max_mem)