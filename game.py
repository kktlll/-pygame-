import pygame
import math
import random
import os

# 初始化
pygame.init()

# 游戏常量（核心调整：网格大小=坦克尺寸=40px，墙壁统一为1格大小）
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GRID_SIZE = 40  # 网格=坦克=墙壁宽度（1格=40px，统一尺寸）
TANK_SIZE = 40  # 坦克固定1格大小
MIN_WALL_SPACING = 1  # 墙壁最小间距（1格，坦克可穿过）
MAX_FIXED_WALLS = 18  # 固定墙数量增加（1格大小，多放不拥挤）
MAX_BREAKABLE_WALLS = 25  # 可破坏墙数量增加

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

# 创建窗口
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("坦克大战 - 优化随机地图版 | 1格坦克+墙壁")
clock = pygame.time.Clock()

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


class Tank:
    def __init__(self, x, y, color, is_enemy=False):
        self.x = x
        self.y = y
        self.color = color
        self.width = TANK_SIZE  # 固定1格大小（40px）
        self.height = TANK_SIZE
        self.speed = 3
        self.base_speed = 3
        self.rotation = 0
        self.cooldown = 0
        self.cooldown_time = 20
        self.health = 100
        self.max_health = 100
        self.is_enemy = is_enemy
        self.bullets = []
        self.bullet_type = "normal"
        self.invincible = 0
        self.speed_boost = 0
        self.bullet_timer = 0
        self.status_effects = []
        self.thruster_timer = 0
        self.effect_particles = []

    def move(self, dx, dy, walls, tanks):
        current_speed = self.speed
        if self.speed_boost > 0:
            current_speed = self.base_speed * 1.5

        new_x = self.x + dx * current_speed
        new_y = self.y + dy * current_speed

        # 边界检查（留20px边距，避免贴墙）
        if new_x < 20 or new_x > SCREEN_WIDTH - self.width - 20:
            return
        if new_y < 20 or new_y > SCREEN_HEIGHT - self.height - 20:
            return

        new_rect = pygame.Rect(new_x, new_y, self.width, self.height)

        # 墙壁碰撞检查（1格缝隙可穿过，因为墙壁是1格，缝隙=1格=坦克宽度）
        for wall in walls:
            if new_rect.colliderect(wall.rect):
                return

        # 坦克之间碰撞检查
        for tank in tanks:
            if tank != self and new_rect.colliderect(pygame.Rect(tank.x, tank.y, tank.width, tank.height)):
                return

        self.x = new_x
        self.y = new_y

        if dx != 0 or dy != 0:
            self.thruster_timer = (self.thruster_timer + 1) % 10

    def rotate(self, angle):
        self.rotation = angle

    def shoot(self):
        if self.cooldown <= 0:
            angle_rad = math.radians(self.rotation)

            if self.bullet_type == "normal":
                start_x = self.x + self.width // 2 + math.sin(angle_rad) * 30
                start_y = self.y + self.height // 2 - math.cos(angle_rad) * 30
                bullet = NormalBullet(start_x, start_y, self.rotation, self.is_enemy)

            elif self.bullet_type == "lightning":
                start_x = self.x + self.width // 2 + math.sin(angle_rad) * 30
                start_y = self.y + self.height // 2 - math.cos(angle_rad) * 30
                bullet = LightningBullet(start_x, start_y, self.rotation, self.is_enemy)

            elif self.bullet_type == "big":
                start_x = self.x + self.width // 2 + math.sin(angle_rad) * 35
                start_y = self.y + self.height // 2 - math.cos(angle_rad) * 35
                bullet = BigBullet(start_x, start_y, self.rotation, self.is_enemy)

            self.bullets.append(bullet)
            self.cooldown = self.cooldown_time
            return True
        return False

    def update(self):
        if self.cooldown > 0:
            self.cooldown -= 1

        # 更新炮弹增益计时器
        if self.bullet_timer > 0:
            self.bullet_timer -= 1
            if self.bullet_timer <= 0:
                self.bullet_type = "normal"
                self.status_effects = [effect for effect in self.status_effects
                                       if not effect.effect_type.startswith("bullet_")]

        # 更新状态效果
        self.status_effects = [effect for effect in self.status_effects if effect.update()]

        # 增益效果时间同步
        self.invincible = 0
        self.speed_boost = 0
        for effect in self.status_effects:
            if effect.effect_type == "invincible":
                self.invincible = effect.duration
            elif effect.effect_type == "speed":
                self.speed_boost = effect.duration

        # 更新特效粒子
        self.effect_particles = [p for p in self.effect_particles if p.update()]

        # 添加特效粒子
        if self.invincible > 0:
            self.add_effect_particles(COLORS['invincible_effect'])
        if self.speed_boost > 0:
            self.add_effect_particles(COLORS['speed_effect'])

    def add_effect_particles(self, color):
        if random.random() < 0.3:
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(20, 35)
            px = self.x + self.width // 2 + math.cos(angle) * distance
            py = self.y + self.height // 2 + math.sin(angle) * distance
            self.effect_particles.append(EffectParticle(px, py, color))

    def add_status_effect(self, effect_type, duration):
        self.status_effects = [effect for effect in self.status_effects if effect.effect_type != effect_type]
        self.status_effects.append(StatusEffect(effect_type, duration))

    def apply_powerup(self, power_type):
        if power_type == "health":
            heal_amount = 30
            self.health = min(self.max_health, self.health + heal_amount)
            return HealText(self.x + self.width // 2, self.y, heal_amount)
        elif power_type == "speed":
            duration = random.randint(300, 480)  # 5-8秒
            self.add_status_effect("speed", duration)
        elif power_type == "invincible":
            duration = random.randint(300, 480)  # 5-8秒
            self.add_status_effect("invincible", duration)
        elif power_type == "bullet_upgrade":
            duration = random.randint(300, 480)  # 5-8秒
            self.bullet_timer = duration
            bullet_types = ["lightning", "big"]
            self.bullet_type = random.choice(bullet_types)
            self.add_status_effect(f"bullet_{self.bullet_type}", duration)
        return None

    def draw(self, surface):
        for particle in self.effect_particles:
            particle.draw(surface)

        tank_rect = pygame.Rect(self.x, self.y, self.width, self.height)

        if self.invincible > 0:
            if self.invincible % 10 < 5:
                pygame.draw.rect(surface, (255, 255, 200), tank_rect)
            else:
                pygame.draw.rect(surface, self.color, tank_rect)
            pygame.draw.rect(surface, COLORS['invincible_effect'], tank_rect, 3)
        else:
            pygame.draw.rect(surface, self.color, tank_rect)

        if self.speed_boost > 0:
            self.draw_thruster(surface)

        angle_rad = math.radians(self.rotation)
        end_x = self.x + self.width // 2 + math.sin(angle_rad) * 25
        end_y = self.y + self.height // 2 - math.cos(angle_rad) * 25
        start_x = self.x + self.width // 2
        start_y = self.y + self.height // 2

        pygame.draw.line(surface, (50, 50, 50), (start_x, start_y), (end_x, end_y), 6)

        weapon_colors = {
            "normal": COLORS['bullet'],
            "lightning": COLORS['lightning_bullet'],
            "big": COLORS['big_bullet']
        }
        weapon_color = weapon_colors.get(self.bullet_type, COLORS['bullet'])
        pygame.draw.circle(surface, weapon_color, (int(self.x + 10), int(self.y - 5)), 3)

        # 生命值条
        bar_width = self.width
        bar_height = 3
        fill = (self.health / self.max_health) * bar_width
        outline_rect = pygame.Rect(self.x, self.y - 8, bar_width, bar_height)
        fill_rect = pygame.Rect(self.x, self.y - 8, fill, bar_height)
        pygame.draw.rect(surface, (100, 100, 100), outline_rect)
        pygame.draw.rect(surface, (0, 255, 0), fill_rect)

    def draw_thruster(self, surface):
        angle_rad = math.radians(self.rotation)

        thruster_x = self.x + self.width // 2 - math.sin(angle_rad) * 25
        thruster_y = self.y + self.height // 2 + math.cos(angle_rad) * 25

        flame_size = 8 + (self.thruster_timer // 2)

        pygame.draw.circle(surface, (255, 255, 0), (int(thruster_x), int(thruster_y)), flame_size - 4)
        pygame.draw.circle(surface, (255, 150, 0), (int(thruster_x), int(thruster_y)), flame_size - 2)
        pygame.draw.circle(surface, (255, 50, 0), (int(thruster_x), int(thruster_y)), flame_size)


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


class Wall:
    def __init__(self, x, y, breakable=False):
        # 墙壁固定1格大小（40x40px），不再随机大小
        self.rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
        self.breakable = breakable

    def draw(self, surface):
        color = COLORS['breakable_wall'] if self.breakable else COLORS['wall']
        pygame.draw.rect(surface, color, self.rect)
        if self.breakable:
            pygame.draw.rect(surface, (80, 80, 100), self.rect, 2)


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


def create_random_map():
    """生成优化后的随机地图：1格墙壁+合理缝隙"""
    walls = []

    # 1. 边界墙（不可破坏，固定1格厚度）
    # 上边界
    for x in range(0, SCREEN_WIDTH, GRID_SIZE):
        walls.append(Wall(x, 0, breakable=False))
    # 下边界
    for x in range(0, SCREEN_WIDTH, GRID_SIZE):
        walls.append(Wall(x, SCREEN_HEIGHT - GRID_SIZE, breakable=False))
    # 左边界
    for y in range(GRID_SIZE, SCREEN_HEIGHT - GRID_SIZE, GRID_SIZE):
        walls.append(Wall(0, y, breakable=False))
    # 右边界
    for y in range(GRID_SIZE, SCREEN_HEIGHT - GRID_SIZE, GRID_SIZE):
        walls.append(Wall(SCREEN_WIDTH - GRID_SIZE, y, breakable=False))

    # 2. 定义出生区域（扩大，避免拥挤）
    player_spawn_area = pygame.Rect(
        GRID_SIZE * 2, SCREEN_HEIGHT - GRID_SIZE * 5,
        GRID_SIZE * 6, GRID_SIZE * 3  # 玩家出生区：下方6x3格
    )
    enemy_spawn_area = pygame.Rect(
        GRID_SIZE * 2, GRID_SIZE * 2,
        GRID_SIZE * 15, GRID_SIZE * 4  # 敌方出生区：上方15x4格（扩大，随机出生）
    )

    # 3. 随机生成固定墙壁（1格大小，数量18个）
    fixed_wall_count = random.randint(15, MAX_FIXED_WALLS)
    used_grid = set()  # 记录已使用的网格坐标（x//40, y//40）

    for _ in range(fixed_wall_count):
        while True:
            # 随机网格坐标（避开边界）
            grid_x = random.randint(1, (SCREEN_WIDTH - GRID_SIZE * 2) // GRID_SIZE)
            grid_y = random.randint(1, (SCREEN_HEIGHT - GRID_SIZE * 2) // GRID_SIZE)
            x = grid_x * GRID_SIZE
            y = grid_y * GRID_SIZE

            # 检查是否在出生区域内
            wall_rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
            if wall_rect.colliderect(player_spawn_area) or wall_rect.colliderect(enemy_spawn_area):
                continue

            # 检查是否已使用该网格
            if (grid_x, grid_y) in used_grid:
                continue

            # 检查与其他墙壁的间距（最小1格，确保缝隙可穿）
            has_near_wall = False
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if (grid_x + dx, grid_y + dy) in used_grid:
                        has_near_wall = True
                        break
                if has_near_wall:
                    break
            # 只允许上下左右相邻（斜向不相邻），保证缝隙连贯
            adjacent_count = 0
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                if (grid_x + dx, grid_y + dy) in used_grid:
                    adjacent_count += 1
            if adjacent_count > 1:  # 最多与2个墙壁相邻，避免密集
                continue

            # 记录并添加墙壁
            used_grid.add((grid_x, grid_y))
            walls.append(Wall(x, y, breakable=False))
            break

    # 4. 随机生成可破坏墙壁（1格大小，数量25个）
    breakable_wall_count = random.randint(20, MAX_BREAKABLE_WALLS)

    for _ in range(breakable_wall_count):
        while True:
            grid_x = random.randint(1, (SCREEN_WIDTH - GRID_SIZE * 2) // GRID_SIZE)
            grid_y = random.randint(1, (SCREEN_HEIGHT - GRID_SIZE * 2) // GRID_SIZE)
            x = grid_x * GRID_SIZE
            y = grid_y * GRID_SIZE

            # 检查是否在出生区域内
            wall_rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
            if wall_rect.colliderect(player_spawn_area) or wall_rect.colliderect(enemy_spawn_area):
                continue

            # 检查是否已使用该网格
            if (grid_x, grid_y) in used_grid:
                continue

            # 检查间距（同固定墙）
            has_near_wall = False
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if (grid_x + dx, grid_y + dy) in used_grid:
                        has_near_wall = True
                        break
                if has_near_wall:
                    break
            adjacent_count = 0
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                if (grid_x + dx, grid_y + dy) in used_grid:
                    adjacent_count += 1
            if adjacent_count > 1:
                continue

            # 记录并添加墙壁
            used_grid.add((grid_x, grid_y))
            walls.append(Wall(x, y, breakable=True))
            break

    return walls


def create_enemies_safely(walls):
    """优化敌方坦克生成：在扩大的出生区内随机位置，每次都变"""
    enemies = []
    positions_tried = set()
    # 扩大的敌方出生区（上方大部分区域，确保随机空间）
    enemy_spawn_area = pygame.Rect(
        GRID_SIZE * 2, GRID_SIZE * 2,
        SCREEN_WIDTH - GRID_SIZE * 4, GRID_SIZE * 4
    )

    while len(enemies) < 4:
        # 在出生区内随机生成（按网格对齐，避免半格）
        grid_x = random.randint(
            enemy_spawn_area.left // GRID_SIZE,
            (enemy_spawn_area.right - TANK_SIZE) // GRID_SIZE
        )
        grid_y = random.randint(
            enemy_spawn_area.top // GRID_SIZE,
            (enemy_spawn_area.bottom - TANK_SIZE) // GRID_SIZE
        )
        x = grid_x * GRID_SIZE
        y = grid_y * GRID_SIZE

        # 检查是否重复尝试
        pos_key = (grid_x, grid_y)
        if pos_key in positions_tried:
            if len(positions_tried) > 100:
                positions_tried.clear()
            continue
        positions_tried.add(pos_key)

        # 碰撞检查
        tank_rect = pygame.Rect(x, y, TANK_SIZE, TANK_SIZE)
        collision = False

        # 与墙壁碰撞
        for wall in walls:
            if tank_rect.colliderect(wall.rect):
                collision = True
                break

        # 与其他敌方坦克碰撞
        for enemy in enemies:
            if tank_rect.colliderect(pygame.Rect(enemy.x, enemy.y, TANK_SIZE, TANK_SIZE)):
                collision = True
                break

        if not collision:
            enemies.append(Tank(x, y, COLORS['enemy'], True))

    return enemies


def spawn_powerup(walls, tanks):
    """道具生成：确保周围60x60空间"""
    while True:
        x = random.randint(50, SCREEN_WIDTH - 50)
        y = random.randint(50, SCREEN_HEIGHT - 50)

        # 1. 道具本身不重叠
        powerup_rect = pygame.Rect(x - 15, y - 15, 30, 30)
        overlap = False

        for wall in walls:
            if powerup_rect.colliderect(wall.rect):
                overlap = True
                break

        for tank in tanks:
            if powerup_rect.colliderect(pygame.Rect(tank.x, tank.y, TANK_SIZE, TANK_SIZE)):
                overlap = True
                break

        if overlap:
            continue

        # 2. 周围60x60空间无墙壁
        required_space = pygame.Rect(x - 30, y - 30, 60, 60)
        space_clear = True
        for wall in walls:
            if required_space.colliderect(wall.rect):
                space_clear = False
                break

        if space_clear:
            power_types = ["health", "speed", "invincible", "bullet_upgrade"]
            weights = [0.3, 0.25, 0.25, 0.2]
            power_type = random.choices(power_types, weights=weights)[0]
            return PowerUp(x, y, power_type)


def draw_pause_menu():
    """绘制暂停菜单"""
    pause_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    pause_surface.fill(COLORS['pause_bg'])
    screen.blit(pause_surface, (0, 0))

    title_font = get_chinese_font(48)
    title_text = title_font.render("游戏暂停", True, COLORS['pause_text'])
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
    screen.blit(title_text, title_rect)

    menu_font = get_chinese_font(24)
    options = [
        ("继续游戏", "按 P 键"),
        ("重新开始", "按 R 键"),
        ("退出游戏", "按 ESC 键")
    ]

    for i, (text, hint) in enumerate(options):
        y_pos = SCREEN_HEIGHT // 2 - 30 + i * 60
        option_text = menu_font.render(text, True, COLORS['pause_highlight'] if i == 0 else COLORS['pause_text'])
        option_rect = option_text.get_rect(center=(SCREEN_WIDTH // 2, y_pos))
        screen.blit(option_text, option_rect)
        hint_text = menu_font.render(hint, True, (150, 150, 150))
        hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2 + 200, y_pos))
        screen.blit(hint_text, hint_rect)

    pygame.display.flip()


def game_loop():
    is_paused = False
    game_running = True

    while game_running:
        # 每次重新开始生成新随机地图
        walls = create_random_map()
        # 玩家固定在下方出生区中心
        player_x = (GRID_SIZE * 2) + (GRID_SIZE * 3) - TANK_SIZE // 2
        player_y = (SCREEN_HEIGHT - GRID_SIZE * 5) + (GRID_SIZE * 1.5) - TANK_SIZE // 2
        player = Tank(player_x, player_y, COLORS['player'])
        enemies = create_enemies_safely(walls)
        all_tanks = [player] + enemies
        explosions = []
        powerups = []
        powerup_timer = 0
        damage_texts = []
        heal_texts = []

        font = get_chinese_font(28)
        small_font = get_chinese_font(16)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        is_paused = not is_paused
                        if is_paused:
                            draw_pause_menu()
                    elif event.key == pygame.K_r:
                        is_paused = False
                        break
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        exit()
                    elif event.key == pygame.K_SPACE and not is_paused:
                        player.shoot()

            if 'event' in locals() and event and event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                break

            if is_paused:
                continue

            # 玩家移动
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w]:
                player.rotate(0)
                player.move(0, -1, walls, all_tanks)
            if keys[pygame.K_s]:
                player.rotate(180)
                player.move(0, 1, walls, all_tanks)
            if keys[pygame.K_a]:
                player.rotate(270)
                player.move(-1, 0, walls, all_tanks)
            if keys[pygame.K_d]:
                player.rotate(90)
                player.move(1, 0, walls, all_tanks)

            # 敌方AI
            for tank in all_tanks:
                if tank.is_enemy and random.random() < 0.02:
                    for powerup in powerups:
                        dx = powerup.x - (tank.x + tank.width // 2)
                        dy = powerup.y - (tank.y + tank.height // 2)
                        dist = math.sqrt(dx * dx + dy * dy)
                        if dist < 200:
                            angle = math.degrees(math.atan2(dy, dx))
                            tank.rotate(angle)
                            break

            for enemy in enemies:
                if random.random() < 0.02:
                    enemy.rotate(random.choice([0, 90, 180, 270]))

                angle_rad = math.radians(enemy.rotation)
                dx = math.sin(angle_rad)
                dy = -math.cos(angle_rad)
                enemy.move(dx, dy, walls, all_tanks)

                if random.random() < 0.01:
                    enemy.shoot()

            # 更新游戏元素
            for tank in all_tanks:
                tank.update()

            # 生成道具
            powerup_timer += 1
            if powerup_timer >= 300 and len(powerups) < 3:
                powerups.append(spawn_powerup(walls, all_tanks))
                powerup_timer = 0

            # 更新文本效果
            heal_texts = [text for text in heal_texts if text.update()]
            damage_texts = [text for text in damage_texts if text.update()]

            # 道具拾取
            for powerup in powerups[:]:
                powerup.update()
                for tank in all_tanks[:]:
                    tank_rect = pygame.Rect(tank.x, tank.y, TANK_SIZE, TANK_SIZE)
                    powerup_rect = pygame.Rect(powerup.x - 15, powerup.y - 15, 30, 30)
                    if tank_rect.colliderect(powerup_rect):
                        heal_text = tank.apply_powerup(powerup.type)
                        if heal_text:
                            heal_texts.append(heal_text)
                        powerups.remove(powerup)
                        explosions.append(Explosion(powerup.x, powerup.y, 15))
                        break

            # 炮弹逻辑
            for tank in all_tanks[:]:
                for bullet in tank.bullets[:]:
                    bullet.update()
                    if bullet.is_out_of_bounds():
                        tank.bullets.remove(bullet)
                        continue

                    bullet_rect = pygame.Rect(bullet.x - bullet.radius, bullet.y - bullet.radius,
                                              bullet.radius * 2, bullet.radius * 2)

                    # 墙壁碰撞（可破坏墙移除）
                    wall_hit = False
                    for wall in walls[:]:
                        if bullet_rect.colliderect(wall.rect):
                            tank.bullets.remove(bullet)
                            explosions.append(Explosion(bullet.x, bullet.y))
                            if wall.breakable:
                                walls.remove(wall)
                            wall_hit = True
                            break
                    if wall_hit:
                        continue

                    # 坦克碰撞
                    hit_tank = False
                    for target_tank in all_tanks:
                        if target_tank == tank or bullet.is_enemy == target_tank.is_enemy:
                            continue
                        target_rect = pygame.Rect(target_tank.x, target_tank.y, TANK_SIZE, TANK_SIZE)
                        if bullet_rect.colliderect(target_rect):
                            damage_texts.append(DamageText(
                                target_tank.x + target_tank.width // 2,
                                target_tank.y,
                                bullet.damage,
                                bullet.damage_type
                            ))

                            # 闪电AOE伤害
                            if isinstance(bullet, LightningBullet):
                                for aoe_tank in all_tanks:
                                    if aoe_tank != tank and aoe_tank.is_enemy != tank.is_enemy:
                                        dx = aoe_tank.x + aoe_tank.width // 2 - bullet.x
                                        dy = aoe_tank.y + aoe_tank.height // 2 - bullet.y
                                        distance = math.sqrt(dx * dx + dy * dy)
                                        if distance < bullet.aoe_radius and aoe_tank.invincible <= 0:
                                            aoe_damage = bullet.damage // 2
                                            aoe_tank.health -= aoe_damage
                                            damage_texts.append(DamageText(
                                                aoe_tank.x + aoe_tank.width // 2,
                                                aoe_tank.y - 20,
                                                aoe_damage,
                                                "lightning"
                                            ))
                                            explosions.append(Explosion(aoe_tank.x + aoe_tank.width // 2,
                                                                        aoe_tank.y + aoe_tank.height // 2, 10))

                            if target_tank.invincible <= 0:
                                target_tank.health -= bullet.damage

                            tank.bullets.remove(bullet)
                            explosions.append(Explosion(bullet.x, bullet.y, 25))

                            if target_tank.health <= 0:
                                all_tanks.remove(target_tank)
                                if target_tank in enemies:
                                    enemies.remove(target_tank)
                                    if random.random() < 0.3:
                                        powerups.append(spawn_powerup(walls, all_tanks))
                            hit_tank = True
                            break
                    if hit_tank:
                        continue

            # 爆炸效果更新
            for explosion in explosions[:]:
                explosion.update()
                if not explosion.active:
                    explosions.remove(explosion)

            # 绘制画面
            screen.fill(COLORS['background'])

            # 绘制网格
            for x in range(0, SCREEN_WIDTH, GRID_SIZE):
                pygame.draw.line(screen, (40, 40, 50), (x, 0), (x, SCREEN_HEIGHT), 1)
            for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
                pygame.draw.line(screen, (40, 40, 50), (0, y), (SCREEN_WIDTH, y), 1)

            # 绘制游戏元素
            for wall in walls:
                wall.draw(screen)
            for powerup in powerups:
                powerup.draw(screen)
            for tank in all_tanks:
                tank.draw(screen)
                for bullet in tank.bullets:
                    bullet.draw(screen)
            for explosion in explosions:
                explosion.draw(screen)
            for damage_text in damage_texts:
                damage_text.draw(screen)
            for heal_text in heal_texts:
                heal_text.draw(screen)

            # 绘制UI
            health_text = font.render(f'生命: {player.health}', True, (0, 255, 0))
            screen.blit(health_text, (10, 10))

            weapon_names = {"normal": "普通", "lightning": "闪电", "big": "巨型"}
            weapon_text = font.render(f'武器: {weapon_names[player.bullet_type]}', True, COLORS['text'])
            screen.blit(weapon_text, (10, 45))

            enemies_text = font.render(f'敌人: {len(enemies)}', True, COLORS['enemy'])
            screen.blit(enemies_text, (SCREEN_WIDTH - 120, 10))

            # 状态效果
            effect_y = 80
            for effect in player.status_effects:
                effect.draw(screen, 10, effect_y)
                effect_y += 45

            # 控制提示
            controls_text = small_font.render('WASD移动 | 空格射击 | P暂停 | R重开 | ESC退出 | 1格坦克+墙壁', True, COLORS['text'])
            screen.blit(controls_text, (SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT - 30))

            # 武器伤害提示
            damage_info = ["普通: 25伤害", "闪电: 15+范围7", "巨型: 40伤害"]
            for i, info in enumerate(damage_info):
                info_text = small_font.render(info, True, (200, 200, 200))
                screen.blit(info_text, (SCREEN_WIDTH - 150, 40 + i * 18))

            pygame.display.flip()
            clock.tick(FPS)

            # 游戏结束
            if player.health <= 0 or len(enemies) == 0:
                end_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                end_surface.fill(COLORS['pause_bg'])
                screen.blit(end_surface, (0, 0))

                end_font = get_chinese_font(48)
                end_text = end_font.render("游戏结束!" if player.health <= 0 else "胜利!", True,
                                          (255, 0, 0) if player.health <= 0 else (0, 255, 0))
                end_rect = end_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
                screen.blit(end_text, end_rect)

                hint_font = get_chinese_font(24)
                hint_text = hint_font.render("按 R 重新开始（新地图+新敌方位置） | 按 ESC 退出", True, COLORS['pause_text'])
                hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
                screen.blit(hint_text, hint_rect)

                pygame.display.flip()

                # 等待操作
                while True:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            exit()
                        elif event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_r:
                                is_paused = False
                                break
                            elif event.key == pygame.K_ESCAPE:
                                pygame.quit()
                                exit()
                    if 'event' in locals() and event and event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                        break
                break


print("坦克大战 - 最终优化版 启动!")
print("核心优化:")
print("1. 墙壁：固定1格大小（40x40px），不再'肥胖'")
print("2. 缝隙：1格缝隙可穿过（坦克=1格，缝隙=1格）")
print("3. 敌方：每次重开在上方随机位置出生，不再固定")
print("4. 地图：墙壁分布更合理，避免密集拥堵")
print("控制说明:")
print("WASD: 移动和转向 | 空格: 发射炮弹 | P: 暂停 | R: 重开 | ESC: 退出")
print("武器类型: 普通(25伤害), 闪电(15+范围伤害), 巨型(40伤害)")

restart = True
while restart:
    restart = game_loop()

pygame.quit()