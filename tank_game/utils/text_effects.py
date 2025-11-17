import pygame
from config import *

class DamageText:
    def __init__(self, x, y, damage, damage_type="normal"):
        self.x = x
        self.y = y
        self.damage = damage
        self.lifetime = 60
        self.velocity_y = -2
        self.alpha = 255
        self.damage_type = damage_type

        self.color_map = {
            "normal": COLORS['damage_normal'],
            "lightning": COLORS['damage_lightning'],
            "big": COLORS['damage_big']
        }
        self.color = self.color_map.get(damage_type, COLORS['damage_normal'])

    def update(self):
        self.y += self.velocity_y
        self.lifetime -= 1
        self.alpha = max(0, int(255 * (self.lifetime / 60)))
        return self.lifetime > 0

    def draw(self, surface):
        font = get_chinese_font(18)
        text = font.render(f"-{self.damage}", True, self.color)

        text_surface = pygame.Surface(text.get_size(), pygame.SRCALPHA)
        text_surface.fill((0, 0, 0, 0))
        text_surface.blit(text, (0, 0))
        text_surface.set_alpha(self.alpha)

        surface.blit(text_surface, (int(self.x - text.get_width() // 2), int(self.y)))

class HealText:
    def __init__(self, x, y, heal_amount):
        self.x = x
        self.y = y
        self.heal_amount = heal_amount
        self.lifetime = 60
        self.velocity_y = -2
        self.alpha = 255
        self.color = COLORS['heal_effect']

    def update(self):
        self.y += self.velocity_y
        self.lifetime -= 1
        self.alpha = max(0, int(255 * (self.lifetime / 60)))
        return self.lifetime > 0

    def draw(self, surface):
        font = get_chinese_font(18)
        text = font.render(f"+{self.heal_amount}", True, self.color)

        text_surface = pygame.Surface(text.get_size(), pygame.SRCALPHA)
        text_surface.fill((0, 0, 0, 0))
        text_surface.blit(text, (0, 0))
        text_surface.set_alpha(self.alpha)

        surface.blit(text_surface, (int(self.x - text.get_width() // 2), int(self.y)))

class StatusEffect:
    def __init__(self, effect_type, duration):
        self.effect_type = effect_type
        self.duration = duration
        self.max_duration = duration
        self.icon_size = 30

        self.effect_info = {
            "invincible": {"color": COLORS['invincible_effect'], "name": "无敌", "icon": "🛡️"},
            "speed": {"color": COLORS['speed_effect'], "name": "加速", "icon": "⚡"},
            "heal": {"color": COLORS['heal_effect'], "name": "治疗", "icon": "❤️"},
            "bullet_normal": {"color": COLORS['bullet'], "name": "普通炮弹", "icon": "●"},
            "bullet_lightning": {"color": COLORS['lightning_bullet'], "name": "闪电炮弹", "icon": "ϟ"},
            "bullet_big": {"color": COLORS['big_bullet'], "name": "巨型炮弹", "icon": "⬤"}
        }

    def update(self):
        self.duration -= 1
        return self.duration > 0

    def draw(self, surface, x, y):
        info = self.effect_info.get(self.effect_type, {"color": (255, 255, 255), "name": "未知", "icon": "?"})
        font = get_chinese_font(16)

        bg_rect = pygame.Rect(x, y, self.icon_size + 130, self.icon_size)
        pygame.draw.rect(surface, (40, 40, 60), bg_rect, border_radius=5)
        pygame.draw.rect(surface, info["color"], bg_rect, 2, border_radius=5)

        icon_text = font.render(info["icon"], True, info["color"])
        surface.blit(icon_text, (x + 5, y + 5))

        name_text = font.render(info["name"], True, (255, 255, 255))
        surface.blit(name_text, (x + 35, y + 5))

        progress_width = 60
        progress_fill = (self.duration / self.max_duration) * progress_width
        progress_rect = pygame.Rect(x + 35, y + 20, progress_width, 6)
        fill_rect = pygame.Rect(x + 35, y + 20, progress_fill, 6)

        pygame.draw.rect(surface, (80, 80, 100), progress_rect)
        pygame.draw.rect(surface, info["color"], fill_rect)

        if self.duration < 9990:
            time_text = font.render(f"{self.duration // 60}秒", True, (200, 200, 200))
            surface.blit(time_text, (x + 100, y + 15))