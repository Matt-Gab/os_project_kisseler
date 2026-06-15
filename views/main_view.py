# views/main_view.py
import tkinter as tk
from tkinter import ttk
from .cpu_scheduling.fcfs_cpu_scheduling_tab import FCFSCPUSchedulingTab
from controllers.cpu_scheduling.fcfs_cpu_scheduling_controller import FCFSCPUController

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

        # --- FCFS (fully wired) --- #
        fcfs_tab = FCFSCPUSchedulingTab(sub_cpu_scheduling_notebook)
        fcfs_controller = FCFSCPUController(fcfs_tab)
        sub_cpu_scheduling_notebook.add(fcfs_tab, text="First-Come, First Served")

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