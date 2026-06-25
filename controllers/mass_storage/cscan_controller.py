from models.mass_storage.disk_scheduling_model import cscan_disk

class CSCANDiskController:
    def __init__(self, view):
        view.set_simulate_function(cscan_disk)