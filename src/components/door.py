import pygame

class Door:
    def __init__(self, pos, resources):
        """
        pos: tuple(x, y) untuk top-left door
        resources: ResourceManager instance
        """
        # Muat sprite door.png
        self.image = resources.load_image("door")
        self.rect  = self.image.get_rect(topleft=pos)
        self.rect.bottom = self.rect.top
        self.rect.right = self.rect.left

    def draw(self, screen):
        screen.blit(self.image, self.rect)
