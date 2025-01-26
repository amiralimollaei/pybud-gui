import math

class Point:
    def __init__(self, x: int | float, y: int | float):
        self.x = x
        self.y = y
    
    def convert_value(self, value, name: str):
        if isinstance(value, float):
            value = float(value)
        
        return value

    def confirm_value(self, value, name: str):
        if not isinstance(value, (int, float)):
            raise TypeError(f"Expected {name} to be of type `int` or `float` but got `{type(value)}`.")

        if value < 0:
            raise ValueError(f"Expected {name} to be zero or positive but got {value}.")

        return self.convert_value(value, name)
    
    @property
    def x(self) -> float:
        return self._x

    @property
    def y(self) -> float:
        return self._y
    
    @x.setter
    def x(self, value):
        self._x = self.confirm_value(value, "x axis")

    @y.setter
    def y(self, value):
        self._y = self.confirm_value(value, "y axis")
    
    def get_size(self) -> tuple[float, float]:
        return (self.x, self.y)

    def get_x(self) -> float:
        return self.x

    def get_y(self) -> float:
        return self.y

    def angle_to(self, other: 'Point') -> float:
        # Aspect ratio adjustment: divide dx by 2
        dx = (other.x - self.x) / 2.0
        dy = -(other.y - self.y)
        
        # Compute angle and normalize to [0, 360)
        angle_radians = math.atan2(dy, dx)
        angle_degrees = math.degrees(angle_radians)
        if angle_degrees < 0:
            angle_degrees = -angle_degrees + 180
        
        return angle_degrees

    def distance_to(self, other: 'Point') -> float:
        # we divide `dx` by 2 because each 2 vertical distance in x axis, almost
        # equals 1 horizontal distance in y axis for our 2d plane of characters
        dx = (other.x - self.x) / 2.0
        dy = other.y - self.y

        return math.sqrt(dx ** 2 + dy ** 2)

    def __str__(self):
        return f"Point(x={self.x}, y={self.y})"