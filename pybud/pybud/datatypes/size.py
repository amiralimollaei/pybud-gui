class Size:
    def __init__(self, width: int | float, height: int | float):
        self.width = width
        self.height = height
    
    def convert_value(self, value, name: str):
        if isinstance(value, float):
            value = int(value)
        
        return value

    def confirm_value(self, value, name: str):
        if not isinstance(value, (int, float)):
            raise TypeError(f"Expected {name} to be of type `int` or `float` but got `{type(value)}`.")

        if value <= 0:
            raise ValueError(f"Expected {name} to be positive but got {value}.")

        return self.convert_value(value, name)
    
    @property
    def width(self) -> int:
        return self._w

    @property
    def height(self) -> int:
        return self._h
    
    @width.setter
    def width(self, value):
        self._w = self.confirm_value(value, "width")

    @height.setter
    def height(self, value):
        self._h = self.confirm_value(value, "height")
    
    def get_size(self) -> tuple[int, int]:
        return (self.width, self.height)

    def get_dimentions(self) -> tuple[int, int]:
        return (self.height, self.width)

    def get_width(self) -> int:
        return self.width

    def get_height(self) -> int:
        return self.height

    def __str__(self):
        return f"Size(w={self.width}, h={self.height})"