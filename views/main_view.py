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

from views.memory_management.mft_tab import MFTTab
from views.memory_management.mvt_tab import MVTTab

from views.virtual_memory.page_replacement_tab import PageReplacementTab
from controllers.virtual_memory.fifo_controller import FIFOController
from controllers.virtual_memory.optimal_controller import OptimalController
from controllers.virtual_memory.lru_controller import LRUController
from controllers.virtual_memory.counting_based_controller import CountingBasedController

from views.mass_storage.disk_scheduling_tab import DiskSchedulingTab
from controllers.mass_storage.fcfs_controller import FCFSDiskController
from controllers.mass_storage.sstf_controller import SSTFDiskController
from controllers.mass_storage.scan_controller import SCANDiskController
from controllers.mass_storage.cscan_controller import CSCANDiskController
from controllers.mass_storage.look_controller import LOOKDiskController


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
            {"label": "Time\nQuantum", "key": "quantum", "type": "entry", "default": ""}
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
        
        # MFT
        mft_tab = MFTTab(sub_memory_management_notebook)
        sub_memory_management_notebook.add(mft_tab, text="MFT")
        # MFT ATL, BF MFT RTL, FF MFT RTL, BAF MFT RTL, MVT NC, MVT C ...
        
        # MVT
        mvt_tab = MVTTab(sub_memory_management_notebook)
        sub_memory_management_notebook.add(mvt_tab, text="MVT")

        # --- Virtual Memory --- #
        virtual_memory_tab = ttk.Frame(self.main_notebook)
        self.main_notebook.add(virtual_memory_tab, text="Virtual Memory")
        virtual_memory_tab.grid_rowconfigure(0, weight=1)
        virtual_memory_tab.grid_columnconfigure(0, weight=1)

        sub_virtual_memory_notebook = ttk.Notebook(virtual_memory_tab)
        sub_virtual_memory_notebook.grid(row=0, column=0, sticky="nsew")

        # --- FIFO ---
        fifo_tab = PageReplacementTab(sub_virtual_memory_notebook, "FIFO")
        FIFOController(fifo_tab)
        sub_virtual_memory_notebook.add(fifo_tab, text="FIFO")

        # --- Optimal ---
        opt_tab = PageReplacementTab(sub_virtual_memory_notebook, "Optimal")
        OptimalController(opt_tab)
        sub_virtual_memory_notebook.add(opt_tab, text="Optimal")

        # --- LRU ---
        lru_tab = PageReplacementTab(sub_virtual_memory_notebook, "LRU")
        LRUController(lru_tab)
        sub_virtual_memory_notebook.add(lru_tab, text="LRU")

        # --- Counting-Based (LFU / MFU) ---
        extra_ctrl_cb = [
            {"label": "Policy", "key": "policy", "type": "combobox",
             "values": ["LFU", "MFU"], "default": "LFU"}
        ]
        cb_tab = PageReplacementTab(sub_virtual_memory_notebook, "Counting-Based",
                                    extra_controls=extra_ctrl_cb)
        CountingBasedController(cb_tab)
        sub_virtual_memory_notebook.add(cb_tab, text="Counting-Based")

        # --- Placeholder for LRU Approximation ---
        frame = ttk.Frame(sub_virtual_memory_notebook)
        sub_virtual_memory_notebook.add(frame, text="LRU Approximation")         

        # --- Mass Storage --- #
        mass_storage_tab = ttk.Frame(self.main_notebook)
        self.main_notebook.add(mass_storage_tab, text="Mass Storage")
        mass_storage_tab.grid_rowconfigure(0, weight=1)
        mass_storage_tab.grid_columnconfigure(0, weight=1)

        sub_mass_storage_notebook = ttk.Notebook(mass_storage_tab)
        sub_mass_storage_notebook.grid(row=0, column=0, sticky="nsew")

        # --- FCFS ---
        fcfs_disk_tab = DiskSchedulingTab(sub_mass_storage_notebook, "FCFS")
        FCFSDiskController(fcfs_disk_tab)
        sub_mass_storage_notebook.add(fcfs_disk_tab, text="FCFS")

        # --- SSTF ---
        sstf_disk_tab = DiskSchedulingTab(sub_mass_storage_notebook, "SSTF")
        SSTFDiskController(sstf_disk_tab)
        sub_mass_storage_notebook.add(sstf_disk_tab, text="SSTF")

        # --- SCAN ---
        scan_disk_tab = DiskSchedulingTab(sub_mass_storage_notebook, "SCAN")
        SCANDiskController(scan_disk_tab)
        sub_mass_storage_notebook.add(scan_disk_tab, text="SCAN")

        # --- C-SCAN ---
        cscan_disk_tab = DiskSchedulingTab(sub_mass_storage_notebook, "C-SCAN")
        CSCANDiskController(cscan_disk_tab)
        sub_mass_storage_notebook.add(cscan_disk_tab, text="C-SCAN")

        # --- LOOK ---
        look_disk_tab = DiskSchedulingTab(sub_mass_storage_notebook, "LOOK")
        LOOKDiskController(look_disk_tab)
        sub_mass_storage_notebook.add(look_disk_tab, text="LOOK")
        # FCFS, SSTF, SCAN, C-SCAN, LOOK ...