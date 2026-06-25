from models.mass_storage.disk_scheduling_model import scan_disk

class SCANDiskController:
    def __init__(self, view):
        view.set_simulate_function(scan_disk)