import pygame
import random
from config import *
from entities.wall import Wall
from entities.tank import Tank
from entities.powerup import PowerUp

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

def create_enemies_safely(walls):
    """优化敌方坦克生成"""
    enemies = []
    positions_tried = set()
    enemy_spawn_area = pygame.Rect(
        GRID_SIZE * 2, GRID_SIZE * 2,
        SCREEN_WIDTH - GRID_SIZE * 4, GRID_SIZE * 4
    )

    while len(enemies) < 4:
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

def draw_pause_menu(screen):
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