import tkinter as tk
from tkinter import ttk, messagebox
from utils.memory_drawer import draw_memory_timeline
from models.memory_management.mft_model import MemoryJob, simulate_mft

class MemoryJobRow:
    """Dynamic row for MFT job inputs. Columns: Name, Size, Burst, Priority (if shown), Partition (if shown)."""
    def __init__(self, parent, app, show_partition, show_priority):
        self.app = app
        self.show_partition = show_partition
        self.show_priority = show_priority
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill="x", pady=1)

        self.name_var = tk.StringVar()
        self.size_var = tk.StringVar()
        self.burst_var = tk.StringVar()
        self.priority_var = tk.StringVar()
        self.part_var = tk.StringVar()

        # Create all entries
        self.name_entry = ttk.Entry(self.frame, textvariable=self.name_var, justify="center")
        self.size_entry = ttk.Entry(self.frame, textvariable=self.size_var, justify="center")
        self.burst_entry = ttk.Entry(self.frame, textvariable=self.burst_var, justify="center")
        self.priority_entry = ttk.Entry(self.frame, textvariable=self.priority_var, justify="center")
        self.part_entry = ttk.Entry(self.frame, textvariable=self.part_var, justify="center")

        self._configure_columns()
        self._place_widgets()

        for var in (self.name_var, self.size_var, self.burst_var, self.priority_var, self.part_var):
            var.trace_add("write", self._on_change)

    def _configure_columns(self):
        # Determine which columns are visible
        for col in range(5):
            self.frame.grid_columnconfigure(col, weight=0)
        visible = [0, 1, 2]
        if self.show_priority:
            visible.append(3)
        if self.show_partition:
            visible.append(4)
        for col in visible:
            self.frame.grid_columnconfigure(col, weight=1, uniform="jobcols")

    def _place_widgets(self):
        self.name_entry.grid(row=0, column=0, sticky="ew", padx=1, pady=1)
        self.size_entry.grid(row=0, column=1, sticky="ew", padx=1, pady=1)
        self.burst_entry.grid(row=0, column=2, sticky="ew", padx=1, pady=1)
        if self.show_priority:
            self.priority_entry.grid(row=0, column=3, sticky="ew", padx=1, pady=1)
        else:
            self.priority_entry.grid_remove()
        if self.show_partition:
            self.part_entry.grid(row=0, column=4, sticky="ew", padx=1, pady=1)
        else:
            self.part_entry.grid_remove()

    def _on_change(self, *args):
        self.app.on_job_row_change()

    def is_empty(self):
        return (self.name_var.get().strip() == "" and
                self.size_var.get().strip() == "" and
                self.burst_var.get().strip() == "" and
                (not self.show_priority or self.priority_var.get().strip() == "") and
                (not self.show_partition or self.part_var.get().strip() == ""))

    def is_valid(self):
        name = self.name_var.get().strip()
        if not name: return False
        try:
            size = int(self.size_var.get().strip())
            burst = int(self.burst_var.get().strip())
            if size <= 0 or burst <= 0:
                return False
        except ValueError:
            return False
        if self.show_partition:
            try:
                part = int(self.part_var.get().strip())
                if part < 1: return False
            except ValueError:
                return False
        return True

    def get_job(self):
        if not self.is_valid():
            return None
        priority = int(self.priority_var.get().strip() or "99")
        return MemoryJob(
            self.name_var.get().strip(),
            int(self.size_var.get().strip()),
            int(self.burst_var.get().strip()),
            int(self.part_var.get().strip()) if self.show_partition else None,
            priority
        )

    def destroy(self):
        self.frame.destroy()


