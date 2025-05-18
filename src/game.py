# src/game.py
import pygame
from src.constants import BLACK
from src.characters.player import Player
from src.scene.level1   import Level1  # import Level 1
from src.scene.level2 import Level2 # Import Level 2

class Game:
    def __init__(self, screen: pygame.Surface, images: dict):
        self.screen      = screen
        self.images      = images
        self.player: Player | None = None

        # level data & objects
        self.current_level = None
        self.level_completed = False

    # Modifikasi metode start_level untuk mengenali level_num = 2
    def start_level(self, level_num: int) -> bool:
        if level_num == 1:
            self.current_level = Level1(self.images)
        elif level_num == 2: # Tambahkan blok ini untuk Level 2
            self.current_level = Level2(self.images)
        else:
            print(f"Level {level_num} not implemented.")
            return False

        # instantiate player at the level’s start
        start_pos = self.current_level.player_start
        self.player = Player(self.images['bob'], start_pos)

        self.level_completed = False
        return True

    # Signature handle_event di kelas Game tetap tidak berubah
    def handle_event(self, event: pygame.event.Event):
        if self.player:
            self.player.handle_event(event)
        # also forward event to level (for levers, etc.), PASSING THE PLAYER
        if self.current_level:
            # Panggilan ini meneruskan objek player ke level
            self.current_level.handle_event(event, self.player)


    # Metode update - memastikan player diteruskan ke level.update
    def update(self):
        if not self.player or not self.current_level:
            return
        # update player (physics & collisions)
        self.player.update(
            self.current_level.static_obstacles,
            self.current_level.movable_walls
        )
        # update level (e.g. moving platforms), PASSING THE PLAYER
        # Panggilan ini meneruskan objek player ke update level
        self.current_level.update(self.player)

        # check for level completion (player reaches door)
        if self.player.rect.colliderect(self.current_level.door_rect):
            self.level_completed = True # Set level_completed jika player mencapai pintu
            # Opsi: Reset level_completed setelah beralih state di main.py jika diinginkan


    def draw(self):
        # clear
        # Gunakan warna latar level, fallback ke hitam
        self.screen.fill(self.current_level.background_color or BLACK)
        # draw static & moving blocks
        self.current_level.draw(self.screen, self.images['block'])
        # draw levers, etc.
        self.current_level.draw_overlays(self.screen, self.images)
        # draw player & door
        if self.player:
            self.player.draw(self.screen)
        # Gambar pintu
        self.screen.blit(self.images['door'], self.current_level.door_rect.topleft)
