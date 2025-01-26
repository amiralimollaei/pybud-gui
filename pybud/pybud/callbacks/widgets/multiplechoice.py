from .. import CallbackContext

class OnSelectionChanged(CallbackContext):
    """
    A child of `CallbackContext` for widgets initializing callback with id="on_selection_changed".
    """

    def __init__(self, new_selection):
        super().__init__(id = "on_selection_changed")
        self.new_selection = new_selection
    
    def get_new_selection(self):
        return self.new_selection