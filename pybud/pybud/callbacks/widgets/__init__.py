from .. import CallbackContext

class OnInitContext(CallbackContext):
    """
    A child of `CallbackContext` for widgets initializing callback with id="on_init".
    """

    def __init__(self):
        super().__init__(id = "on_init")

class OnCloseContext(CallbackContext):
    """
    A child of `CallbackContext` for widgets closing callback with id="on_close".
    """

    def __init__(self):
        super().__init__(id = "on_close")