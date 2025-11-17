import pygame
import math
from config import *

class PowerUp:
    def __init__(self, x, y, power_type):
        self.x = x
        self.y = y
        self.type = power_type
        self.radius = 15
        self.color = COLORS.get(f'{power_type}_potion', COLORS['bullet_upgrade'])
        self.blink_timer = 0
        self.float_timer = 0

    def update(self):
        self.blink_timer = (self.blink_timer + 1) % 30
        self.float_timer += 1

    def draw(self, surface):
        float_offset = math.sin(self.float_timer * 0.1) * 3
        draw_y = self.y + float_offset

        if self.blink_timer < 15:
            pygame.draw.circle(surface, self.color, (int(self.x), int(draw_y)), self.radius)
            pygame.draw.circle(surface, (255, 255, 255), (int(self.x), int(draw_y)), self.radius - 5)

        font = get_chinese_font(18)
        if self.type == "health":
            icon_text = font.render("❤️", True, (255, 255, 255))
        elif self.type == "speed":
            icon_text = font.render("⚡", True, (255, 255, 255))
        elif self.type == "invincible":
            icon_text = font.render("🛡️", True, (255, 255, 255))
        elif self.type == "bullet_upgrade":
            icon_text = font.render("★", True, (255, 255, 255))

        text_rect = icon_text.get_rect(center=(self.x, draw_y))
        surface.blit(icon_text, text_rect)