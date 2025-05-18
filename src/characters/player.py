# src/characters/player.py
import pygame
from src.constants import GRAVITY, BOB_SPEED

class Player(pygame.sprite.Sprite):
    def __init__(self, image: pygame.Surface, start_pos: tuple[int,int]):
        super().__init__()
        self.image    = image
        self.rect     = image.get_rect(topleft=start_pos)
        self.velocity = pygame.math.Vector2(0,0)
        self.moving   = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.moving = not self.moving

    def update(self, static_blocks: list[pygame.Rect], movable_walls: list[pygame.Rect]):
        # gravity
        self.velocity.y += GRAVITY
        self.rect.y += int(self.velocity.y)
        for block in static_blocks + movable_walls:
            if self.rect.colliderect(block):
                if self.velocity.y > 0:
                    self.rect.bottom = block.top
                else:
                    self.rect.top = block.bottom
                self.velocity.y = 0

        # horizontal
        if self.moving:
            self.rect.x += BOB_SPEED
            for block in static_blocks + movable_walls:
                if self.rect.colliderect(block):
                    self.rect.right = block.left
                    self.moving = False
                    break

    def draw(self, surface: pygame.Surface):
        surface.blit(self.image, self.rect.topleft)
