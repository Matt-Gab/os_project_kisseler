from models.mass_storage.disk_scheduling_model import sstf_disk

class SSTFDiskController:
    def __init__(self, view):
        view.set_simulate_function(sstf_disk)