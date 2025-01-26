from .point import Point

class Position:
    def __init__(self, x: int | float, y: int | float):
        self.x = x
        self.y = y
    
    def convert_value(self, value, name: str):
        if isinstance(value, float):
            value = int(value)
        
        return value

    def confirm_value(self, value, name: str):
        if not isinstance(value, (int, float)):
            raise TypeError(f"Expected {name} to be of type `int` or `float` but got `{type(value)}`.")

        if value < 0:
            raise ValueError(f"Expected {name} to be zero or positive but got {value}.")

        return self.convert_value(value, name)
    
    @property
    def x(self) -> int:
        return self._x

    @property
    def y(self) -> int:
        return self._y
    
    @x.setter
    def x(self, value):
        self._x = self.confirm_value(value, "x positon")

    @y.setter
    def y(self, value):
        self._y = self.confirm_value(value, "y position")
    
    def get_xy(self) -> tuple[int, int]:
        return (self.x, self.y)
    
    def get_yx(self) -> tuple[int, int]:
        return (self.y, self.x)

    def get_x(self) -> int:
        return self.x

    def get_y(self) -> int:
        return self.y

    def to_point(self) -> Point:
        return Point(self.x, self.y)

    def __str__(self):
        return f"Position(x={self.x}, y={self.y})"