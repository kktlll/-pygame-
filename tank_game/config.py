import pygame
import os

# 游戏常量
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GRID_SIZE = 40
TANK_SIZE = 36
MIN_WALL_SPACING = 1
MAX_FIXED_WALLS = 18
MAX_BREAKABLE_WALLS = 25

# 颜色定义
COLORS = {
    'background': (30, 30, 40),
    'player': (80, 160, 255),
    'enemy': (220, 100, 100),
    'wall': (120, 80, 60),
    'breakable_wall': (100, 100, 120),
    'bullet': (255, 220, 50),
    'lightning_bullet': (100, 200, 255),
    'big_bullet': (255, 100, 100),
    'text': (240, 240, 240),
    'explosion': (255, 200, 50),
    'health_potion': (255, 80, 80),
    'speed_potion': (80, 255, 80),
    'invincible_potion': (255, 255, 80),
    'bullet_upgrade': (200, 80, 255),
    'thruster': (255, 150, 50),
    'damage_normal': (255, 255, 100),
    'damage_lightning': (100, 200, 255),
    'damage_big': (255, 100, 100),
    'heal_effect': (80, 255, 80),
    'speed_effect': (80, 200, 255),
    'invincible_effect': (255, 220, 80),
    'pause_bg': (0, 0, 0, 180),
    'pause_text': (255, 255, 255),
    'pause_highlight': (255, 200, 0)
}

# 字体缓存
_font_cache = {}

def get_chinese_font(size):
    """获取中文字体"""
    if size in _font_cache:
        return _font_cache[size]

    try:
        font_paths = [
            'C:/Windows/Fonts/simhei.ttf',
            'C:/Windows/Fonts/simsun.ttc',
            'C:/Windows/Fonts/msyh.ttc',
        ]

        for font_path in font_paths:
            if os.path.exists(font_path):
                font = pygame.font.Font(font_path, size)
                _font_cache[size] = font
                return font

        font = pygame.font.Font(None, size)
        _font_cache[size] = font
        return font
    except:
        font = pygame.font.Font(None, size)
        _font_cache[size] = font
        return font