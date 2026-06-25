from models.mass_storage.disk_scheduling_model import fcfs_disk

class FCFSDiskController:
    def __init__(self, view):
        view.set_simulate_function(fcfs_disk)