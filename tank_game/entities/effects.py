import pygame
import random
import math
from config import *

class Explosion:
    def __init__(self, x, y, size=20):
        self.x = x
        self.y = y
        self.radius = 5
        self.max_radius = size
        self.growth_speed = 3
        self.active = True

    def update(self):
        self.radius += self.growth_speed
        if self.radius >= self.max_radius:
            self.active = False

    def draw(self, surface):
        pygame.draw.circle(surface, COLORS['explosion'], (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, (255, 255, 100), (int(self.x), int(self.y)), self.radius - 5)

class EffectParticle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(2, 4)
        self.lifetime = random.randint(20, 40)
        self.velocity_x = random.uniform(-1, 1)
        self.velocity_y = random.uniform(-1, 1)

    def update(self):
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.lifetime -= 1
        self.size = max(0, self.size - 0.1)
        return self.lifetime > 0 and self.size > 0

    def draw(self, surface):
        alpha = min(255, int(255 * (self.lifetime / 40)))
        color_with_alpha = (*self.color, alpha)

        particle_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(particle_surface, color_with_alpha, (self.size, self.size), self.size)
        surface.blit(particle_surface, (int(self.x - self.size), int(self.y - self.size)))