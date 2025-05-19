import pygame
from src.components.lever import Lever
from src.components.door import Door

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
            pygame.Rect(300, 530, 200, 20),
            pygame.Rect(525, 350, 280, 200)
        ]
        
        self.platform_target_y = 300
        self.completed = False

        # Load dan cache tile image
        self.block_img = resources.load_image("block")

        plat_rect = self.obstacles[1]
        lever_x = 100
        lever_y = 480
        self.lever = Lever((lever_x, lever_y), resources)

        door_x = 800
        door_y = 350
        self.door  = Door((door_x, door_y), resources)
        
    def update(self, dt, keys, events):
        # Toggle lever saat tekan E
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                if self.lever.is_player_near(self.player.rect):
                    self.lever.toggle()

        # Animate platform: naik ke target jika aktif, turun ke posisi awal jika tidak
        plat = self.obstacles[1]
        old_y = plat.y
        start_y = self.obstacles[0].top - plat.height  # ground_top - height
        
        if self.lever.active:
        # naik
            new_y = max(self.platform_target_y, plat.y - int(100 * dt))
        else:
            if abs(self.player.rect.bottom - plat.y) < 2:
                new_y = plat.y
            else:
                new_y = min(start_y, plat.y + int(100 * dt))
        
        temp_rect = plat.copy()
        temp_rect.y = new_y
        if temp_rect.colliderect(self.player.rect):
            if new_y < old_y:
                pass
            else:
                new_y = self.player.rect.top - plat.height
                self.lever.active = False
        
        delta_y = new_y - old_y
        plat.y = new_y
        
        if abs(self.player.rect.bottom - old_y) < 2 or (delta_y > 0 and self.lever.active):
            self.player.rect.y += delta_y
        
        if getattr(self, "door", None) and self.player.rect.colliderect(self.door.rect):
            self.completed = True
            
        # Tile semua obstacles dengan block.png
    def draw(self, screen):
        for rect in self.obstacles:
            scaled = pygame.transform.scale(self.block_img, (rect.width, rect.height))
            screen.blit(scaled, rect.topleft)

        # Gambar lever di atas
        self.lever.draw(screen)
        self.door.draw(screen)
