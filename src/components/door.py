import pygame

class Door:
    def __init__(self, pos, resources):
        self.image = resources.load_image("door")
        self.rect  = self.image.get_rect(topleft=pos)
        self.rect.bottom = self.rect.top
        self.rect.right = self.rect.left

    def draw(self, screen):
        screen.blit(self.image, self.rect)
