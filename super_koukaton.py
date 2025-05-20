import pygame
import sys  # ← 新加的


# 画面のサイズ
SCREEN_WIDTH = 1100
SCREEN_HEIGHT = 700
FPS = 60

# 色
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# ブロックの上端のy座標（背景画像に合わせて調整）
GROUND_Y = 610  # 必要に応じて微調整してください

TILE_SIZE = 50  # ← 加在这里，表示每块地砖的宽度



# 1 是地面，0 是坑（落ちったらGame Over）
ground_tiles = [
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1,1, 1, 1, 1, 1, 1, 1,1,
      1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1,1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1,1, 1, 1, 1, 1, 1, 1,1,
      1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 0, 1, 1, 1, 1, 1, 1
]

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([30, 50])
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = 50
        self.rect.bottom = GROUND_Y  # ブロックの上に乗せる
        self.speed_x = 0
        self.speed_y = 0
        self.gravity = 1
        self.jump_power = -20
        self.is_jumping = False
        self.world_x = 50  # ワールド座標
        self.is_alive = True  # プレイヤーの生死状態 

    def update(self):
        # 左右移動
        self.world_x += self.speed_x
        # プレイヤーの画面上のx座標は後で調整

        # 重力
        self.speed_y += self.gravity
        self.rect.y += self.speed_y

        # 地面との衝突判定（ブロックの上）
        if self.rect.bottom > GROUND_Y:
            self.rect.bottom = GROUND_Y
            self.speed_y = 0
            self.is_jumping = False
                    # 掉进坑的判定
            tile_index = self.world_x // TILE_SIZE
            if 0 <= tile_index < len(ground_tiles):
                if ground_tiles[int(tile_index)] == 0 and self.rect.bottom >= GROUND_Y:
                    print("Game Over: 落坑了")
                    pygame.quit()
                    sys.exit()


    def jump(self):
        if not self.is_jumping:
            self.speed_y = self.jump_power
            self.is_jumping = True


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("マリオっぽいゲーム")
    clock = pygame.time.Clock()

    # 背景画像のロード
    bg_img = pygame.transform.rotozoom(pygame.image.load("ex5/fig/pg_bg.png").convert(), 0, 2.92)
    bg_width = bg_img.get_width()
    bg_height = bg_img.get_height()

    all_sprites = pygame.sprite.Group()
    player = Player()
    all_sprites.add(player)

    scroll_x = 0  # 背景のスクロール量

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.speed_x = -5
                if event.key == pygame.K_RIGHT:
                    player.speed_x = 5
                if event.key == pygame.K_SPACE:
                    player.jump()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT and player.speed_x < 0:
                    player.speed_x = 0
                if event.key == pygame.K_RIGHT and player.speed_x > 0:
                    player.speed_x = 0

        # ゲームループ
        all_sprites.update()

        # プレイヤーが画面中央より右に行ったら背景をスクロール
        center_x = SCREEN_WIDTH // 2
        if player.world_x > center_x:
            scroll_x = player.world_x - center_x
        else:
            scroll_x = 0
        # 背景の範囲外に行かないように制限
        max_scroll = bg_width - SCREEN_WIDTH
        if scroll_x > max_scroll:
            scroll_x = max_scroll
        if scroll_x < 0:
            scroll_x = 0

        # プレイヤーの画面上のx座標を調整
        if player.world_x > center_x:
            player.rect.x = center_x
        else:
            player.rect.x = player.world_x

        # 描画
        screen.blit(bg_img, (-scroll_x, 0))
        all_sprites.draw(screen)
        pygame.display.flip()

        clock.tick(FPS)

    pygame.quit()







if __name__ == '__main__':
    main()