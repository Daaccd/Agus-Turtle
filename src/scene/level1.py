# src/scene/level1.py
import pygame
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT, BLUE_SKY, MOVABLE_WALL_SPEED

# 100(lokasi dari kiri, -100(lokasi dari bawah), 100(lebar), 100(tinggi))

class Level1:
    def __init__(self, images: dict):
        # define where the player starts
        self.wall_should_move = False  # Start as False
        self.player_start      = (50, SCREEN_HEIGHT - 100)
        self.wall_initial_y = SCREEN_HEIGHT - 50
        self.wall_target_y  = SCREEN_HEIGHT - 300

        # static ground/platforms
        floor = pygame.Rect(0, SCREEN_HEIGHT-50, SCREEN_WIDTH, 50)
        self.static_obstacles = [floor]
        # 100(lokasi dari kiri, - 100(lokasi dari bawah), 100(lebar), 100(tinggi))
        # moving wall (platform)
        wall_rect = pygame.Rect(400, SCREEN_HEIGHT - 50, 400, 50)
        self.movable_walls    = [wall_rect]

        self.wall_speed       = MOVABLE_WALL_SPEED

        # lever to trigger the wall
        self.lever_rect       = pygame.Rect(300, SCREEN_HEIGHT - 100, 200, 50)
        self.lever_state      = 'up'
        # 100(lokasi dari kiri, - 100(lokasi dari bawah), 100(lebar), 100(tinggi))
        # exit door
        self.door_rect        = pygame.Rect(SCREEN_WIDTH-80, SCREEN_HEIGHT-400, 50, 80)

        self.background_color = BLUE_SKY

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.lever_rect.collidepoint(event.pos):
            self.lever_state = 'down' if self.lever_state == 'up' else 'up'
            self.wall_should_move = True  # Allow wall to move only after lever clicked


    def update(self):
        if not self.wall_should_move:
            return  # Don't move wall yet

        target = self.wall_target_y if self.lever_state == 'down' else self.wall_initial_y
        for wall in self.movable_walls:
            if wall.top < target:
                wall.top += self.wall_speed
            elif wall.top > target:
                wall.top -= self.wall_speed


    def draw(self, screen: pygame.Surface, block_image: pygame.Surface):
        # tile static & movable blocks
        for rect in self.static_obstacles + self.movable_walls:
            w,h = block_image.get_size()
            for x in range(rect.left, rect.right, w):
                for y in range(rect.top, rect.bottom, h):
                    screen.blit(block_image, (x,y))

    def draw_overlays(self, screen: pygame.Surface, images: dict):
        # draw lever
        img = images['lever_down'] if self.lever_state=='down' else images['lever_up']
        screen.blit(img, self.lever_rect.topleft)
