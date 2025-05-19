import pygame

class Lever:
    def __init__(self, pos, resources):
        # Muat dua state lever
        self.image_off = resources.load_image("lever_down")
        self.image_on  = resources.load_image("lever_up")
        self.image     = self.image_off
        self.rect      = self.image.get_rect(topleft=pos)
        self.active    = False

    def toggle(self):
        self.active = not self.active
        self.image  = self.image_on if self.active else self.image_off

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def is_player_near(self, player_rect, margin=20):
        return self.rect.inflate(margin, margin).colliderect(player_rect)
