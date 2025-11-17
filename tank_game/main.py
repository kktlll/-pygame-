import pygame
from game import Game


def main():
    pygame.init()

    print("坦克大战 - 最终优化版 启动!")
    print("核心优化:")
    print("1. 墙壁：固定1格大小（40x40px），不再'肥胖'")
    print("2. 缝隙：1格缝隙可穿过（坦克=1格，缝隙=1格）")
    print("3. 敌方：每次重开在上方随机位置出生，不再固定")
    print("4. 地图：墙壁分布更合理，避免密集拥堵")
    print("控制说明:")
    print("WASD: 移动和转向 | 空格: 发射炮弹 | P: 暂停 | R: 重开 | ESC: 退出")
    print("武器类型: 普通(25伤害), 闪电(15+范围伤害), 巨型(40伤害)")

    game = Game()
    game.run()


if __name__ == "__main__":
    main()