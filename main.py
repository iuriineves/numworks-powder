from kandinsky import fill_rect, color
from time import sleep, monotonic
from math import floor
from ion import keydown, KEY_LEFT, KEY_UP, KEY_DOWN, KEY_RIGHT, KEY_OK

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

class Material:
    def __init__(self, color, adhesion: float, viscosity: float, gravity: float) -> None:
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

    def _draw(self):
        self._physics_update()
        set_pixel(self.position, self.material.color)

    def _physics_update(self):
        self.last_position = self.position
        self.position += Vector2(int(self.velocity.x), int(self.velocity.y))
class PixelManager:
    _pixel_grid = [[None for _ in range(GRID_SIZE.y)] for _ in range(GRID_SIZE.x)]

    def add_pixel(self, pixel: Pixel):
        x = pixel.position.x
        y = pixel.position.y
        self._pixel_grid[y][x] = pixel # type: ignore

    def remove_pixel(self, pixel):
        x = pixel.position.x
        y = pixel.position.y
        set_pixel(pixel.position, color(255, 255, 255))
        self._pixel_grid[y][x] = None

    def draw(self, delta):
        for i, line in enumerate(self._pixel_grid[::-1]):
            for j, pixel in enumerate(line):
                if type(pixel) is Pixel:
                    if pixel.material.gravity == 0.0:
                        pixel._draw()
                        continue
                    pixel.velocity += Vector2(0, pixel.material.gravity * delta)
                    last_px = pixel.position
                    if self._pixel_grid[pixel.position.y + 1][pixel.position.x] != None:
                        if self._pixel_grid[pixel.position.y + 1][pixel.position.x + 1] == None:
                            pixel.velocity = Vector2(1, 1)
                            self.remove_pixel(pixel)
                            pixel._draw()
                            self.add_pixel(pixel)
                        elif self._pixel_grid[pixel.position.y + 1][pixel.position.x - 1] == None:
                           pixel.velocity = Vector2(-1, 1)
                           self.remove_pixel(pixel)
                           pixel._draw()
                           self.add_pixel(pixel)
                        else:
                            pixel.velocity = Vector2(0,0)
                            pixel._draw()
                    else:
                        collision = False
                        for px_vel in get_line(pixel.position - Vector2(floor(pixel.velocity.x), floor(pixel.velocity.y)), pixel.position + Vector2(floor(pixel.velocity.x), floor(pixel.velocity.y))):
                            set_pixel(px_vel, color(0, 255, 0))
                            if px_vel.y >= GRID_SIZE.y:
                                self.remove_pixel(pixel)
                                break
                            if type(self._pixel_grid[int(px_vel.y)][int(px_vel.x)]) is Pixel and not self._pixel_grid[int(px_vel.y)][int(px_vel.x)] is pixel:
                                
                                collision = True
                                self.remove_pixel(pixel)
                                pixel.position = Vector2(int(last_px.x), int(last_px.y))
                                pixel.velocity = Vector2(0, 0)
                                break
                            last_px = px_vel
                        if self._pixel_grid[int(pixel.position.y)][int(pixel.position.x)] or collision:
                            self.remove_pixel(pixel)
                            pixel._draw()
                            self.add_pixel(pixel)

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
    delta = time - last_time + 1
    mouse.draw()
    manager.draw(delta)
    mouse.draw()
    last_time = time