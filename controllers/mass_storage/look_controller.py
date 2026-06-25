from models.mass_storage.disk_scheduling_model import look_disk

class LOOKDiskController:
    def __init__(self, view):
        view.set_simulate_function(look_disk)