import pygame, math
from src.constants import COLOR_BROWN
from src.components.lever import Lever
from src.utils.resource_manager import ResourceManager

class Level1:
    def __init__(self, player, resources):
        self.player = player
        self.resources = resources

        # Definisi obstacle: lantai + satu platform yang bisa dinaikkan
        ground_rect = pygame.Rect(0, 550, 800, 50)
        ground_top  = ground_rect.top  # 550

        # Obstacle: ground + platform
        self.obstacles = [
            ground_rect,
            # Mulai platform tepat di atas ground
            pygame.Rect(300, 550, 200, 20),
        ]
        
        self.platform_target_y = 300

        # Load dan cache tile image
        self.block_img = resources.load_image("block")
        # self.orig_w, _ = self.block_img.get_size()
        
        self._cache = {}

        # Buat lever di samping platform
        plat_rect = self.obstacles[1]
        lever_x = 100
        # Pastikan lever berdiri tepat di atas platform
        lever_y = 480
        self.lever = Lever((lever_x, lever_y), resources)

    def update(self, dt, keys, events):
        # Toggle lever saat tekan E
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                if self.lever.is_player_near(self.player.rect):
                    self.lever.toggle()

        # Animate platform: naik ke target jika aktif, turun ke posisi awal jika tidak
        plat = self.obstacles[1]
        start_y = self.obstacles[0].top - plat.height  # ground_top - height
        if self.lever.active and plat.y > self.platform_target_y:
            plat.y -= int(100 * dt)
            if plat.y < self.platform_target_y:
                plat.y = self.platform_target_y
        elif not self.lever.active and plat.y < start_y:
            plat.y += int(100 * dt)
            if plat.y > start_y:
                plat.y = start_y
            
        # Tile semua obstacles dengan block.png
    def draw(self, screen):
        for rect in self.obstacles:
            scaled = pygame.transform.scale(self.block_img, (rect.width, rect.height))
            screen.blit(scaled, rect.topleft)

        # Gambar lever di atas
        self.lever.draw(screen)
