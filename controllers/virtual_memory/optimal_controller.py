from models.virtual_memory.page_replacement_model import optimal_page_replacement

class OptimalController:
    def __init__(self, view):
        view.set_simulate_function(optimal_page_replacement)