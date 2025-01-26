from . import CallbackContext

class OnOpenContext(CallbackContext):
    """
    A child of `CallbackContext` for screens closing callback with id="on_open".
    """

    def __init__(self):
        super().__init__(id = "on_open")

class OnCloseContext(CallbackContext):
    """
    A child of `CallbackContext` for screens closing callback with id="on_close".
    """

    def __init__(self, reason: int = None):
        super().__init__(id = "on_close")
        self.reason = reason

    def get_reason(self) -> int:
        return self.reason