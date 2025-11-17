import pygame
import math
import random
import os

# 初始化
pygame.init()

# 游戏常量
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GRID_SIZE = 40
TANK_SIZE = 36
MIN_WALL_SPACING = 1
MAX_FIXED_WALLS = 18
MAX_BREAKABLE_WALLS = 25
GAME_TIME_LIMIT = 5 * 60 * FPS  # 5分钟游戏时限

# 游戏模式配置
GAME_MODES = {
    "人机对战": {"player_count": 1, "enemy_count": 1},
    "双人对战": {"player_count": 2, "enemy_count": 0},
    "双人+电脑": {"player_count": 2, "enemy_count": 1}
}

# 颜色定义
COLORS = {
    'background': (30, 30, 40),
    'player': (80, 160, 255),
    'player2': (255, 160, 80),
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
    'pause_highlight': (255, 200, 0),
    'menu_bg': (20, 20, 30),
    'menu_highlight': (100, 150, 255),
    'menu_text': (200, 200, 220),
    'level_text': (255, 215, 0),
    'score_text': (100, 255, 100),
    'mouse_aim': (255, 100, 100, 150),
    'mouse_cursor': (255, 255, 255),
    'button_normal': (80, 80, 120),
    'button_hover': (100, 100, 160),
    'button_click': (120, 120, 200),
}

# 创建窗口
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("坦克大战 - 多模式对战版")
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


