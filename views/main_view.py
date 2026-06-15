import tkinter as tk
from tkinter import ttk
from views.cpu_scheduling.cpu_scheduling_tab import CPUSchedulingTab
from controllers.cpu_scheduling.fcfs_cpu_scheduling_controller import FCFSCPUController
from controllers.cpu_scheduling.sjf_cpu_scheduling_controller import SJFCPUController
from controllers.cpu_scheduling.srtf_cpu_scheduling_controller import SRTFCPUController
from controllers.cpu_scheduling.priority_np_cpu_scheduling_controller import PriorityNPCPUController
from controllers.cpu_scheduling.priority_p_cpu_scheduling_controller import PriorityPCPUController
from controllers.cpu_scheduling.hrrn_cpu_scheduling_controller import HRRNCPUController
from controllers.cpu_scheduling.rr_cpu_scheduling_controller import RRCPUController



class MainView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # --- Main Notebook --- #
        self.main_notebook = ttk.Notebook(self)
        self.main_notebook.grid(row=0, column=0, sticky="nsew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- CPU Scheduling --- #
        cpu_scheduling_tab = ttk.Frame(self.main_notebook)
        self.main_notebook.add(cpu_scheduling_tab, text="CPU Scheduling")
        cpu_scheduling_tab.grid_rowconfigure(0, weight=1)
        cpu_scheduling_tab.grid_columnconfigure(0, weight=1)

        sub_cpu_scheduling_notebook = ttk.Notebook(cpu_scheduling_tab)
        sub_cpu_scheduling_notebook.grid(row=0, column=0, sticky="nsew")

        # FCFS
        fcfs_tab = CPUSchedulingTab(sub_cpu_scheduling_notebook)
        FCFSCPUController(fcfs_tab)
        sub_cpu_scheduling_notebook.add(fcfs_tab, text="First-Come, First-Served")

        # SJF (Non‑preemptive)
        sjf_tab = CPUSchedulingTab(sub_cpu_scheduling_notebook)
        SJFCPUController(sjf_tab)
        sub_cpu_scheduling_notebook.add(sjf_tab, text="Shortest-Job-First")

        # SRTF (Preemptive SJF)
        srtf_tab = CPUSchedulingTab(sub_cpu_scheduling_notebook)
        SRTFCPUController(srtf_tab)
        sub_cpu_scheduling_notebook.add(srtf_tab, text="Shortest-Remaining-Time-First")
        
        # Priority Non‑Preemptive
        extra_fields_priority = [
            ("Priority", "priority", 4, "", lambda v: v.isdigit() or v == "")
        ]
        prio_np_tab = CPUSchedulingTab(sub_cpu_scheduling_notebook, extra_fields=extra_fields_priority)
        PriorityNPCPUController(prio_np_tab)
        sub_cpu_scheduling_notebook.add(prio_np_tab, text="Priority Nonpreemptive")
        
        # Preemptive Priority
        prio_p_tab = CPUSchedulingTab(sub_cpu_scheduling_notebook, extra_fields=extra_fields_priority)
        PriorityPCPUController(prio_p_tab)
        sub_cpu_scheduling_notebook.add(prio_p_tab, text="Priority Preemptive")
        
        # HRRN
        hrrn_tab = CPUSchedulingTab(sub_cpu_scheduling_notebook)
        HRRNCPUController(hrrn_tab)
        sub_cpu_scheduling_notebook.add(hrrn_tab, text="Highest Response-Ratio Next")
        
        # Round Robin
        global_controls_rr = [
            {"label": "Time Quantum", "key": "quantum", "type": "spinbox", "default": 2, "from": 1, "to": 100}
        ]
        rr_tab = CPUSchedulingTab(sub_cpu_scheduling_notebook, global_controls=global_controls_rr)
        RRCPUController(rr_tab)
        sub_cpu_scheduling_notebook.add(rr_tab, text="Round-Robin")

        # --- Placeholders for other CPU scheduling tabs ---
        # NP SJF, P SJF, NP Priority, P Priority, HRRN, RR, MQ, MFQ ...
        # You'll create a similar view/controller pair for each one.

        # --- Memory Management --- #
        memory_management_tab = ttk.Frame(self.main_notebook)
        self.main_notebook.add(memory_management_tab, text="Memory Management")
        memory_management_tab.grid_rowconfigure(0, weight=1)
        memory_management_tab.grid_columnconfigure(0, weight=1)

        sub_memory_management_notebook = ttk.Notebook(memory_management_tab)
        sub_memory_management_notebook.grid(row=0, column=0, sticky="nsew")
        # MFT ATL, BF MFT RTL, FF MFT RTL, BAF MFT RTL, MVT NC, MVT C ...

        # --- Virtual Memory --- #
        virtual_memory_tab = ttk.Frame(self.main_notebook)
        self.main_notebook.add(virtual_memory_tab, text="Virtual Memory")
        virtual_memory_tab.grid_rowconfigure(0, weight=1)
        virtual_memory_tab.grid_columnconfigure(0, weight=1)

        sub_virtual_memory_notebook = ttk.Notebook(virtual_memory_tab)
        sub_virtual_memory_notebook.grid(row=0, column=0, sticky="nsew")
        # FIFO, Optimal, LRU, LRUA ARB, LRUA SCC, LRUA ESC, CB LFU, CB MFU ...

        # --- Mass Storage --- #
        mass_storage_tab = ttk.Frame(self.main_notebook)
        self.main_notebook.add(mass_storage_tab, text="Mass Storage")
        mass_storage_tab.grid_rowconfigure(0, weight=1)
        mass_storage_tab.grid_columnconfigure(0, weight=1)

        sub_mass_storage_notebook = ttk.Notebook(mass_storage_tab)
        sub_mass_storage_notebook.grid(row=0, column=0, sticky="nsew")
        # FCFS, SSTF, SCAN, C-SCAN, LOOK ...