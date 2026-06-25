from models.virtual_memory.page_replacement_model import lfu_page_replacement, mfu_page_replacement

class CountingBasedController:
    def __init__(self, view):
        self.view = view

        def simulate(refs, num_frames):
            policy = view.get_extra_value("policy")
            if policy == "LFU":
                return lfu_page_replacement(refs, num_frames)
            else:
                return mfu_page_replacement(refs, num_frames)

        view.set_simulate_function(simulate)