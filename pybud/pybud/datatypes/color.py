class Color:
    def __init__(self, r: int | float, g: int | float, b: int | float):
        self.r = r
        self.g = g
        self.b = b
    
    def convert_value(self, value, name: str):
        if isinstance(value, float):
            if value < 0 or value > 1:
                raise ValueError(f"Expected {name} to be in range [0, 1] but got {value}.")

            value = int(value * 255)
        
        return value
    
    def confirm_value(self, value, name: str):
        if not isinstance(value, (int, float)):
            raise TypeError(f"Expected {name} to be of type `int` or `float` but got `{type(value)}`.")

        return self.convert_value(value, name)
    
    @property
    def r(self) -> int:
        return self.convert_value(self._r, "red")

    @property
    def g(self) -> int:
        return self.convert_value(self._g, "green")
    
    @property
    def b(self) -> int:
        return self.convert_value(self._b, "blue")
    
    @r.setter
    def r(self, value):
        self._r = self.confirm_value(value, "red")
    
    @g.setter
    def g(self, value):
        self._g = self.confirm_value(value, "green")
    
    @b.setter
    def b(self, value):
        self._b = self.confirm_value(value, "blue")
    
    def get_rgb(self) -> tuple[int, int, int]:
        return (self.r, self.g, self.b)

    def get_bgr(self) -> tuple[int, int, int]:
        return (self.b, self.g, self.r)

    def __str__(self):
        return f"Color({self.r}, {self.g}, {self.b})"