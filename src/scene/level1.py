import pygame, math
from src.constants import COLOR_BROWN
from src.components.lever import Lever
from 

class Level1:
    def __init__(self, player, resources):
        self.player = player
        self.resources = resources

        # Definisi obstacle: lantai + satu platform yang bisa dinaikkan
        self.obstacles = [
            pygame.Rect(0,   550, 800, 50),
            pygame.Rect(300, 450, 100, 20),
        ]

        # Batas target naik
        self.platform_target_y = 300

        # Load dan cache tile image
        self.block_img = resources.load_image("block")
        self.orig_w, _ = self.block_img.get_size()
        self._cache = {}

        # Buat lever di samping platform kedua
        lever_x = 200
        lever_y = 480
        self.lever = Lever((lever_x, lever_y), resources)

    def update(self, dt, keys, events):
        # Toggle lever saat tekan E
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                if self.lever.is_player_near(self.player.rect):
                    self.lever.toggle()

        # Animate platform
        plat = self.obstacles[1]
        if self.lever.active and plat.y > self.platform_target_y:
            plat.y -= int(100 * dt)
            if plat.y < self.platform_target_y:
                plat.y = self.platform_target_y
        elif not self.lever.active and plat.y < 450:
            plat.y += int(100 * dt)
            if plat.y > 450:
                plat.y = 450

    def draw(self, screen):
        # Tile semua obstacles dengan block.png
        def draw(self, screen):
            for rect in self.obstacles:
                # Hanya stretch vertikal
                h = rect.height
                # cache per-height untuk performa
                if h not in self._cache:
                    tile = pygame.transform.scale(self.block_img, (self.orig_w, h))
                    self._cache[h] = tile
                tile = self._cache[h]

                # hitung jumlah tile horizontal
                count = math.ceil(rect.width / self.orig_w)
                for i in range(count):
                    x = rect.x + i * self.orig_w
                    screen.blit(tile, (x, rect.y))

            self.lever.draw(screen)
