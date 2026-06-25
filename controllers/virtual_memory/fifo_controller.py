from models.virtual_memory.page_replacement_model import fifo_page_replacement

class FIFOController:
    def __init__(self, view):
        view.set_simulate_function(fifo_page_replacement)