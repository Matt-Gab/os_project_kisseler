class MFTController:
    def __init__(self, view):
        self.view = view
        self.view.run_btn.config(command=self.view.run_simulation)  # already connected