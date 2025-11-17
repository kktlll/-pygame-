import pygame
from config import *

class Wall:
    def __init__(self, x, y, breakable=False):
        self.rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
        self.breakable = breakable

    def draw(self, surface):
        color = COLORS['breakable_wall'] if self.breakable else COLORS['wall']
        pygame.draw.rect(surface, color, self.rect)
        if self.breakable:
            pygame.draw.rect(surface, (80, 80, 100), self.rect, 2)