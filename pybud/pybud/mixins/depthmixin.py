class DepthMixin:
    def __init__(self):
        self._depth = -1

    def _set_depth(self, depth: int):
        # TODO: add a comprehensive erorr message
        assert isinstance(depth, int)
        assert depth >= 0
        self._depth = depth

    def _get_depth(self):
        return self._depth