class Tank:
    def __init__(self, x, y, color, is_enemy=False, is_player2=False):
        self.x = x
        self.y = y
        self.color = color
        self.width = TANK_SIZE
        self.height = TANK_SIZE
        self.speed = 3
        self.base_speed = 3
        self.rotation = 0
        self.cooldown = 0
        self.cooldown_time = 20
        self.health = 100
        self.max_health = 100
        self.is_enemy = is_enemy
        self.is_player2 = is_player2
        self.bullets = []
        self.bullet_type = "normal"
        self.invincible = 0
        self.speed_boost = 0
        self.bullet_timer = 0
        self.status_effects = []
        self.thruster_timer = 0
        self.effect_particles = []
        # 双人模式下都使用键盘控制
        self.mouse_control = not is_enemy and not is_player2
        self.keyboard_control = not is_enemy

        # 敌人特定属性
        if is_enemy:
            self.health = 120
            self.max_health = 120
            self.enemy_damage = 30
            self.ai_timer = 0
            self.target_angle = 0
            self.move_timer = 0
            self.shoot_cooldown = random.randint(30, 90)

    def move(self, dx, dy, walls, tanks):
        current_speed = self.speed
        if self.speed_boost > 0:
            current_speed = self.base_speed * 1.5

        new_x = self.x + dx * current_speed
        new_y = self.y + dy * current_speed

        # 边界检查
        if new_x < 20 or new_x > SCREEN_WIDTH - self.width - 20:
            return False
        if new_y < 20 or new_y > SCREEN_HEIGHT - self.height - 20:
            return False

        new_rect = pygame.Rect(new_x, new_y, self.width, self.height)

        # 墙壁碰撞检查
        for wall in walls:
            if new_rect.colliderect(wall.rect):
                return False

        # 坦克之间碰撞检查（只检查存活的坦克）
        for tank in tanks:
            if tank != self and tank.health > 0 and new_rect.colliderect(
                    pygame.Rect(tank.x, tank.y, tank.width, tank.height)):
                return False

        self.x = new_x
        self.y = new_y

        if dx != 0 or dy != 0:
            self.thruster_timer = (self.thruster_timer + 1) % 10

        return True

    def rotate(self, angle):
        self.rotation = angle

    def update_mouse_rotation(self, mouse_pos):
        """根据鼠标位置更新坦克朝向"""
        if not self.mouse_control:
            return

        tank_center_x = self.x + self.width // 2
        tank_center_y = self.y + self.height // 2

        mouse_x, mouse_y = mouse_pos
        dx = mouse_x - tank_center_x
        dy = mouse_y - tank_center_y

        # 计算角度
        angle = math.degrees(math.atan2(dx, -dy)) % 360
        self.rotation = angle

    def mouse_shoot(self):
        """鼠标射击"""
        if self.mouse_control and self.cooldown <= 0:
            return self.shoot()
        return False

    def rotate_towards(self, target_x, target_y, speed=2):
        """平滑转向目标"""
        dx = target_x - (self.x + self.width // 2)
        dy = target_y - (self.y + self.height // 2)
        target_angle = math.degrees(math.atan2(dx, dy)) % 360

        # 计算角度差
        angle_diff = (target_angle - self.rotation) % 360
        if angle_diff > 180:
            angle_diff -= 360

        # 平滑转向
        if abs(angle_diff) > speed:
            if angle_diff > 0:
                self.rotation = (self.rotation + speed) % 360
            else:
                self.rotation = (self.rotation - speed) % 360
        else:
            self.rotation = target_angle

        return abs(angle_diff) < 10

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

    def update_ai(self, players, walls, tanks):
        """增强的AI逻辑"""
        if not self.is_enemy:
            return

        self.ai_timer += 1
        self.move_timer -= 1

        # 找到最近的玩家
        closest_player = None
        min_distance = float('inf')

        for player in players:
            if player.health <= 0:
                continue

            player_center_x = player.x + player.width // 2
            player_center_y = player.y + player.height // 2
            self_center_x = self.x + self.width // 2
            self_center_y = self.y + self.height // 2

            dx = player_center_x - self_center_x
            dy = player_center_y - self_center_y
            distance = math.sqrt(dx * dx + dy * dy)

            if distance < min_distance:
                min_distance = distance
                closest_player = player

        if not closest_player:
            return

        player_center_x = closest_player.x + closest_player.width // 2
        player_center_y = closest_player.y + closest_player.height // 2
        self_center_x = self.x + self.width // 2
        self_center_y = self.y + self.height // 2

        dx = player_center_x - self_center_x
        dy = player_center_y - self_center_y
        distance = math.sqrt(dx * dx + dy * dy)

        # AI行为决策
        if distance < 200:  # 近距离：攻击
            # 转向玩家
            self.rotate_towards(player_center_x, player_center_y, 3)

            # 射击
            if distance < 250 and random.random() < 0.02:
                self.shoot()

            # 保持距离
            if distance < 100 and self.move_timer <= 0:
                # 后退
                angle_rad = math.radians(self.rotation)
                move_success = self.move(-math.sin(angle_rad), math.cos(angle_rad), walls, tanks)
                if not move_success:
                    # 如果后退失败，尝试侧移
                    side_angle = self.rotation + 90
                    angle_rad = math.radians(side_angle)
                    self.move(math.sin(angle_rad), -math.cos(angle_rad), walls, tanks)
                self.move_timer = 30

        else:  # 远距离：寻找玩家
            if self.move_timer <= 0:
                # 转向玩家方向移动
                self.rotate_towards(player_center_x, player_center_y, 2)
                angle_rad = math.radians(self.rotation)
                move_success = self.move(math.sin(angle_rad), -math.cos(angle_rad), walls, tanks)

                if not move_success:
                    # 如果移动失败，随机转向
                    self.rotation = random.choice([0, 90, 180, 270])
                    self.move_timer = 60
                else:
                    self.move_timer = 20

            # 偶尔射击
            if random.random() < 0.005:
                self.shoot()

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
        # 只绘制存活的坦克
        if self.health <= 0:
            return

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
        bar_height = 5
        fill = (self.health / self.max_health) * bar_width
        outline_rect = pygame.Rect(self.x, self.y - 10, bar_width, bar_height)
        fill_rect = pygame.Rect(self.x, self.y - 10, fill, bar_height)
        pygame.draw.rect(surface, (100, 100, 100), outline_rect)

        # 生命值颜色根据血量变化
        health_color = (0, 255, 0)  # 绿色
        if self.health < self.max_health * 0.3:
            health_color = (255, 0, 0)  # 红色
        elif self.health < self.max_health * 0.6:
            health_color = (255, 255, 0)  # 黄色

        pygame.draw.rect(surface, health_color, fill_rect)

    def draw_thruster(self, surface):
        angle_rad = math.radians(self.rotation)

        thruster_x = self.x + self.width // 2 - math.sin(angle_rad) * 25
        thruster_y = self.y + self.height // 2 + math.cos(angle_rad) * 25

        flame_size = 8 + (self.thruster_timer // 2)

        pygame.draw.circle(surface, (255, 255, 0), (int(thruster_x), int(thruster_y)), flame_size - 4)
        pygame.draw.circle(surface, (255, 150, 0), (int(thruster_x), int(thruster_y)), flame_size - 2)
        pygame.draw.circle(surface, (255, 50, 0), (int(thruster_x), int(thruster_y)), flame_size)

    def draw_aim_line(self, surface, mouse_pos):
        """绘制鼠标瞄准线"""
        if not self.mouse_control:
            return

        tank_center_x = self.x + self.width // 2
        tank_center_y = self.y + self.height // 2

        # 绘制从坦克到鼠标的瞄准线
        pygame.draw.line(surface, COLORS['mouse_aim'],
                         (tank_center_x, tank_center_y), mouse_pos, 2)

        # 在鼠标位置绘制准星
        cross_size = 8
        pygame.draw.line(surface, COLORS['mouse_cursor'],
                         (mouse_pos[0] - cross_size, mouse_pos[1]),
                         (mouse_pos[0] + cross_size, mouse_pos[1]), 2)
        pygame.draw.line(surface, COLORS['mouse_cursor'],
                         (mouse_pos[0], mouse_pos[1] - cross_size),
                         (mouse_pos[0], mouse_pos[1] + cross_size), 2)

        # 绘制射击范围圆环
        pygame.draw.circle(surface, COLORS['mouse_aim'], mouse_pos, 20, 1)


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

    # 2. 定义出生区域
    player_spawn_area = pygame.Rect(
        GRID_SIZE * 2, SCREEN_HEIGHT - GRID_SIZE * 5,
        GRID_SIZE * 6, GRID_SIZE * 3
    )
    enemy_spawn_area = pygame.Rect(
        GRID_SIZE * 2, GRID_SIZE * 2,
        GRID_SIZE * 15, GRID_SIZE * 4
    )

    # 3. 随机生成固定墙壁
    fixed_wall_count = random.randint(15, MAX_FIXED_WALLS)
    used_grid = set()

    for _ in range(fixed_wall_count):
        while True:
            grid_x = random.randint(1, (SCREEN_WIDTH - GRID_SIZE * 2) // GRID_SIZE)
            grid_y = random.randint(1, (SCREEN_HEIGHT - GRID_SIZE * 2) // GRID_SIZE)
            x = grid_x * GRID_SIZE
            y = grid_y * GRID_SIZE

            wall_rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
            if wall_rect.colliderect(player_spawn_area) or wall_rect.colliderect(enemy_spawn_area):
                continue

            if (grid_x, grid_y) in used_grid:
                continue

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

            used_grid.add((grid_x, grid_y))
            walls.append(Wall(x, y, breakable=False))
            break

    # 4. 随机生成可破坏墙壁
    breakable_wall_count = random.randint(20, MAX_BREAKABLE_WALLS)

    for _ in range(breakable_wall_count):
        while True:
            grid_x = random.randint(1, (SCREEN_WIDTH - GRID_SIZE * 2) // GRID_SIZE)
            grid_y = random.randint(1, (SCREEN_HEIGHT - GRID_SIZE * 2) // GRID_SIZE)
            x = grid_x * GRID_SIZE
            y = grid_y * GRID_SIZE

            wall_rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
            if wall_rect.colliderect(player_spawn_area) or wall_rect.colliderect(enemy_spawn_area):
                continue

            if (grid_x, grid_y) in used_grid:
                continue

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

            used_grid.add((grid_x, grid_y))
            walls.append(Wall(x, y, breakable=True))
            break

    return walls


def create_tanks_safely(walls, game_mode):
    """根据游戏模式创建坦克"""
    tanks = []
    positions_tried = set()

    mode_config = GAME_MODES[game_mode]
    player_count = mode_config["player_count"]
    enemy_count = mode_config["enemy_count"]

    # 玩家1出生区域
    player1_spawn_area = pygame.Rect(
        GRID_SIZE * 2, SCREEN_HEIGHT - GRID_SIZE * 5,
        GRID_SIZE * 6, GRID_SIZE * 3
    )

    # 玩家2出生区域（左上角）
    player2_spawn_area = pygame.Rect(
        GRID_SIZE * 2, GRID_SIZE * 2,
        GRID_SIZE * 6, GRID_SIZE * 3
    )

    # 敌人出生区域（右上角）
    enemy_spawn_area = pygame.Rect(
        SCREEN_WIDTH - GRID_SIZE * 8, GRID_SIZE * 2,
        GRID_SIZE * 6, GRID_SIZE * 3
    )

    # 创建玩家1
    if player_count >= 1:
        while True:
            grid_x = random.randint(
                player1_spawn_area.left // GRID_SIZE,
                (player1_spawn_area.right - TANK_SIZE) // GRID_SIZE
            )
            grid_y = random.randint(
                player1_spawn_area.top // GRID_SIZE,
                (player1_spawn_area.bottom - TANK_SIZE) // GRID_SIZE
            )
            x = grid_x * GRID_SIZE
            y = grid_y * GRID_SIZE

            pos_key = (grid_x, grid_y)
            if pos_key in positions_tried:
                if len(positions_tried) > 100:
                    positions_tried.clear()
                continue
            positions_tried.add(pos_key)

            tank_rect = pygame.Rect(x, y, TANK_SIZE, TANK_SIZE)
            collision = False

            for wall in walls:
                if tank_rect.colliderect(wall.rect):
                    collision = True
                    break

            for tank in tanks:
                if tank_rect.colliderect(pygame.Rect(tank.x, tank.y, TANK_SIZE, TANK_SIZE)):
                    collision = True
                    break

            if not collision:
                tanks.append(Tank(x, y, COLORS['player']))
                break

    # 创建玩家2
    if player_count >= 2:
        while True:
            grid_x = random.randint(
                player2_spawn_area.left // GRID_SIZE,
                (player2_spawn_area.right - TANK_SIZE) // GRID_SIZE
            )
            grid_y = random.randint(
                player2_spawn_area.top // GRID_SIZE,
                (player2_spawn_area.bottom - TANK_SIZE) // GRID_SIZE
            )
            x = grid_x * GRID_SIZE
            y = grid_y * GRID_SIZE

            pos_key = (grid_x, grid_y)
            if pos_key in positions_tried:
                if len(positions_tried) > 100:
                    positions_tried.clear()
                continue
            positions_tried.add(pos_key)

            tank_rect = pygame.Rect(x, y, TANK_SIZE, TANK_SIZE)
            collision = False

            for wall in walls:
                if tank_rect.colliderect(wall.rect):
                    collision = True
                    break

            for tank in tanks:
                if tank_rect.colliderect(pygame.Rect(tank.x, tank.y, TANK_SIZE, TANK_SIZE)):
                    collision = True
                    break

            if not collision:
                tanks.append(Tank(x, y, COLORS['player2'], is_player2=True))
                break

    # 创建敌人
    for _ in range(enemy_count):
        while True:
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

            pos_key = (grid_x, grid_y)
            if pos_key in positions_tried:
                if len(positions_tried) > 100:
                    positions_tried.clear()
                continue
            positions_tried.add(pos_key)

            tank_rect = pygame.Rect(x, y, TANK_SIZE, TANK_SIZE)
            collision = False

            for wall in walls:
                if tank_rect.colliderect(wall.rect):
                    collision = True
                    break

            for tank in tanks:
                if tank_rect.colliderect(pygame.Rect(tank.x, tank.y, TANK_SIZE, TANK_SIZE)):
                    collision = True
                    break

            if not collision:
                tanks.append(Tank(x, y, COLORS['enemy'], is_enemy=True))
                break

    return tanks


def spawn_powerup(walls, tanks):
    """道具生成：确保周围60x60空间"""
    while True:
        x = random.randint(50, SCREEN_WIDTH - 50)
        y = random.randint(50, SCREEN_HEIGHT - 50)

        powerup_rect = pygame.Rect(x - 15, y - 15, 30, 30)
        overlap = False

        for wall in walls:
            if powerup_rect.colliderect(wall.rect):
                overlap = True
                break

        for tank in tanks:
            if tank.health > 0 and powerup_rect.colliderect(pygame.Rect(tank.x, tank.y, TANK_SIZE, TANK_SIZE)):
                overlap = True
                break

        if overlap:
            continue

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


def draw_pause_menu(surface):
    """绘制暂停菜单"""
    pause_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    pause_surface.fill(COLORS['pause_bg'])
    surface.blit(pause_surface, (0, 0))

    title_font = get_chinese_font(48)
    title_text = title_font.render("游戏暂停", True, COLORS['pause_text'])
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
    surface.blit(title_text, title_rect)

    menu_font = get_chinese_font(24)
    options = [
        ("继续游戏", "按 P 键"),
        ("重新开始", "按 R 键"),
        ("返回主菜单", "按 ESC 键")
    ]

    for i, (text, hint) in enumerate(options):
        y_pos = SCREEN_HEIGHT // 2 - 30 + i * 60
        option_text = menu_font.render(text, True, COLORS['pause_highlight'] if i == 0 else COLORS['pause_text'])
        option_rect = option_text.get_rect(center=(SCREEN_WIDTH // 2, y_pos))
        surface.blit(option_text, option_rect)
        hint_text = menu_font.render(hint, True, (150, 150, 150))
        hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2 + 200, y_pos))
        surface.blit(hint_text, hint_rect)

    pygame.display.flip()


class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.selected_option = 0
        self.main_options = ["开始游戏", "游戏说明", "退出游戏"]
        self.mode_options = ["人机对战", "双人对战", "双人+电脑", "返回主菜单"]
        self.current_menu = "main"  # "main" 或 "mode"
        self.in_instructions = False

        # 鼠标交互相关
        self.buttons = []
        self.update_buttons()

    def update_buttons(self):
        """更新按钮位置和大小"""
        self.buttons = []

        if self.in_instructions:
            # 说明页面只有一个返回按钮
            back_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 80, 200, 40)
            self.buttons.append(back_button)
        elif self.current_menu == "main":
            # 主菜单按钮
            for i, option in enumerate(self.main_options):
                button_rect = pygame.Rect(
                    SCREEN_WIDTH // 2 - 100,
                    SCREEN_HEIGHT // 2 + i * 60 - 20,
                    200, 40
                )
                self.buttons.append(button_rect)
        else:
            # 模式选择菜单按钮
            for i, option in enumerate(self.mode_options):
                button_rect = pygame.Rect(
                    SCREEN_WIDTH // 2 - 100,
                    SCREEN_HEIGHT // 2 + i * 60 - 20,
                    200, 40
                )
                self.buttons.append(button_rect)

    def check_button_hover(self, mouse_pos):
        """检查鼠标悬停的按钮"""
        for i, button in enumerate(self.buttons):
            if button.collidepoint(mouse_pos):
                self.selected_option = i
                return True
        return False

    def draw_main_menu(self):
        """绘制主菜单"""
        self.screen.fill(COLORS['menu_bg'])

        # 标题
        title_font = get_chinese_font(64)
        title_text = title_font.render("坦克大战", True, COLORS['menu_highlight'])
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
        self.screen.blit(title_text, title_rect)

        # 版本信息
        version_font = get_chinese_font(18)
        version_text = version_font.render("多模式对战版 - 支持鼠标控制", True, COLORS['menu_text'])
        version_rect = version_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4 + 60))
        self.screen.blit(version_text, version_rect)

        # 菜单选项（带按钮效果）
        menu_font = get_chinese_font(36)
        for i, option in enumerate(self.main_options):
            # 按钮背景
            button_color = COLORS['button_hover'] if i == self.selected_option else COLORS['button_normal']
            pygame.draw.rect(self.screen, button_color, self.buttons[i], border_radius=10)
            pygame.draw.rect(self.screen, COLORS['menu_highlight'], self.buttons[i], 2, border_radius=10)

            # 按钮文字
            color = COLORS['menu_highlight'] if i == self.selected_option else COLORS['menu_text']
            option_text = menu_font.render(option, True, color)
            option_rect = option_text.get_rect(center=self.buttons[i].center)
            self.screen.blit(option_text, option_rect)

        # 控制提示
        hint_font = get_chinese_font(16)
        hint_text = hint_font.render("使用鼠标点击选择 | ESC 退出", True, (150, 150, 150))
        hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        self.screen.blit(hint_text, hint_rect)

        pygame.display.flip()

    def draw_mode_menu(self):
        """绘制模式选择菜单"""
        self.screen.fill(COLORS['menu_bg'])

        # 标题
        title_font = get_chinese_font(48)
        title_text = title_font.render("选择游戏模式", True, COLORS['menu_highlight'])
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 6))
        self.screen.blit(title_text, title_rect)

        # 模式说明
        info_font = get_chinese_font(16)
        mode_descriptions = [
            "人机对战: 1名玩家 vs 1名电脑",
            "双人对战: 2名玩家对战",
            "双人+电脑: 2名玩家 vs 1名电脑"
        ]

        for i, desc in enumerate(mode_descriptions):
            desc_text = info_font.render(desc, True, COLORS['menu_text'])
            desc_rect = desc_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 + i * 25))
            self.screen.blit(desc_text, desc_rect)

        # 模式选项（带按钮效果）
        menu_font = get_chinese_font(36)
        for i, option in enumerate(self.mode_options):
            # 按钮背景
            button_color = COLORS['button_hover'] if i == self.selected_option else COLORS['button_normal']
            pygame.draw.rect(self.screen, button_color, self.buttons[i], border_radius=10)
            pygame.draw.rect(self.screen, COLORS['menu_highlight'], self.buttons[i], 2, border_radius=10)

            # 按钮文字
            color = COLORS['menu_highlight'] if i == self.selected_option else COLORS['menu_text']
            option_text = menu_font.render(option, True, color)
            option_rect = option_text.get_rect(center=self.buttons[i].center)
            self.screen.blit(option_text, option_rect)

        # 控制提示
        hint_font = get_chinese_font(16)
        hint_text = hint_font.render("使用鼠标点击选择模式 | ESC 返回", True, (150, 150, 150))
        hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        self.screen.blit(hint_text, hint_rect)

        pygame.display.flip()

    def draw_instructions(self):
        """绘制游戏说明"""
        self.screen.fill(COLORS['menu_bg'])

        # 标题
        title_font = get_chinese_font(48)
        title_text = title_font.render("游戏说明", True, COLORS['menu_highlight'])
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(title_text, title_rect)

        # 游戏说明 - 分成两列
        content_font = get_chinese_font(20)
        left_instructions = [
            "控制方式:",
            "玩家1 (蓝色):",
            "  WASD - 移动坦克和转向",
            "  空格键 - 发射炮弹",
            "",
            "通用控制:",
            "  P - 暂停游戏",
            "  R - 重新开始",
            "  ESC - 返回菜单",

        ]

        right_instructions = [
            "玩家2 (橙色):",
            "  方向键 - 移动坦克和转向",
            "  右Ctrl - 发射炮弹",
            "",

            "游戏规则:",
            "最后存活的坦克获胜",
            "5分钟时限，时间到按血量判定",
            "收集道具获得特殊能力",
            "避开炮弹，保护自己"
        ]

        # 左列
        for i, line in enumerate(left_instructions):
            text = content_font.render(line, True, COLORS['menu_text'])
            text_rect = text.get_rect(midleft=(SCREEN_WIDTH // 4 - 50, 150 + i * 30))
            self.screen.blit(text, text_rect)

        # 右列
        for i, line in enumerate(right_instructions):
            text = content_font.render(line, True, COLORS['menu_text'])
            text_rect = text.get_rect(midleft=(SCREEN_WIDTH // 2 + 50, 150 + i * 30))
            self.screen.blit(text, text_rect)


        # 返回按钮 - 添加鼠标悬停效果
        back_button = self.buttons[0]
        mouse_pos = pygame.mouse.get_pos()

        # 检查鼠标是否悬停在返回按钮上
        is_hovered = back_button.collidepoint(mouse_pos)

        # 根据悬停状态选择颜色
        button_color = COLORS['button_hover'] if is_hovered else COLORS['button_normal']
        text_color = COLORS['menu_highlight'] if is_hovered else COLORS['menu_text']

        pygame.draw.rect(self.screen, button_color, back_button, border_radius=10)
        pygame.draw.rect(self.screen, COLORS['menu_highlight'], back_button, 2, border_radius=10)

        back_font = get_chinese_font(24)
        back_text = back_font.render("返回主菜单", True, text_color)  # 使用动态文字颜色
        back_rect = back_text.get_rect(center=back_button.center)
        self.screen.blit(back_text, back_rect)

        pygame.display.flip()


    def run(self):
        """运行菜单系统"""
        running = True
        selected_mode = None

        while running:
            mouse_pos = pygame.mouse.get_pos()

            # 检查鼠标悬停
            self.check_button_hover(mouse_pos)

            if self.in_instructions:
                self.draw_instructions()
            elif self.current_menu == "main":
                self.draw_main_menu()
            else:
                self.draw_mode_menu()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.in_instructions:
                            self.in_instructions = False
                            self.current_menu = "main"
                            self.selected_option = 0
                            self.update_buttons()
                        elif self.current_menu == "mode":
                            self.current_menu = "main"
                            self.selected_option = 0
                            self.update_buttons()
                        else:
                            return "quit"

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # 左键点击
                        for i, button in enumerate(self.buttons):
                            if button.collidepoint(mouse_pos):
                                if self.in_instructions:
                                    self.in_instructions = False
                                    self.current_menu = "main"
                                    self.selected_option = 0
                                    self.update_buttons()
                                elif self.current_menu == "main":
                                    if i == 0:  # 开始游戏
                                        self.current_menu = "mode"
                                        self.selected_option = 0
                                        self.update_buttons()
                                    elif i == 1:  # 游戏说明
                                        self.in_instructions = True
                                        self.selected_option = 0
                                        self.update_buttons()
                                    elif i == 2:  # 退出游戏
                                        return "quit"
                                else:  # 模式选择菜单
                                    if i == 0:  # 人机对战
                                        selected_mode = "人机对战"
                                        running = False
                                    elif i == 1:  # 双人对战
                                        selected_mode = "双人对战"
                                        running = False
                                    elif i == 2:  # 双人+电脑
                                        selected_mode = "双人+电脑"
                                        running = False
                                    elif i == 3:  # 返回主菜单
                                        self.current_menu = "main"
                                        self.selected_option = 0
                                        self.update_buttons()

            self.clock.tick(FPS)

        return selected_mode


class Game:
    def __init__(self):
        self.screen = screen
        self.clock = clock
        self.is_paused = False
        self.game_running = True
        self.menu = Menu(self.screen)
        self.game_mode = None
        self.game_state = "menu"
        self.time_remaining = GAME_TIME_LIMIT

        # 鼠标控制相关
        self.mouse_control = True
        self.show_mouse_aim = True
        self.mouse_pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

    def reset_game(self, game_mode):
        """重置游戏状态"""
        self.game_mode = game_mode
        self.walls = create_random_map()
        self.tanks = create_tanks_safely(self.walls, game_mode)
        self.time_remaining = GAME_TIME_LIMIT

        # 分离玩家和敌人
        self.players = [tank for tank in self.tanks if not tank.is_enemy]
        self.enemies = [tank for tank in self.tanks if tank.is_enemy]

        # 设置控制方式
        if len(self.players) > 0:
            # 人机对战：玩家1使用鼠标控制
            # 双人对战和双人+电脑：都使用键盘控制
            if game_mode == "人机对战":
                self.players[0].mouse_control = True
                self.players[0].keyboard_control = False
            else:
                self.players[0].mouse_control = False
                self.players[0].keyboard_control = True

        # 设置玩家2为键盘控制
        if len(self.players) > 1:
            self.players[1].mouse_control = False
            self.players[1].keyboard_control = True

        self.explosions = []
        self.powerups = []
        self.powerup_timer = 0
        self.damage_texts = []
        self.heal_texts = []

        self.font = get_chinese_font(28)
        self.small_font = get_chinese_font(16)

    def handle_events(self):
        """处理游戏事件"""
        # 更新鼠标位置
        self.mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p and self.game_state == "playing":
                    self.is_paused = not self.is_paused
                    if self.is_paused:
                        draw_pause_menu(self.screen)
                elif event.key == pygame.K_r and self.game_state == "playing":
                    return "restart"
                elif event.key == pygame.K_ESCAPE:
                    if self.game_state == "playing":
                        self.game_state = "menu"
                        return "menu"
                    else:
                        return False
                elif event.key == pygame.K_SPACE and self.game_state == "playing" and not self.is_paused:
                    # 玩家1射击
                    if len(self.players) > 0 and self.players[0].health > 0:
                        self.players[0].shoot()
                elif event.key == pygame.K_RCTRL and self.game_state == "playing" and not self.is_paused:
                    # 玩家2射击
                    if len(self.players) > 1 and self.players[1].health > 0:
                        self.players[1].shoot()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.game_state == "playing" and not self.is_paused:
                    if event.button == 1:  # 左键射击
                        if (self.mouse_control and len(self.players) > 0 and
                                self.players[0].health > 0 and self.players[0].mouse_control):
                            self.players[0].mouse_shoot()
                    elif event.button == 3:  # 右键切换瞄准线显示
                        self.show_mouse_aim = not self.show_mouse_aim
                elif self.game_state == "game_over":
                    # 在结束画面点击开始新游戏
                    return "restart"

        return True

    def update_player_movement(self):
        """更新玩家移动"""
        keys = pygame.key.get_pressed()

        # 玩家1移动
        if len(self.players) > 0 and self.players[0].health > 0:
            player1 = self.players[0]

            if player1.mouse_control:
                # 鼠标控制：用鼠标瞄准，键盘移动
                player1.update_mouse_rotation(self.mouse_pos)

                # 键盘移动
                if keys[pygame.K_w]:
                    player1.move(0, -1, self.walls, self.tanks)
                if keys[pygame.K_s]:
                    player1.move(0, 1, self.walls, self.tanks)
                if keys[pygame.K_a]:
                    player1.move(-1, 0, self.walls, self.tanks)
                if keys[pygame.K_d]:
                    player1.move(1, 0, self.walls, self.tanks)
            else:
                # 纯键盘控制
                if keys[pygame.K_w]:
                    player1.rotate(0)
                    player1.move(0, -1, self.walls, self.tanks)
                if keys[pygame.K_s]:
                    player1.rotate(180)
                    player1.move(0, 1, self.walls, self.tanks)
                if keys[pygame.K_a]:
                    player1.rotate(270)
                    player1.move(-1, 0, self.walls, self.tanks)
                if keys[pygame.K_d]:
                    player1.rotate(90)
                    player1.move(1, 0, self.walls, self.tanks)

        # 玩家2移动（纯键盘控制）
        if len(self.players) > 1 and self.players[1].health > 0:
            player2 = self.players[1]
            if keys[pygame.K_UP]:
                player2.rotate(0)
                player2.move(0, -1, self.walls, self.tanks)
            if keys[pygame.K_DOWN]:
                player2.rotate(180)
                player2.move(0, 1, self.walls, self.tanks)
            if keys[pygame.K_LEFT]:
                player2.rotate(270)
                player2.move(-1, 0, self.walls, self.tanks)
            if keys[pygame.K_RIGHT]:
                player2.rotate(90)
                player2.move(1, 0, self.walls, self.tanks)

    def update_enemy_ai(self):
        """更新敌人AI"""
        for enemy in self.enemies:
            if enemy.health > 0:
                enemy.update_ai(self.players, self.walls, self.tanks)

    def update_powerups(self):
        """更新道具"""
        self.powerup_timer += 1
        if self.powerup_timer >= 300 and len(self.powerups) < 3:
            self.powerups.append(spawn_powerup(self.walls, self.tanks))
            self.powerup_timer = 0

    def handle_powerup_collisions(self):
        """处理道具碰撞"""
        for powerup in self.powerups[:]:
            powerup.update()
            for tank in self.tanks[:]:
                if tank.health <= 0:
                    continue

                tank_rect = pygame.Rect(tank.x, tank.y, TANK_SIZE, TANK_SIZE)
                powerup_rect = pygame.Rect(powerup.x - 15, powerup.y - 15, 30, 30)
                if tank_rect.colliderect(powerup_rect):
                    heal_text = tank.apply_powerup(powerup.type)
                    if heal_text:
                        self.heal_texts.append(heal_text)
                    self.powerups.remove(powerup)
                    self.explosions.append(Explosion(powerup.x, powerup.y, 15))
                    break

    def handle_bullet_collisions(self):
        """处理子弹碰撞"""
        for tank in self.tanks[:]:
            for bullet in tank.bullets[:]:
                bullet.update()
                if bullet.is_out_of_bounds():
                    tank.bullets.remove(bullet)
                    continue

                bullet_rect = pygame.Rect(bullet.x - bullet.radius, bullet.y - bullet.radius,
                                          bullet.radius * 2, bullet.radius * 2)

                # 墙壁碰撞
                wall_hit = False
                for wall in self.walls[:]:
                    if bullet_rect.colliderect(wall.rect):
                        tank.bullets.remove(bullet)
                        self.explosions.append(Explosion(bullet.x, bullet.y))
                        if wall.breakable:
                            self.walls.remove(wall)
                        wall_hit = True
                        break
                if wall_hit:
                    continue

                # 坦克碰撞
                self.handle_tank_bullet_collision(tank, bullet, bullet_rect)

    def handle_tank_bullet_collision(self, tank, bullet, bullet_rect):
        """处理坦克与子弹碰撞"""
        for target_tank in self.tanks:
            if target_tank.health <= 0:
                continue

            # 不能打自己，同队不能互相伤害
            if target_tank == tank:
                continue
            if bullet.is_enemy == target_tank.is_enemy and not target_tank.is_enemy:
                # 玩家之间可以互相伤害
                pass
            elif bullet.is_enemy == target_tank.is_enemy:
                # 敌人之间不能互相伤害
                continue

            target_rect = pygame.Rect(target_tank.x, target_tank.y, TANK_SIZE, TANK_SIZE)
            if bullet_rect.colliderect(target_rect):
                self.damage_texts.append(DamageText(
                    target_tank.x + target_tank.width // 2,
                    target_tank.y,
                    bullet.damage,
                    bullet.damage_type
                ))

                # 闪电AOE伤害
                if hasattr(bullet, 'aoe_radius'):
                    self.handle_lightning_aoe(tank, bullet, target_tank)

                if target_tank.invincible <= 0:
                    target_tank.health -= bullet.damage

                tank.bullets.remove(bullet)
                self.explosions.append(Explosion(bullet.x, bullet.y, 25))

                if target_tank.health <= 0:
                    # 坦克死亡，从列表中移除
                    self.explosions.append(Explosion(
                        target_tank.x + target_tank.width // 2,
                        target_tank.y + target_tank.height // 2, 40
                    ))
                return True
        return False

    def handle_lightning_aoe(self, tank, bullet, original_target):
        """处理闪电AOE伤害"""
        for aoe_tank in self.tanks:
            if aoe_tank.health <= 0:
                continue
            if aoe_tank != tank and aoe_tank != original_target:
                dx = aoe_tank.x + aoe_tank.width // 2 - bullet.x
                dy = aoe_tank.y + aoe_tank.height // 2 - bullet.y
                distance = math.sqrt(dx * dx + dy * dy)
                if distance < bullet.aoe_radius and aoe_tank.invincible <= 0:
                    aoe_damage = bullet.damage // 2
                    aoe_tank.health -= aoe_damage
                    self.damage_texts.append(DamageText(
                        aoe_tank.x + aoe_tank.width // 2,
                        aoe_tank.y - 20,
                        aoe_damage,
                        "lightning"
                    ))
                    self.explosions.append(Explosion(aoe_tank.x + aoe_tank.width // 2,
                                                     aoe_tank.y + aoe_tank.height // 2, 10))

    def draw_game(self):
        """绘制游戏画面"""
        self.screen.fill(COLORS['background'])

        # 绘制网格
        self.draw_grid()

        # 绘制游戏元素
        for wall in self.walls:
            wall.draw(self.screen)
        for powerup in self.powerups:
            powerup.draw(self.screen)
        for tank in self.tanks:
            if tank.health > 0:
                tank.draw(self.screen)
            for bullet in tank.bullets:
                bullet.draw(self.screen)
        for explosion in self.explosions:
            explosion.draw(self.screen)
        for damage_text in self.damage_texts:
            damage_text.draw(self.screen)
        for heal_text in self.heal_texts:
            heal_text.draw(self.screen)

        # 绘制鼠标瞄准线
        if (self.mouse_control and self.show_mouse_aim and self.game_state == "playing" and
                len(self.players) > 0 and self.players[0].health > 0 and self.players[0].mouse_control):
            self.players[0].draw_aim_line(self.screen, self.mouse_pos)

        # 绘制UI
        self.draw_ui()

    def draw_grid(self):
        """绘制背景网格"""
        for x in range(0, SCREEN_WIDTH, GRID_SIZE):
            pygame.draw.line(self.screen, (40, 40, 50), (x, 0), (x, SCREEN_HEIGHT), 1)
        for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
            pygame.draw.line(self.screen, (40, 40, 50), (0, y), (SCREEN_WIDTH, y), 1)

    def draw_ui(self):
        """绘制用户界面"""
        # 游戏模式
        mode_text = self.font.render(f'模式: {self.game_mode}', True, COLORS['text'])
        self.screen.blit(mode_text, (10, 10))

        # 玩家1生命值
        if len(self.players) > 0:
            health_color = (0, 255, 0) if self.players[0].health > 0 else (150, 150, 150)
            health_text = self.font.render(f'玩家1: {self.players[0].health}', True, health_color)
            self.screen.blit(health_text, (10, 45))

        # 玩家2生命值
        if len(self.players) > 1:
            health_color = (255, 165, 0) if self.players[1].health > 0 else (150, 150, 150)
            health_text = self.font.render(f'玩家2: {self.players[1].health}', True, health_color)
            self.screen.blit(health_text, (10, 80))

        # 时间显示（移到右上角）
        minutes = self.time_remaining // (60 * FPS)
        seconds = (self.time_remaining % (60 * FPS)) // FPS
        time_text = self.font.render(f'时间: {minutes:02d}:{seconds:02d}', True, COLORS['text'])
        self.screen.blit(time_text, (SCREEN_WIDTH - 180, 10))

        # 状态效果
        effect_y = 110
        if len(self.players) > 0 and self.players[0].health > 0:
            for effect in self.players[0].status_effects:
                effect.draw(self.screen, 10, effect_y)
                effect_y += 45

        # 控制提示
        if len(self.players) > 0 and self.players[0].health > 0 and self.players[0].mouse_control:
            controls_text = self.small_font.render(
                'WASD移动 | 鼠标瞄准 | 左键射击 | 右键切换瞄准 | P暂停 | R重开 | ESC菜单',
                True, COLORS['text']
            )
        else:
            controls_text = self.small_font.render(
                'WASD移动和转向 | 空格射击 | P暂停 | R重开 | ESC菜单',
                True, COLORS['text']
            )
        self.screen.blit(controls_text, (SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT - 30))

        # 玩家2控制提示
        if len(self.players) > 1 and self.players[1].health > 0:
            player2_controls = self.small_font.render(
                '玩家2: 方向键移动 | 右Ctrl射击',
                True, (255, 165, 0)
            )
            self.screen.blit(player2_controls, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT - 60))

        # 鼠标控制提示
        if (self.mouse_control and self.show_mouse_aim and
                len(self.players) > 0 and self.players[0].health > 0 and self.players[0].mouse_control):
            aim_hint = self.small_font.render("鼠标瞄准 | 左键射击 | 右键隐藏瞄准线", True, (200, 200, 100))
            self.screen.blit(aim_hint, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT - 90))

    def check_game_state(self):
        """检查游戏状态"""
        # 更新时间
        if self.game_state == "playing" and not self.is_paused:
            self.time_remaining -= 1

        # 检查存活坦克数量
        alive_tanks = [tank for tank in self.tanks if tank.health > 0]

        if len(alive_tanks) == 1:
            # 只有一个坦克存活，游戏结束
            self.game_state = "game_over"
            self.winner = alive_tanks[0]
            return True
        elif len(alive_tanks) == 0:
            # 没有坦克存活，平局
            self.game_state = "game_over"
            self.winner = None
            return True
        elif self.time_remaining <= 0:
            # 时间到，按血量判定胜负
            self.game_state = "game_over"
            # 找到血量最高的坦克
            max_health = -1
            self.winner = None
            for tank in alive_tanks:
                if tank.health > max_health:
                    max_health = tank.health
                    self.winner = tank
            # 检查是否有多个坦克血量相同
            same_health_tanks = [tank for tank in alive_tanks if tank.health == max_health]
            if len(same_health_tanks) > 1:
                self.winner = None  # 平局
            return True

        return False

    def show_game_over_screen(self):
        """显示游戏结束画面"""
        end_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        end_surface.fill(COLORS['pause_bg'])
        self.screen.blit(end_surface, (0, 0))

        # 显示结果
        result_font = get_chinese_font(48)

        if self.winner:
            if self.winner.is_enemy:
                result_text = result_font.render("电脑获胜!", True, (255, 0, 0))
            elif self.winner.is_player2:
                result_text = result_font.render("玩家2获胜!", True, (255, 165, 0))
            else:
                result_text = result_font.render("玩家1获胜!", True, (0, 255, 0))
        else:
            result_text = result_font.render("平局!", True, (255, 255, 0))

        result_rect = result_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        self.screen.blit(result_text, result_rect)

        # 显示统计信息
        stats_font = get_chinese_font(24)

        # 收集所有存活坦克的血量信息
        alive_tanks = [tank for tank in self.tanks if tank.health > 0]
        if self.time_remaining <= 0 and len(alive_tanks) > 0:
            stats_lines = ["时间到! 按血量判定胜负:"]
            for tank in self.tanks:
                if tank.health > 0:
                    if tank.is_enemy:
                        name = "电脑"
                        color = (220, 100, 100)
                    elif tank.is_player2:
                        name = "玩家2"
                        color = (255, 165, 0)
                    else:
                        name = "玩家1"
                        color = (80, 160, 255)
                    stats_lines.append(f"{name}: {tank.health}生命值")
        else:
            stats_lines = [f"游戏模式: {self.game_mode}"]

        for i, line in enumerate(stats_lines):
            stat_text = stats_font.render(line, True, COLORS['menu_text'])
            stat_rect = stat_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + i * 40))
            self.screen.blit(stat_text, stat_rect)

        hint_font = get_chinese_font(20)
        hint_text = hint_font.render("点击鼠标开始新游戏", True, COLORS['pause_text'])
        hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))
        self.screen.blit(hint_text, hint_rect)

        pygame.display.flip()

    def run_game_loop(self, game_mode):
        """运行游戏主循环"""
        self.reset_game(game_mode)
        self.game_state = "playing"

        while True:
            # 处理事件
            event_result = self.handle_events()
            if event_result == "restart":
                return "restart"
            elif event_result == "menu":
                return "menu"
            elif not event_result:
                return False

            if self.is_paused:
                continue

            if self.game_state != "playing":
                continue

            # 更新游戏状态
            self.update_player_movement()
            if len(self.enemies) > 0:
                self.update_enemy_ai()

            for tank in self.tanks:
                if tank.health > 0:
                    tank.update()

            self.update_powerups()
            self.heal_texts = [text for text in self.heal_texts if text.update()]
            self.damage_texts = [text for text in self.damage_texts if text.update()]

            self.handle_powerup_collisions()
            self.handle_bullet_collisions()

            # 更新爆炸效果
            for explosion in self.explosions[:]:
                explosion.update()
                if not explosion.active:
                    self.explosions.remove(explosion)

            # 绘制游戏
            self.draw_game()
            pygame.display.flip()
            self.clock.tick(FPS)

            # 检查游戏状态
            if self.check_game_state():
                if self.game_state == "game_over":
                    self.show_game_over_screen()
                    # 等待点击
                    waiting = True
                    while waiting:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                return False
                            elif event.type == pygame.MOUSEBUTTONDOWN:
                                if event.button == 1:
                                    return "restart"
                        self.clock.tick(FPS)

    def run(self):
        """运行游戏"""
        while self.game_running:
            if self.game_state == "menu":
                menu_result = self.menu.run()
                if menu_result == "quit":
                    self.game_running = False
                elif menu_result in ["人机对战", "双人对战", "双人+电脑"]:
                    # 开始游戏循环，自动重开
                    while True:
                        game_result = self.run_game_loop(menu_result)
                        if game_result == "menu":
                            self.game_state = "menu"
                            break
                        elif game_result == "restart":
                            # 继续同一模式的新游戏（自动重开）
                            continue
                        elif not game_result:
                            self.game_running = False
                            break
                else:
                    self.game_running = False
            else:
                self.game_running = False

        pygame.quit()


def main():
    print("坦克大战 - 多模式对战版 启动!")
    print("主菜单功能:")
    print("1. 开始游戏 - 选择游戏模式")
    print("2. 游戏说明 - 查看操作说明")
    print("3. 退出游戏 - 退出程序")
    print("游戏模式:")
    print("- 人机对战: 1名玩家 vs 1名电脑")
    print("- 双人对战: 2名玩家对战")
    print("- 双人+电脑: 2名玩家 vs 1名电脑")
    print("游戏规则:")
    print("- 最后存活的坦克获胜")
    print("- 5分钟时限，时间到按血量判定胜负")
    print("- 按R键重新开始，ESC返回主菜单")
    print("操作说明:")
    print("玩家1: WASD移动和转向 | 空格射击")
    print("玩家2: 方向键移动和转向 | 右Ctrl射击")
    print("通用: P暂停 | R重开 | ESC菜单")

    game = Game()
    game.run()


if __name__ == "__main__":
    main()