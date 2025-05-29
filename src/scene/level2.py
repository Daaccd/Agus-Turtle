import pygame
import math
import os
import sys

# Konstanta
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
COLOR_SKY = (135, 206, 235)
MOVABLE_WALL_SPEED = 100

# Kelas untuk memuat gambar
class ResourceManager:
    def __init__(self, asset_dir="assets"):
        self.asset_dir = asset_dir
        self.cache = {}

    def load_image(self, name):
        if name not in self.cache:
            path = os.path.join(self.asset_dir, f"{name}.png")
            if not os.path.exists(path):
                print(f"[ERROR] Gambar {path} tidak ditemukan")
                sys.exit(1)
            self.cache[name] = pygame.image.load(path).convert_alpha()
        return self.cache[name]

# Tuas
class Lever(pygame.Rect):
    def __init__(self, x, y, width, height, up_img, down_img):
        super().__init__(x, y, width, height)
        self.up_img = up_img
        self.down_img = down_img
        self.is_up = True
        self.is_interactable = False

    def draw(self, screen):
        screen.blit(self.up_img if self.is_up else self.down_img, self.topleft)

    def toggle(self):
        self.is_up = not self.is_up

# Level 2
class Level2:
    def __init__(self, player, resources: ResourceManager, sfx_lever=None):
        self.player = player
        self.resources = resources
        self.player_start_pos = (50, SCREEN_HEIGHT - 100)
        self.sfx_lever = sfx_lever

        # Gambar latar
        self.cloud1_img = self.resources.load_image("cloud1")
        self.cloud2_img = self.resources.load_image("cloud2")
        self.bush_img   = self.resources.load_image("bush")
        self.plant_img  = self.resources.load_image("plant")
        self.cactus_img = self.resources.load_image("cactus")

        self.background_elements = [
            (self.cloud1_img, (100, 60)),
            (self.cloud1_img, (-20, 15)),
            (self.cloud1_img, (300, 25)),
            (self.cloud2_img, (500, 80)),
            (self.cloud2_img, (700, 50)),
            (self.bush_img,   (50 , SCREEN_HEIGHT - 115)),
            (self.plant_img,  (400, SCREEN_HEIGHT - 115)),
            (self.cactus_img, (100, SCREEN_HEIGHT - 115)),
            (self.cactus_img, (600, SCREEN_HEIGHT - 120)),
            (self.cactus_img, (350, SCREEN_HEIGHT - 120)),
            (self.cactus_img, (250, SCREEN_HEIGHT - 100)),
        ]

        # Rintangan
        self.obstacles = []
        self.ground_rect = pygame.Rect(0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50)
        self.obstacles.append(self.ground_rect)

        self.bridge_platforms_rects = []
        w1, w2 = 300, 200
        x1 = SCREEN_WIDTH - w1 - 400
        y1 = SCREEN_HEIGHT - 150
        x2 = SCREEN_WIDTH - w2 - 300
        y2 = SCREEN_HEIGHT - 250
        rect1 = pygame.Rect(x1, y1, w1, 25)
        rect2 = pygame.Rect(x2, y2, w2, 25)
        self.bridge_platforms_rects.extend([rect1, rect2])
        self.obstacles.extend([rect1, rect2])

        second_x = 100
        second_y = SCREEN_HEIGHT - 300
        self.second_bridge_rect = pygame.Rect(second_x, second_y, 100, 20)
        self.bridge_platforms_rects.append(self.second_bridge_rect)
        self.obstacles.append(self.second_bridge_rect)

        # Gambar
        self.block_img = self.resources.load_image("fence")
        self.grass_img = self.resources.load_image("grass")
        self.bridge_img = self.resources.load_image("bridge")
        self.lever_up_img = self.resources.load_image("lever_up")
        self.lever_down_img = self.resources.load_image("lever_down")
        self.door_img = self.resources.load_image("signExit")

        self.orig_block_w = self.block_img.get_width()
        self.orig_grass_w = self.grass_img.get_width()
        self.orig_bridge_w = self.bridge_img.get_width()
        self._block_cache = {}
        self._grass_cache = {}
        self._bridge_cache = {}

        lw = self.lever_up_img.get_width()
        lh = self.lever_up_img.get_height()
        lx = SCREEN_WIDTH - 685
        ly = SCREEN_HEIGHT - 300 - lh
        self.lever = Lever(lx, ly, lw, lh, self.lever_up_img, self.lever_down_img)
        self._can_interact_lever = True
        self._lever_cooldown_timer = 0

        dw, dh = 50, 80
        dx = SCREEN_WIDTH - 80
        dy = SCREEN_HEIGHT - 50 - dh
        self.closed_door_rect = pygame.Rect(dx, dy, dw, dh)
        self.door_open = False

        ew = self.door_img.get_width()
        eh = self.door_img.get_height()
        ex, ey = dx, dy - (eh - dh)
        self.exit_rect = pygame.Rect(ex, ey, ew, eh)

        if not self.door_open:
            self.obstacles.append(self.closed_door_rect)

        self.completed = False

    def update(self, dt, player_rect):
        ia = self.lever.inflate(10, 10)
        if player_rect.colliderect(ia):
            self.lever.is_interactable = True
            keys = pygame.key.get_pressed()
            if keys[pygame.K_e] and self._can_interact_lever:
                self.lever.toggle()
                self.door_open = not self.lever.is_up
                if self.sfx_lever:
                    self.sfx_lever.play()
                self._can_interact_lever = False
                self._lever_cooldown_timer = 0.5
        else:
            self.lever.is_interactable = False

        if not self._can_interact_lever:
            self._lever_cooldown_timer -= dt
            if self._lever_cooldown_timer <= 0:
                self._can_interact_lever = True

        if self.door_open:
            if self.closed_door_rect in self.obstacles:
                self.obstacles.remove(self.closed_door_rect)
        else:
            if self.closed_door_rect not in self.obstacles:
                self.obstacles.append(self.closed_door_rect)

        if player_rect.colliderect(self.exit_rect) and self.door_open:
            self.completed = True

    def draw(self, screen):
        screen.fill(COLOR_SKY)

        for img, pos in self.background_elements:
            screen.blit(img, pos)

        for rect in self.obstacles:
            if rect is self.ground_rect:
                img, orig_w, cache = self.grass_img, self.orig_grass_w, self._grass_cache
            elif rect in self.bridge_platforms_rects:
                continue
            elif rect is self.closed_door_rect:
                continue
            else:
                img, orig_w, cache = self.block_img, self.orig_block_w, self._block_cache

            h = rect.height
            if h not in cache:
                cache[h] = pygame.transform.scale(img, (orig_w, h))
            tile = cache[h]
            count = math.ceil(rect.width / orig_w)
            for i in range(count):
                screen.blit(tile, (rect.x + i * orig_w, rect.y))

        bw, bh = self.bridge_img.get_size()
        for rect in self.bridge_platforms_rects:
            for x in range(rect.left, rect.right, bw):
                draw_w = min(bw, rect.right - x)
                screen.blit(self.bridge_img, (x, rect.top), (0, 0, draw_w, bh))

        self.lever.draw(screen)
        if self.lever.is_interactable:
            font = pygame.font.SysFont(None, 24)
            text = font.render("Press E", True, (255,255,255))
            tr = text.get_rect(center=(self.lever.centerx, self.lever.top - 20))
            screen.blit(text, tr)

        if self.closed_door_rect in self.obstacles:
            h = self.closed_door_rect.height
            if h not in self._block_cache:
                self._block_cache[h] = pygame.transform.scale(self.block_img, (self.orig_block_w, h))
            tile = self._block_cache[h]
            count = math.ceil(self.closed_door_rect.width / self.orig_block_w)
            for i in range(count):
                screen.blit(tile, (self.closed_door_rect.x + i*self.orig_block_w, self.closed_door_rect.y))

        screen.blit(self.door_img, self.exit_rect.topleft)

# Jalankan untuk test
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    res = ResourceManager()
    player = pygame.Rect(50, SCREEN_HEIGHT - 100, 40, 60)
    level = Level2(player, res)

    running = True
    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        speed = 200
        if keys[pygame.K_LEFT]:
            player.x -= speed * dt
        if keys[pygame.K_RIGHT]:
            player.x += speed * dt
        if keys[pygame.K_UP]:
            player.y -= speed * dt
        if keys[pygame.K_DOWN]:
            player.y += speed * dt

        level.update(dt, player)
        level.draw(screen)
        pygame.draw.rect(screen, (255, 0, 0), player)  # Gambar player
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
