import pygame
import math
import random
from config import *

class Bullet:
    def __init__(self, x, y, angle, is_enemy=False):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = 7
        self.radius = 4
        self.color = COLORS['bullet']
        self.is_enemy = is_enemy
        self.damage = 25
        self.damage_type = "normal"

    def update(self):
        angle_rad = math.radians(self.angle)
        self.x += math.sin(angle_rad) * self.speed
        self.y -= math.cos(angle_rad) * self.speed

    def is_out_of_bounds(self):
        return (self.x < 0 or self.x > SCREEN_WIDTH or
                self.y < 0 or self.y > SCREEN_HEIGHT)

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

class NormalBullet(Bullet):
    def __init__(self, x, y, angle, is_enemy=False):
        super().__init__(x, y, angle, is_enemy)
        self.color = COLORS['bullet']
        self.damage = 25
        self.damage_type = "normal"

class LightningBullet(Bullet):
    def __init__(self, x, y, angle, is_enemy=False):
        super().__init__(x, y, angle, is_enemy)
        self.color = COLORS['lightning_bullet']
        self.speed = 10
        self.radius = 3
        self.damage = 15
        self.damage_type = "lightning"
        self.aoe_radius = 60

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        for i in range(5):
            offset_x = random.randint(-8, 8)
            offset_y = random.randint(-8, 8)
            pygame.draw.circle(surface, (200, 230, 255),
                               (int(self.x + offset_x), int(self.y + offset_y)), 1)

class BigBullet(Bullet):
    def __init__(self, x, y, angle, is_enemy=False):
        super().__init__(x, y, angle, is_enemy)
        self.color = COLORS['big_bullet']
        self.speed = 4
        self.radius = 10
        self.damage = 40
        self.damage_type = "big"