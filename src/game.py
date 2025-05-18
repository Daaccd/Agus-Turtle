# src/game.py
import pygame
from src.constants import BLACK
from src.characters.player import Player
from src.scene.level1   import Level1  # import other levels as you add them

class Game:
    def __init__(self, screen: pygame.Surface, images: dict):
        self.screen      = screen
        self.images      = images
        self.player: Player | None = None

        # level data & objects
        self.current_level = None
        self.level_completed = False

    def start_level(self, level_num: int) -> bool:
        if level_num == 1:
            self.current_level = Level1(self.images)
        else:
            print(f"Level {level_num} not implemented.")
            return False

        # instantiate player at the level’s start
        start_pos = self.current_level.player_start
        self.player = Player(self.images['bob'], start_pos)

        self.level_completed = False
        return True

    def handle_event(self, event: pygame.event.Event):
        if self.player:
            self.player.handle_event(event)
        # also forward event to level (for levers, etc.)
        if self.current_level:
            self.current_level.handle_event(event)

    def update(self):
        if not self.player or not self.current_level:
            return
        # update player (physics & collisions)
        self.player.update(
            self.current_level.static_obstacles,
            self.current_level.movable_walls
        )
        # update level (e.g. moving platforms)
        self.current_level.update()

        # check for level completion (player reaches door)
        if self.player.rect.colliderect(self.current_level.door_rect):
            self.level_completed = True

    def draw(self):
        # clear
        self.screen.fill(self.current_level.background_color or BLACK)
        # draw static & moving blocks
        self.current_level.draw(self.screen, self.images['block'])
        # draw levers, etc.
        self.current_level.draw_overlays(self.screen, self.images)
        # draw player & door
        if self.player:
            self.player.draw(self.screen)
        self.screen.blit(self.images['door'], self.current_level.door_rect.topleft)