class PartitionRow:
    """Dynamic row for partition sizes – centered."""
    def __init__(self, parent, app, idx):
        self.app = app
        self.idx = idx
        self.frame = tk.Frame(parent)
        self.frame.pack(fill="x", pady=1)

        label_text = "OS" if idx == 0 else f"Partition {idx}"
        tk.Label(self.frame, text=label_text, anchor="center",
                 font=("Arial", 8)).pack(padx=2, pady=(0, 1), anchor="center")

        self.size_var = tk.StringVar()
        self.entry = ttk.Entry(self.frame, textvariable=self.size_var, width=8, justify="center")
        self.entry.pack(padx=2, pady=(0, 2), anchor="center")
        self.size_var.trace_add("write", self._on_change)

    def _on_change(self, *args):
        self.app.on_part_row_change()

    def is_empty(self):
        return self.size_var.get().strip() == ""

    def get_size(self):
        try:
            return int(self.size_var.get().strip())
        except ValueError:
            return None

    def destroy(self):
        self.frame.destroy()


class MFTTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.job_rows = []
        self.part_rows = []
        self.create_widgets()
        # initial build
        self.rebuild_job_area()
        self.add_part_row()   # OS row

    def create_widgets(self):
        main_panel = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_panel.pack(fill="both", expand=True)

        left_frame = ttk.Frame(main_panel)
        right_frame = ttk.Frame(main_panel)
        main_panel.add(left_frame, weight=4)
        main_panel.add(right_frame, weight=1)

        left_frame.grid_columnconfigure(0, weight=1)   # Jobs
        left_frame.grid_columnconfigure(1, weight=0)   # Partitions
        left_frame.grid_columnconfigure(2, weight=0)   # Settings
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
        self.job_window_id = self.job_canvas.create_window((0, 0), window=self.job_row_frame, anchor="nw",
                                                           tags="job_window")
        self.job_row_frame.bind("<Configure>",
            lambda e: self.job_canvas.configure(scrollregion=self.job_canvas.bbox("all")))
        self.job_canvas.configure(yscrollcommand=job_scroll.set)
        self.job_canvas.bind("<Configure>", self._on_job_canvas_configure)

        # ---- Partitions Column ----
        part_frame = ttk.LabelFrame(left_frame, text="Partitions", padding=3)
        part_frame.grid(row=0, column=1, sticky="nsew", padx=2)
        part_frame.grid_rowconfigure(0, weight=1)
        part_frame.grid_columnconfigure(0, weight=1)

        self.part_canvas = tk.Canvas(part_frame, borderwidth=0, highlightthickness=0,
                                     height=120, width=140)
        self.part_canvas.grid(row=0, column=0, sticky="nsew")
        part_scroll = ttk.Scrollbar(part_frame, orient="vertical", command=self.part_canvas.yview)
        part_scroll.grid(row=0, column=1, sticky="ns")

        self.part_row_frame = tk.Frame(self.part_canvas)
        self.part_window_id = self.part_canvas.create_window((0, 0), window=self.part_row_frame, anchor="nw")
        self.part_row_frame.bind("<Configure>",
            lambda e: self.part_canvas.configure(scrollregion=self.part_canvas.bbox("all")))
        self.part_canvas.configure(yscrollcommand=part_scroll.set)
        self.part_canvas.bind("<Configure>", self._on_part_canvas_configure)

        # ---- Settings Column ----
        ctrl_frame = ttk.LabelFrame(left_frame, text="Settings", padding=5)
        ctrl_frame.grid(row=0, column=2, sticky="nsew", padx=2)

        ttk.Label(ctrl_frame, text="Translation & Loading:").pack(anchor="w", pady=2)
        self.trans_var = tk.StringVar(value="absolute")
        trans_combo = ttk.Combobox(ctrl_frame, textvariable=self.trans_var,
                                   values=["absolute", "relocatable"], state="readonly", width=18)
        trans_combo.pack(anchor="w", fill="x")
        trans_combo.bind("<<ComboboxSelected>>", self.on_settings_change)

        ttk.Label(ctrl_frame, text="Scheduling:").pack(anchor="w", pady=(10, 2))
        self.sched_var = tk.StringVar(value="FCFS")
        sched_combo = ttk.Combobox(ctrl_frame, textvariable=self.sched_var,
                                   values=["FCFS", "SJF", "HRRN", "Priority NP", "RR"], state="readonly", width=18)
        sched_combo.pack(anchor="w", fill="x")
        sched_combo.bind("<<ComboboxSelected>>", self.on_settings_change)

        self.alloc_frame = ttk.Frame(ctrl_frame)
        self.alloc_label = ttk.Label(self.alloc_frame, text="Allocation Policy:")
        self.alloc_var = tk.StringVar(value="first_fit")
        self.alloc_combo = ttk.Combobox(self.alloc_frame, textvariable=self.alloc_var,
                                        values=["first_fit", "best_fit", "best_available_fit"],
                                        state="readonly", width=18)

        # Time Quantum (only for RR)
        self.quantum_frame = ttk.Frame(ctrl_frame)
        ttk.Label(self.quantum_frame, text="Time Quantum:").pack(anchor="w", pady=(10, 2))
        self.quantum_var = tk.StringVar(value="2")
        ttk.Entry(self.quantum_frame, textvariable=self.quantum_var, width=5,
                  justify="center").pack(anchor="w")

        self.run_btn = ttk.Button(ctrl_frame, text="Run Simulation", command=self.run_simulation)
        self.run_btn.pack(side="bottom", pady=10)

        # ---- Right side: Memory Timeline ----
        memory_frame = ttk.LabelFrame(right_frame, text="Memory Layout", padding=3)
        memory_frame.pack(fill="both", expand=True)

        canvas_frame = ttk.Frame(memory_frame)
        canvas_frame.pack(fill="both", expand=True)
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(canvas_frame, bg="white")
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.v_scroll = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        self.v_scroll.grid(row=0, column=1, sticky="ns")

        self.h_scroll = ttk.Scrollbar(canvas_frame, orient="horizontal", command=self.canvas.xview)
        self.h_scroll.grid(row=1, column=0, sticky="ew")

        self.canvas.configure(xscrollcommand=self.h_scroll.set,
                              yscrollcommand=self.v_scroll.set)

    # -----------------------------------------------------------------
    # Canvas resize handlers
    # -----------------------------------------------------------------
    def _on_job_canvas_configure(self, event):
        self._job_canvas_width = event.width
        self.job_canvas.itemconfig(self.job_window_id, width=event.width)

    def _on_part_canvas_configure(self, event):
        self.part_canvas.itemconfig(self.part_window_id, width=event.width)

    # -----------------------------------------------------------------
    # Complete rebuild of jobs area (header + rows)
    # -----------------------------------------------------------------
    def rebuild_job_area(self):
        """Destroy all job rows and header, then recreate from scratch."""
        for widget in self.job_row_frame.winfo_children():
            widget.destroy()
        self.job_rows.clear()

        show_part = (self.trans_var.get() == "absolute")
        show_prio = (self.sched_var.get() == "Priority NP")
        self._create_job_header(show_part, show_prio)
        self._add_job_row(show_part, show_prio)

        if hasattr(self, '_job_canvas_width') and self._job_canvas_width > 10:
            self.job_canvas.itemconfig(self.job_window_id, width=self._job_canvas_width)
        else:
            self.job_canvas.update_idletasks()
            w = self.job_canvas.winfo_width()
            if w > 10:
                self.job_canvas.itemconfig(self.job_window_id, width=w)

    def _create_job_header(self, show_partition, show_priority):
        cols = [("Name", 0), ("Size", 1), ("Burst", 2)]
        if show_priority:
            cols.append(("Priority", 3))
        if show_partition:
            cols.append(("Partition", 4))

        header = ttk.Frame(self.job_row_frame)
        header.pack(fill="x", pady=(0, 4))
        for _, col_idx in cols:
            header.grid_columnconfigure(col_idx, weight=1, uniform="jobcols")

        for label, col_idx in cols:
            ttk.Label(header, text=label, anchor="center").grid(row=0, column=col_idx,
                sticky="ew", padx=1)
        self.job_header_row = header

    def _add_job_row(self, show_partition, show_priority):
        row = MemoryJobRow(self.job_row_frame, self, show_partition, show_priority)
        self.job_rows.append(row)
        return row

    # -----------------------------------------------------------------
    # Settings change callback
    # -----------------------------------------------------------------
    def on_settings_change(self, event=None):
        show_part = (self.trans_var.get() == "absolute")

        # Allocation policy visibility
        if self.trans_var.get() == "relocatable":
            self.alloc_frame.pack(anchor="w", before=self.run_btn, pady=(10, 0))
            self.alloc_label.pack(anchor="w")
            self.alloc_combo.pack(anchor="w", fill="x")
        else:
            self.alloc_frame.pack_forget()

        # Time quantum visibility
        if self.sched_var.get() == "RR":
            self.quantum_frame.pack(anchor="w", before=self.run_btn, pady=(10, 0))
        else:
            self.quantum_frame.pack_forget()

        # Rebuild job area with new column visibility
        self.rebuild_job_area()

    # -----------------------------------------------------------------
    # Row management (trailing buffer)
    # -----------------------------------------------------------------
    def on_job_row_change(self):
        empty = [r for r in self.job_rows if r.is_empty()]
        if len(empty) == 0:
            show_part = (self.trans_var.get() == "absolute")
            show_prio = (self.sched_var.get() == "Priority NP")
            self._add_job_row(show_part, show_prio)
        elif len(empty) > 1:
            keep = empty[0]
            for r in empty[1:]:
                r.destroy()
                self.job_rows.remove(r)

    # -----------------------------------------------------------------
    # Partition rows
    # -----------------------------------------------------------------
    def add_part_row(self):
        idx = len(self.part_rows)
        row = PartitionRow(self.part_row_frame, self, idx)
        self.part_rows.append(row)

    def on_part_row_change(self):
        empty = [r for r in self.part_rows if r.is_empty()]
        if len(empty) == 0:
            self.add_part_row()
        elif len(empty) > 1:
            keep = empty[0]
            for r in empty[1:]:
                r.destroy()
                self.part_rows.remove(r)

    # -----------------------------------------------------------------
    # Data retrieval
    # -----------------------------------------------------------------
    def get_jobs(self):
        jobs = []
        for row in self.job_rows:
            job = row.get_job()
            if job:
                jobs.append(job)
        return jobs

    def get_partitions(self):
        sizes = []
        for row in self.part_rows:
            size = row.get_size()
            if size is not None:
                sizes.append(size)
        return sizes

    # -----------------------------------------------------------------
    # Simulation
    # -----------------------------------------------------------------
    def run_simulation(self):
        jobs = self.get_jobs()
        partitions = self.get_partitions()
        if not jobs or len(partitions) < 2:
            messagebox.showerror("Error", "Add at least one job and at least OS plus one partition.")
            return

        # Duplicate name check
        seen_names = set()
        for job in jobs:
            if job.name in seen_names:
                messagebox.showerror("Error", f"Duplicate job name: '{job.name}'.")
                return
            seen_names.add(job.name)

        # Invalid partition check (absolute mode only)
        if self.trans_var.get() == "absolute":
            max_part = len(partitions) - 1
            for job in jobs:
                if job.partition_number is None or job.partition_number < 1 or job.partition_number > max_part:
                    messagebox.showerror("Error",
                        f"Job '{job.name}' has an invalid partition number ({job.partition_number}).\n"
                        f"Valid range: 1 – {max_part}")
                    return

        trans = self.trans_var.get()
        alloc = self.alloc_var.get() if trans == "relocatable" else None
        cpu_sched = self.sched_var.get()
        quantum = int(self.quantum_var.get().strip() or "1")

        events = simulate_mft(jobs, partitions, trans, alloc, cpu_sched, quantum)
        draw_memory_timeline(self.canvas, events, partitions)