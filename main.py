from kandinsky import fill_rect, color
from time import sleep, monotonic
from math import fabs
class Vector2:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
    def __mul__(self, mul):
        return Vector2(self.x * mul, self.y * mul)
    
    def __truediv__(self, div):
        return Vector2(self.x / div, self.y / div)

    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)

    def magnitude(self):
        return (self.x**2 + self.y**2)**0.5

    def normalize(self):
        mag = self.magnitude()
        if mag == 0:
            return Vector2(0, 0)
        return self / mag

    def dot(self, other):
        return self.x * other.x + self.y * other.y

def set_pixel(position: Vector2, color):
    fill_rect(position.x * PIXEL_SIZE.x, position.y * PIXEL_SIZE.y, PIXEL_SIZE.x, PIXEL_SIZE.y, color)

SCREEN_SIZE = Vector2(200, 200)
PIXEL_SIZE = Vector2(2, 2)
GRID_SIZE = Vector2(100, 100)

class Pixel:
    def __init__(self, material):
        self.material = material
        self.last_position = Vector2(0, 0)
        self.position = Vector2(0, 0)
        self.velocity = Vector2(0, 0)

    def _draw(self):
        self._physics_update()
        set_pixel(self.last_position, color(255, 255, 255))
        set_pixel(self.position, color(0, 0, 0))

    def _physics_update(self):
        self.last_position = self.position
        self.position += Vector2(int(self.velocity.x), int(self.velocity.y))
class PixelManager:
    _pixel_grid = [[None for _ in range(GRID_SIZE.y)] for _ in range(GRID_SIZE.x)]
    def __init__(self, gravity: float):
        self.gravity = gravity

    def add_pixel(self, pixel: Pixel):
        x = pixel.position.x
        y = pixel.position.y
        self._pixel_grid[x][y] = pixel # type: ignore
    
    def draw(self):
        for line in self._pixel_grid:
            for pixel in line:
                if type(pixel) is Pixel: pixel._draw()

manager = PixelManager(9.8)

pixel = Pixel(0)
manager.add_pixel(pixel)

pixel.position = Vector2(50, 0)

time = monotonic()
last_time = time

while True:
    time = monotonic()
    print(pixel.velocity.x, pixel.velocity.y)
    delta = fabs(time - last_time)
    pixel.velocity += Vector2(0, 2 * delta)
    manager.draw()
    last_time = time