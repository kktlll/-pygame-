import pygame
import random
import math
from config import *
from entities.tank import Tank
from entities.wall import Wall
from entities.powerup import PowerUp
from entities.effects import Explosion
from utils.text_effects import DamageText, HealText
from utils.helpers import create_random_map, create_enemies_safely, spawn_powerup, draw_pause_menu


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("坦克大战 - 优化随机地图版 | 1格坦克+墙壁")
        self.clock = pygame.time.Clock()
        self.is_paused = False
        self.game_running = True

    def reset_game(self):
        """重置游戏状态"""
        self.walls = create_random_map()
        player_x = (GRID_SIZE * 2) + (GRID_SIZE * 3) - TANK_SIZE // 2
        player_y = (SCREEN_HEIGHT - GRID_SIZE * 5) + (GRID_SIZE * 1.5) - TANK_SIZE // 2
        self.player = Tank(player_x, player_y, COLORS['player'])
        self.enemies = create_enemies_safely(self.walls)
        self.all_tanks = [self.player] + self.enemies
        self.explosions = []
        self.powerups = []
        self.powerup_timer = 0
        self.damage_texts = []
        self.heal_texts = []

        self.font = get_chinese_font(28)
        self.small_font = get_chinese_font(16)

    def handle_events(self):
        """处理游戏事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    self.is_paused = not self.is_paused
                    if self.is_paused:
                        draw_pause_menu(self.screen)
                elif event.key == pygame.K_r:
                    return "restart"
                elif event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_SPACE and not self.is_paused:
                    self.player.shoot()
        return True

    def update_player_movement(self):
        """更新玩家移动"""
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.player.rotate(0)
            self.player.move(0, -1, self.walls, self.all_tanks)
        if keys[pygame.K_s]:
            self.player.rotate(180)
            self.player.move(0, 1, self.walls, self.all_tanks)
        if keys[pygame.K_a]:
            self.player.rotate(270)
            self.player.move(-1, 0, self.walls, self.all_tanks)
        if keys[pygame.K_d]:
            self.player.rotate(90)
            self.player.move(1, 0, self.walls, self.all_tanks)

    def update_enemy_ai(self):
        """更新敌人AI"""
        for enemy in self.enemies:
            if random.random() < 0.02:
                enemy.rotate(random.choice([0, 90, 180, 270]))

            angle_rad = math.radians(enemy.rotation)
            dx = math.sin(angle_rad)
            dy = -math.cos(angle_rad)
            enemy.move(dx, dy, self.walls, self.all_tanks)

            if random.random() < 0.01:
                enemy.shoot()

    def update_powerups(self):
        """更新道具"""
        self.powerup_timer += 1
        if self.powerup_timer >= 300 and len(self.powerups) < 3:
            self.powerups.append(spawn_powerup(self.walls, self.all_tanks))
            self.powerup_timer = 0

    def handle_powerup_collisions(self):
        """处理道具碰撞"""
        for powerup in self.powerups[:]:
            powerup.update()
            for tank in self.all_tanks[:]:
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
        for tank in self.all_tanks[:]:
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
        for target_tank in self.all_tanks:
            if target_tank == tank or bullet.is_enemy == target_tank.is_enemy:
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
                    self.all_tanks.remove(target_tank)
                    if target_tank in self.enemies:
                        self.enemies.remove(target_tank)
                        if random.random() < 0.3:
                            self.powerups.append(spawn_powerup(self.walls, self.all_tanks))
                return True
        return False

    def handle_lightning_aoe(self, tank, bullet, original_target):
        """处理闪电AOE伤害"""
        for aoe_tank in self.all_tanks:
            if aoe_tank != tank and aoe_tank.is_enemy != tank.is_enemy:
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
        for tank in self.all_tanks:
            tank.draw(self.screen)
            for bullet in tank.bullets:
                bullet.draw(self.screen)
        for explosion in self.explosions:
            explosion.draw(self.screen)
        for damage_text in self.damage_texts:
            damage_text.draw(self.screen)
        for heal_text in self.heal_texts:
            heal_text.draw(self.screen)

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
        # 生命值
        health_text = self.font.render(f'生命: {self.player.health}', True, (0, 255, 0))
        self.screen.blit(health_text, (10, 10))

        # 武器信息
        weapon_names = {"normal": "普通", "lightning": "闪电", "big": "巨型"}
        weapon_text = self.font.render(f'武器: {weapon_names[self.player.bullet_type]}', True, COLORS['text'])
        self.screen.blit(weapon_text, (10, 45))

        # 敌人数量
        enemies_text = self.font.render(f'敌人: {len(self.enemies)}', True, COLORS['enemy'])
        self.screen.blit(enemies_text, (SCREEN_WIDTH - 120, 10))

        # 状态效果
        effect_y = 80
        for effect in self.player.status_effects:
            effect.draw(self.screen, 10, effect_y)
            effect_y += 45

        # 控制提示
        controls_text = self.small_font.render('WASD移动 | 空格射击 | P暂停 | R重开 | ESC退出 | 1格坦克+墙壁', True,
                                               COLORS['text'])
        self.screen.blit(controls_text, (SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT - 30))

        # 武器伤害提示
        damage_info = ["普通: 25伤害", "闪电: 15+范围7", "巨型: 40伤害"]
        for i, info in enumerate(damage_info):
            info_text = self.small_font.render(info, True, (200, 200, 200))
            self.screen.blit(info_text, (SCREEN_WIDTH - 150, 40 + i * 18))

    def check_game_over(self):
        """检查游戏是否结束"""
        return self.player.health <= 0 or len(self.enemies) == 0

    def show_game_over_screen(self):
        """显示游戏结束画面"""
        end_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        end_surface.fill(COLORS['pause_bg'])
        self.screen.blit(end_surface, (0, 0))

        end_font = get_chinese_font(48)
        end_text = end_font.render("游戏结束!" if self.player.health <= 0 else "胜利!", True,
                                   (255, 0, 0) if self.player.health <= 0 else (0, 255, 0))
        end_rect = end_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(end_text, end_rect)

        hint_font = get_chinese_font(24)
        hint_text = hint_font.render("按 R 重新开始（新地图+新敌方位置） | 按 ESC 退出", True, COLORS['pause_text'])
        hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(hint_text, hint_rect)

        pygame.display.flip()

        # 等待操作
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        return "restart"
                    elif event.key == pygame.K_ESCAPE:
                        return False
            self.clock.tick(FPS)

    def run_game_loop(self):
        """运行游戏主循环"""
        self.reset_game()

        while True:
            # 处理事件
            event_result = self.handle_events()
            if event_result == "restart":
                return "restart"
            elif not event_result:
                return False

            if self.is_paused:
                continue

            # 更新游戏状态
            self.update_player_movement()
            self.update_enemy_ai()

            for tank in self.all_tanks:
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

            # 检查游戏结束
            if self.check_game_over():
                return self.show_game_over_screen()

    def run(self):
        """运行游戏"""
        while self.game_running:
            result = self.run_game_loop()
            if result == "restart":
                continue
            else:
                self.game_running = False

        pygame.quit()