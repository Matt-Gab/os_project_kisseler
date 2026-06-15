# utils/process_row.py
import tkinter as tk
from tkinter import ttk
from typing import Callable, Dict, List, Optional, Tuple

ExtraFieldDef = Tuple[str, str, int, str, Optional[Callable[[str], bool]]]

class ProcessRow:
    def __init__(self, parent, app, extra_fields: Optional[List[ExtraFieldDef]] = None):
        self.app = app
        self.extra_fields = extra_fields or []
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill="x", pady=2)

        total_cols = 3 + len(self.extra_fields)
        for i in range(total_cols):
            self.frame.grid_columnconfigure(i, weight=1, uniform="rowcols")

        self.name_var = tk.StringVar()
        self.arrival_var = tk.StringVar()
        self.burst_var = tk.StringVar()

        self.name_entry = ttk.Entry(self.frame, textvariable=self.name_var, justify="center")
        self.name_entry.grid(row=0, column=0, sticky="ew", padx=2)

        self.arrival_entry = ttk.Entry(self.frame, textvariable=self.arrival_var, justify="center")
        self.arrival_entry.grid(row=0, column=1, sticky="ew", padx=2)

        self.burst_entry = ttk.Entry(self.frame, textvariable=self.burst_var, justify="center")
        self.burst_entry.grid(row=0, column=2, sticky="ew", padx=2)

        self.extra_vars: Dict[str, tk.StringVar] = {}
        self.extra_validators: Dict[str, Optional[Callable[[str], bool]]] = {}
        col_offset = 3
        for idx, (label, key, width, default, validator) in enumerate(self.extra_fields):
            var = tk.StringVar(value=default)
            self.extra_vars[key] = var
            self.extra_validators[key] = validator
            entry = ttk.Entry(self.frame, textvariable=var, width=width, justify="center")
            entry.grid(row=0, column=col_offset + idx, sticky="ew", padx=2)

        all_vars = [self.name_var, self.arrival_var, self.burst_var] + list(self.extra_vars.values())
        for var in all_vars:
            var.trace_add("write", self._on_change)

    def _on_change(self, *args):
        # Prevent re-entrant calls from simultaneous trace callbacks
        if not hasattr(self, '_guard'):
            self._guard = False
        if self._guard:
            return
        self._guard = True
        try:
            # Use after_idle to batch multiple rapid changes
            self.frame.after_idle(self.app.on_row_change)
        finally:
            self._guard = False

    # ----- trailing buffer helpers -----
    def is_empty(self) -> bool:
        if self.name_var.get().strip() != "":
            return False
        if self.arrival_var.get().strip() != "":
            return False
        if self.burst_var.get().strip() != "":
            return False
        for var in self.extra_vars.values():
            if var.get().strip() != "":
                return False
        return True

    def is_valid(self) -> bool:
        name = self.name_var.get().strip()
        if not name:
            return False
        try:
            arrival = int(self.arrival_var.get().strip())
            burst = int(self.burst_var.get().strip())
        except ValueError:
            return False
        if burst <= 0:
            return False
        for key, validator in self.extra_validators.items():
            if validator is not None:
                val = self.extra_vars[key].get().strip()
                if not validator(val):
                    return False
        return True

    def get_base_job_dict(self) -> dict:
        if not self.is_valid():
            return None
        return {
            "name": self.name_var.get().strip(),
            "arrival": int(self.arrival_var.get().strip()),
            "burst": int(self.burst_var.get().strip()),
        }

    def get_extra_values(self) -> Dict[str, str]:
        return {key: var.get().strip() for key, var in self.extra_vars.items()}

    def destroy(self):
        self.frame.destroy()