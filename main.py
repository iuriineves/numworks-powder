from kandinsky import fill_rect, color
from time import sleep, monotonic
from math import fabs, floor
from ion import keydown, KEY_LEFT, KEY_UP, KEY_DOWN, KEY_RIGHT, KEY_OK # type: ignore

def get_line(coord1, coord2):
  
    dx = (coord2.x - coord1.x)
    dy = (coord2.y - coord1.y)
    if dx == 0:
        dx += 1
    elif dy == 0:
        dy += 1
    
    if abs(dx) >= abs(dy):
        step = abs(dx)
    else:
        step = abs(dy)
    
    dx = dx / step
    dy = dy / step
    x = coord1.x
    y = coord2.y

    points = []
    for i in range(int(step)):
        points.append(Vector2(x, y))
        x += dx
        y += dy
    return points

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
    fill_rect(
        int(position.x * int(PIXEL_SIZE.x)),
        int(position.y * int(PIXEL_SIZE.y)),
        int(PIXEL_SIZE.x),
        int(PIXEL_SIZE.y),
        color
    )

SCREEN_SIZE = Vector2(200, 200)
PIXEL_SIZE = Vector2(4, 4)
GRID_SIZE = Vector2(50, 50)

MOUSE_SPRITE = [
                ["", color(0, 0, 0), ""],
                [color(0, 0, 0), "", color(0, 0, 0)],
                ["", color(0, 0, 0), ""],
                ]

pixel_grid = [[None for _ in range(int(GRID_SIZE.y))] for _ in range(int(GRID_SIZE.x))]
class Material:
    def __init__(self, color, adhesion: float, viscosity: float, gravity: int) -> None:
        self.color = color
        self.adhesion = adhesion
        self.viscosity = viscosity
        self.gravity = gravity

class MaterialType:
    SAND = Material(color(235, 177, 52), 0.2, 0.0, 2)
    STONE = Material(color(82, 84, 87), 0.0, 0.0, 0)


class Pixel:
    def __init__(self, material: Material):
        self.material = material
        self.last_position = Vector2(0, 0)
        self.position = Vector2(0, 0)
        self.velocity = Vector2(0, 0)

    def _draw(self, delta):
        self._physics_update(delta)
        set_pixel(self.last_position, color(255, 255, 255))
        pixel_grid[int(self.last_position.y)][int(self.last_position.x)] = None
        set_pixel(self.position, self.material.color)
        if int(self.position.y) < len(pixel_grid) and int(self.position.x) < len(pixel_grid[0]):
            pixel_grid[int(self.position.y)][int(self.position.x)] = self # type: ignore

    def _physics_update(self, delta):
        if self.material == MaterialType.STONE:
            print("a")

        self.last_position = self.position
        self.velocity.y += self.material.gravity * delta
        points = get_line(self.position, self.position + self.velocity)
        for i, point in enumerate(points):
            if int(point.y) >= len(pixel_grid) or int(point.x) >= len(pixel_grid[0]):
                self.position = Vector2(int(point.x), int(point.y))
                break
            if pixel_grid[int(point.y)][int(point.x)] != None and pixel_grid[int(point.y)][int(point.x)] != self:
                self.position = Vector2(int(points[i-1].x), int(points[i-1].y))
                break
        else:
            self.position += Vector2(int(self.velocity.x), int(self.velocity.y))
        
class PixelManager:

    def add_pixel(self, pixel: Pixel):
        x = pixel.position.x
        y = pixel.position.y
        pixel_grid[y][x] = pixel # type: ignore
    
    def remove_pixel(self, pixel):
        x = pixel.position.x
        y = pixel.position.y
        pixel_grid[y][x] = None

    def draw(self):
        for line in pixel_grid:
            #sleep(0.1)
            for pixel in line:
                if type(pixel) is Pixel: 
                    delta = fabs(time - last_time)
                    pixel._draw(delta)

class Mouse():
    def __init__(self, pixel_manager: PixelManager) -> None:
        self.pixel_manager = pixel_manager
        self.position = Vector2(0, 0)
        self.last_position = Vector2(0, 0)

    def handle_input(self):
        if keydown(KEY_RIGHT):
            self.position = Vector2(self.position.x + 1, self.position.y)
        if keydown(KEY_LEFT):
            self.position = Vector2(self.position.x - 1, self.position.y)
        if keydown(KEY_UP):
            self.position = Vector2(self.position.x, self.position.y - 1)
        if keydown(KEY_DOWN):
            self.position = Vector2(self.position.x, self.position.y + 1)
        if keydown(KEY_OK):
            new_px = Pixel(MaterialType.SAND)
            new_px.position = self.position + Vector2(1, 1)
            self.pixel_manager.add_pixel(new_px)


    def draw(self):
        self.handle_input()
        for i, line in enumerate(MOUSE_SPRITE):
            for j, pixel in enumerate(line):
                if pixel == "": continue
                set_pixel((Vector2(j, i) + self.last_position), color(255, 255, 255))
                set_pixel(Vector2(j, i) + self.position, color(255, 0, 0))
        self.last_position = self.position

manager = PixelManager()
mouse = Mouse(manager)

for i in range(10):
    pixel = Pixel(MaterialType.STONE)
    pixel.position = Vector2(5 + i, 20)
    manager.add_pixel(pixel)

time = monotonic()
last_time = time

while True:
    time = monotonic()
    mouse.draw()
    manager.draw()
    mouse.draw()
    last_time = time