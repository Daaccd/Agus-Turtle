import pygame
from src.constants import COLOR_BROWN
from src.utils.resource_manager import ResourceManager

class Level1:
    def __init__(self, player, resources):
        self.player = player
        self.resources = resources
        self.obstacles = [
            pygame.Rect(0, 550, 800, 50),   # lantai
            pygame.Rect(300, 450, 100, 20), # platform
        ]
        self.block_img = self.resources.load_image("block")

    def update(self, dt):
        pass

    def draw(self, screen):
        for rect in self.obstacles:
            scaled_img = pygame.transform.scale(self.block_img, (rect.width, rect.height))
            screen.blit(scaled_img, rect.topleft)