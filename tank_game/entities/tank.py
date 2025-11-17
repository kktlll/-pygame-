import pygame
import math
import random
from config import *
from entities.bullet import NormalBullet, LightningBullet, BigBullet
from entities.effects import EffectParticle
from utils.text_effects import StatusEffect, HealText

class Tank:
    def __init__(self, x, y, color, is_enemy=False):
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

        # 边界检查
        if new_x < 20 or new_x > SCREEN_WIDTH - self.width - 20:
            return
        if new_y < 20 or new_y > SCREEN_HEIGHT - self.height - 20:
            return

        new_rect = pygame.Rect(new_x, new_y, self.width, self.height)

        # 墙壁碰撞检查
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