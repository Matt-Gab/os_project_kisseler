import tkinter as tk
from tkinter import ttk

from views.main_view import MainView

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Operating System Simulator")
    root.geometry("960x540")
    
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    view = MainView(root)
    view.grid(row=0, column=0, sticky="nsew")

    root.mainloop()