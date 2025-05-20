import pygame
import sys
import random
import math

# 画面のサイズ
SCREEN_WIDTH = 1100
SCREEN_HEIGHT = 700
FPS = 60

# 色
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# ブロックの上端のy座標
GROUND_Y = 610
TILE_SIZE = 50

# 游戏状态
coin_count = 0
score = 0
lives = 3
power_level = 0  # 0=小马里奥, 1=大马里奥, 2=火焰马里奥
game_time = 400  # 游戏时间（秒）
level = 1

# 字体
coin_font = None
score_font = None

# 音效（你可以替换这些文件）
coin_sound = None
jump_sound = None
fireball_sound = None
powerup_sound = None
enemy_defeat_sound = None
game_over_sound = None

# 地图 - 全部设为1（无坑）
ground_tiles = [1] * 200  # 创建200个地面块

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.load_images()
        self.rect = self.image.get_rect()
        self.rect.x = 50
        self.rect.bottom = GROUND_Y
        self.speed_x = 0
        self.speed_y = 0
        self.gravity = 1
        self.jump_power = -18
        self.is_jumping = False
        self.world_x = 50
        self.is_alive = True
        self.invincible_time = 0  # 无敌时间
        self.animation_frame = 0
        self.animation_counter = 0
        self.facing_right = True
        
    def load_images(self):
        """根据power_level加载不同的马里奥图片"""
        try:
            if power_level == 0:  # 小马里奥
                self.image = pygame.image.load("ex5/fig/supermario.png").convert_alpha()
                self.image = pygame.transform.scale(self.image, (30, 50))
            elif power_level == 1:  # 大马里奥
                self.image = pygame.image.load("ex5/fig/supermario_big.png").convert_alpha()
                self.image = pygame.transform.scale(self.image, (35, 70))
            else:  # 火焰马里奥
                self.image = pygame.image.load("ex5/fig/supermario_fire.png").convert_alpha()
                self.image = pygame.transform.scale(self.image, (35, 70))
        except:
            # 如果图片加载失败，使用默认图片
            self.image = pygame.image.load("ex5/fig/supermario.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (30, 50))

    def update(self):
        if not self.is_alive:
            return
            
        # 更新无敌时间
        if self.invincible_time > 0:
            self.invincible_time -= 1
            
        # 动画更新
        self.animation_counter += 1
        if self.animation_counter >= 10:
            self.animation_counter = 0
            self.animation_frame = (self.animation_frame + 1) % 4
            
        # 左右移動
        self.world_x += self.speed_x
        
        # 限制不能往回走太远
        if self.world_x < 0:
            self.world_x = 0

        # 重力
        self.speed_y += self.gravity
        self.rect.y += self.speed_y

        # 地面碰撞
        if self.rect.bottom >= GROUND_Y:
            self.rect.bottom = GROUND_Y
            self.speed_y = 0
            self.is_jumping = False

    def jump(self):
        if not self.is_jumping and self.is_alive:
            self.speed_y = self.jump_power
            self.is_jumping = True
            if jump_sound:
                jump_sound.play()

    def shoot_fireball(self):
        """发射火球（只有火焰马里奥可以）"""
        if power_level >= 2:
            direction = 1 if self.facing_right else -1
            fireball = Fireball(self.world_x + (35 if self.facing_right else -35), 
                              self.rect.centery, direction)
            fireballs.add(fireball)
            if fireball_sound:
                fireball_sound.play()

    def power_up(self):
        """升级"""
        global power_level
        if power_level < 2:
            power_level += 1
            self.load_images()
            if powerup_sound:
                powerup_sound.play()

    def take_damage(self):
        """受伤"""
        global power_level, lives
        if self.invincible_time > 0:
            return
            
        if power_level > 0:
            power_level -= 1
            self.load_images()
            self.invincible_time = 120  # 2秒无敌时间
        else:
            lives -= 1
            if lives <= 0:
                self.die()
            else:
                self.invincible_time = 180  # 3秒无敌时间

    def die(self):
        """死亡"""
        self.is_alive = False
        if game_over_sound:
            game_over_sound.play()
        print("Game Over!")

class Coin(pygame.sprite.Sprite):
    def __init__(self, world_x, world_y):
        super().__init__()
        try:
            self.image = pygame.image.load("ex5/fig/coin.jpg").convert_alpha()
            self.image = pygame.transform.scale(self.image, (25, 25))
        except:
            # 如果加载失败，创建一个黄色圆形
            self.image = pygame.Surface((25, 25), pygame.SRCALPHA)
            pygame.draw.circle(self.image, YELLOW, (12, 12), 12)
            
        self.rect = self.image.get_rect()
        self.world_x = world_x
        self.world_y = world_y
        self.rect.x = world_x
        self.rect.y = world_y
        self.value = 100
        self.bob_offset = 0
        self.bob_speed = 0.1

    def update_screen_position(self, scroll_x):
        self.rect.x = self.world_x - scroll_x
        # 添加上下浮动效果
        self.bob_offset += self.bob_speed
        self.rect.y = self.world_y + math.sin(self.bob_offset) * 3

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, world_x, world_y, powerup_type="mushroom"):
        super().__init__()
        self.powerup_type = powerup_type
        try:
            if powerup_type == "mushroom":
                self.image = pygame.image.load("ex5/fig/mushroom.png").convert_alpha()
            elif powerup_type == "flower":
                self.image = pygame.image.load("ex5/fig/flower.png").convert_alpha()
            else:
                self.image = pygame.image.load("ex5/fig/star.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (30, 30))
        except:
            # 默认创建一个彩色方块
            self.image = pygame.Surface((30, 30))
            color = RED if powerup_type == "mushroom" else BLUE if powerup_type == "flower" else YELLOW
            self.image.fill(color)
            
        self.rect = self.image.get_rect()
        self.world_x = world_x
        self.world_y = world_y
        self.speed_x = 2
        self.speed_y = 0
        self.gravity = 0.5

    def update(self):
        self.world_x += self.speed_x
        self.speed_y += self.gravity
        self.world_y += self.speed_y
        
        # 地面碰撞
        if self.world_y >= GROUND_Y - 30:
            self.world_y = GROUND_Y - 30
            self.speed_y = 0

    def update_screen_position(self, scroll_x):
        self.rect.x = self.world_x - scroll_x
        self.rect.y = self.world_y

class Enemy(pygame.sprite.Sprite):
    def __init__(self, world_x, world_y, enemy_type="goomba"):
        super().__init__()
        self.enemy_type = enemy_type
        try:
            if enemy_type == "goomba":
                self.image = pygame.image.load("ex5/fig/goomba.png").convert_alpha()
                self.image = pygame.transform.scale(self.image, (35, 35))
            else:  # koopa
                self.image = pygame.image.load("ex5/fig/koopa.png").convert_alpha()
                self.image = pygame.transform.scale(self.image, (40, 50))
        except:
            # 默认创建红色方块
            size = (35, 35) if enemy_type == "goomba" else (40, 50)
            self.image = pygame.Surface(size)
            self.image.fill(RED)
            
        self.rect = self.image.get_rect()
        self.world_x = world_x
        self.world_y = world_y
        self.speed_x = -1
        self.speed_y = 0
        self.gravity = 0.8
        self.alive = True

    def update(self):
        if not self.alive:
            return
            
        self.world_x += self.speed_x
        self.speed_y += self.gravity
        self.world_y += self.speed_y
        
        # 地面碰撞
        if self.world_y >= GROUND_Y - self.rect.height:
            self.world_y = GROUND_Y - self.rect.height
            self.speed_y = 0
            
        # 如果走得太远就删除
        if self.world_x < -100:
            self.kill()

    def update_screen_position(self, scroll_x):
        self.rect.x = self.world_x - scroll_x
        self.rect.y = self.world_y
        
    def defeat(self):
        self.alive = False
        if enemy_defeat_sound:
            enemy_defeat_sound.play()
        self.kill()

class Fireball(pygame.sprite.Sprite):
    def __init__(self, world_x, world_y, direction):
        super().__init__()
        try:
            self.image = pygame.image.load("ex5/fig/fireball.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (20, 20))
        except:
            self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
            pygame.draw.circle(self.image, RED, (10, 10), 10)
            
        self.rect = self.image.get_rect()
        self.world_x = world_x
        self.world_y = world_y
        self.speed_x = 8 * direction
        self.speed_y = -2
        self.gravity = 0.3
        self.bounce_count = 0

    def update(self):
        self.world_x += self.speed_x
        self.speed_y += self.gravity
        self.world_y += self.speed_y
        
        # 地面碰撞 - 弹跳
        if self.world_y >= GROUND_Y - 20:
            self.world_y = GROUND_Y - 20
            self.speed_y = -4
            self.bounce_count += 1
            
        # 弹跳3次后消失
        if self.bounce_count >= 3:
            self.kill()

    def update_screen_position(self, scroll_x):
        self.rect.x = self.world_x - scroll_x
        self.rect.y = self.world_y

def load_sounds():
    """加载音效文件"""
    global coin_sound, jump_sound, fireball_sound, powerup_sound, enemy_defeat_sound, game_over_sound
    try:
        pygame.mixer.init()
        coin_sound = pygame.mixer.Sound("ex5/sound/coin.wav") 
        jump_sound = pygame.mixer.Sound("ex5/sound/jump.wav")
        fireball_sound = pygame.mixer.Sound("ex5/sound/fireball.wav")
        powerup_sound = pygame.mixer.Sound("ex5/sound/powerup.wav")
        enemy_defeat_sound = pygame.mixer.Sound("ex5/sound/enemy_defeat.wav")
        game_over_sound = pygame.mixer.Sound("ex5/sound/game_over.wav")
    except:
        print("音效文件加载失败，游戏将静音运行")

def spawn_enemy():
    """随机生成敌人"""
    enemy_type = random.choice(["goomba", "koopa"])
    spawn_x = player.world_x + SCREEN_WIDTH + random.randint(0, 200)
    enemy = Enemy(spawn_x, GROUND_Y - 50, enemy_type)
    enemies.add(enemy)

def spawn_powerup(x, y):
    """生成道具"""
    powerup_type = random.choice(["mushroom", "flower", "star"])
    powerup = PowerUp(x, y, powerup_type)
    powerups.add(powerup)

def main():
    global coin_count, score, lives, game_time, player, enemies, powerups, fireballs
    global coin_font, score_font
    
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("スーパーマリオ風ゲーム")
    clock = pygame.time.Clock()

    # 加载音效
    load_sounds()

    # 初始化字体
    coin_font = pygame.font.Font(None, 24)
    score_font = pygame.font.Font(None, 36)

    # 背景
    try:
        bg_img = pygame.transform.rotozoom(pygame.image.load("ex5/fig/pg_bg.png").convert(), 0, 2.92)
    except:
        bg_img = pygame.Surface((SCREEN_WIDTH * 3, SCREEN_HEIGHT))
        bg_img.fill((135, 206, 235))  # 天蓝色背景
    bg_width = bg_img.get_width()

    # 创建精灵组
    all_sprites = pygame.sprite.Group()
    coins = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    powerups = pygame.sprite.Group()
    fireballs = pygame.sprite.Group()

    # 创建玩家
    player = Player()
    all_sprites.add(player)

    # 创建金币（更多且分布更广）
    for i in range(50):
        coin_x = 200 + i * random.randint(100, 300)
        coin_y = GROUND_Y - random.randint(50, 200)
        coin = Coin(coin_x, coin_y)
        coins.add(coin)

    # 创建一些道具
    for i in range(10):
        powerup_x = 500 + i * random.randint(200, 400)
        powerup_y = GROUND_Y - 100
        spawn_powerup(powerup_x, powerup_y)

    scroll_x = 0
    enemy_spawn_timer = 0
    game_timer = 0

    running = True
    while running and lives > 0:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.speed_x = -6
                    player.facing_right = False
                if event.key == pygame.K_RIGHT:
                    player.speed_x = 6
                    player.facing_right = True
                if event.key == pygame.K_SPACE:
                    player.jump()
                if event.key == pygame.K_x:  # X键发射火球
                    player.shoot_fireball()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT and player.speed_x < 0:
                    player.speed_x = 0
                if event.key == pygame.K_RIGHT and player.speed_x > 0:
                    player.speed_x = 0

        # 更新游戏时间
        game_timer += 1
        if game_timer >= FPS:  # 每秒
            game_timer = 0
            game_time -= 1
            if game_time <= 0:
                player.die()

        # 敌人生成
        enemy_spawn_timer += 1
        if enemy_spawn_timer >= random.randint(180, 300):  # 3-5秒随机生成
            spawn_enemy()
            enemy_spawn_timer = 0

        # 更新全部精灵
        all_sprites.update()
        enemies.update()
        powerups.update()
        fireballs.update()

        # 计算滚动
        center_x = SCREEN_WIDTH // 2
        if player.world_x > center_x:
            scroll_x = player.world_x - center_x
        else:
            scroll_x = 0
        
        max_scroll = bg_width - SCREEN_WIDTH
        if scroll_x > max_scroll:
            scroll_x = max_scroll
        if scroll_x < 0:
            scroll_x = 0

        # 更新玩家屏幕位置
        if player.world_x > center_x:
            player.rect.x = center_x
        else:
            player.rect.x = player.world_x

        # 更新所有物体的屏幕位置
        for coin in coins:
            coin.update_screen_position(scroll_x)
        for enemy in enemies:
            enemy.update_screen_position(scroll_x)
        for powerup in powerups:
            powerup.update_screen_position(scroll_x)
        for fireball in fireballs:
            fireball.update_screen_position(scroll_x)

        # 碰撞检测
        # 金币碰撞
        for coin in coins.sprites():
            player_world_rect = pygame.Rect(player.world_x - 15, player.rect.y, 30, 50)
            coin_world_rect = pygame.Rect(coin.world_x, coin.world_y, 25, 25)
            if player_world_rect.colliderect(coin_world_rect):
                coin_count += 1
                score += coin.value
                if coin_sound:
                    coin_sound.play()
                coins.remove(coin)

        # 道具碰撞
        for powerup in powerups.sprites():
            player_world_rect = pygame.Rect(player.world_x - 15, player.rect.y, 30, 50)
            powerup_world_rect = pygame.Rect(powerup.world_x, powerup.world_y, 30, 30)
            if player_world_rect.colliderect(powerup_world_rect):
                player.power_up()
                score += 1000
                powerups.remove(powerup)

        # 敌人碰撞
        for enemy in enemies.sprites():
            player_world_rect = pygame.Rect(player.world_x - 15, player.rect.y, 30, 50)
            enemy_world_rect = pygame.Rect(enemy.world_x, enemy.world_y, enemy.rect.width, enemy.rect.height)
            if player_world_rect.colliderect(enemy_world_rect):
                # 检查是否从上方踩踏
                if player.speed_y > 0 and player.rect.bottom <= enemy.rect.centery:
                    enemy.defeat()
                    score += 500
                    player.speed_y = -10  # 小跳跃
                else:
                    player.take_damage()

        # 火球与敌人碰撞
        for fireball in fireballs:
            for enemy in enemies:
                fireball_rect = pygame.Rect(fireball.world_x, fireball.world_y, 20, 20)
                enemy_rect = pygame.Rect(enemy.world_x, enemy.world_y, enemy.rect.width, enemy.rect.height)
                if fireball_rect.colliderect(enemy_rect):
                    enemy.defeat()
                    score += 500
                    fireballs.remove(fireball)
                    break

        # 绘制
        screen.fill(BLACK)
        screen.blit(bg_img, (-scroll_x, 0))
        
        # 绘制所有可见物体
        if player.is_alive:
            # 无敌时闪烁效果
            if player.invincible_time == 0 or player.invincible_time % 10 < 5:
                screen.blit(player.image, player.rect)

        for coin in coins:
            if -50 <= coin.rect.x <= SCREEN_WIDTH + 50:
                screen.blit(coin.image, coin.rect)

        for enemy in enemies:
            if -100 <= enemy.rect.x <= SCREEN_WIDTH + 100:
                screen.blit(enemy.image, enemy.rect)

        for powerup in powerups:
            if -50 <= powerup.rect.x <= SCREEN_WIDTH + 50:
                screen.blit(powerup.image, powerup.rect)

        for fireball in fireballs:
            if -50 <= fireball.rect.x <= SCREEN_WIDTH + 50:
                screen.blit(fireball.image, fireball.rect)

        # 绘制UI
        # 分数
        score_text = score_font.render(f"SCORE: {score:06d}", True, WHITE)
        screen.blit(score_text, (20, 20))
        
        # 金币
        coin_text = coin_font.render(f"COINS: {coin_count:02d}", True, WHITE)
        screen.blit(coin_text, (20, 60))
        
        # 生命
        lives_text = coin_font.render(f"LIVES: {lives}", True, WHITE)
        screen.blit(lives_text, (20, 85))
        
        # 时间
        time_text = coin_font.render(f"TIME: {game_time:03d}", True, WHITE)
        screen.blit(time_text, (20, 110))
        
        # 等级
        level_text = coin_font.render(f"LEVEL: {level}", True, WHITE)
        screen.blit(level_text, (20, 135))
        
        # 马里奥状态
        status = ["SMALL", "BIG", "FIRE"][power_level]
        status_text = coin_font.render(f"MARIO: {status}", True, WHITE)
        screen.blit(status_text, (20, 160))

        pygame.display.flip()
        clock.tick(FPS)

    # 游戏结束
    pygame.time.wait(2000)
    pygame.quit()

if __name__ == '__main__':
    main()