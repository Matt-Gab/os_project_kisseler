# controllers/virtual_memory/lru_controller.py
from models.virtual_memory.page_replacement_model import lru_page_replacement

class LRUController:
    def __init__(self, view):
        view.set_simulate_function(lru_page_replacement)