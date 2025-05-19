import pygame
from pathlib import Path
from src.utils.resource_manager import ResourceManager
from src.characters.player   import Player
from src.scene.main_menu     import MainMenu
from src.scene.level_select  import LevelSelect
from src.scene.level1        import Level1
from src.constants           import *

class Game:
    STATE_MENU         = 0
    STATE_LEVEL_SELECT = 1
    STATE_PLAYING      = 2
    STATE_OPTION       = 3
    STATE_GAMEOVER     = 4

    def __init__(self, screen):
        self.screen    = screen
        self.clock     = pygame.time.Clock()
        self.state     = Game.STATE_MENU

        # ResourceManager
        base_dir       = Path(__file__).resolve().parent.parent
        img_dir        = base_dir / IMAGES_DIR
        self.resources = ResourceManager(img_dir)

        # Scene instances (belum ada player/level sampai dipilih)
        self.menu      = MainMenu(self.screen)
        self.level_sel = LevelSelect(self.screen)
        self.player    = None
        self.level     = None

        # buffer event per frame
        self.events    = []

    def run(self):
        while True:
            dt          = self.clock.tick(FPS) / 1000
            self.events = pygame.event.get()
            self._handle_events()
            self._update(dt)
            self._draw()

    def _handle_events(self):
        for event in self.events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if self.state == Game.STATE_MENU:
                choice = self.menu.handle_input(event)
                if choice == "Start Game":
                    self.state = Game.STATE_LEVEL_SELECT
                elif choice == "Options":
                    self.state = Game.STATE_OPTION
                elif choice == "Exit":
                    pygame.quit()
                    exit()

            elif self.state == Game.STATE_LEVEL_SELECT:
                choice = self.level_sel.handle_input(event)
                if choice in LEVELS:
                    # instansiasi player & level
                    bob_sprite    = self.resources.load_image("bob")
                    self.player   = Player((100, 500), bob_sprite)
                    self.level    = Level1(self.player, self.resources)
                    self.state    = Game.STATE_PLAYING
                elif choice == "Back":
                    self.state = Game.STATE_MENU

            elif self.state == Game.STATE_OPTION:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.state = Game.STATE_MENU

    def _update(self, dt):
        if self.state == Game.STATE_PLAYING and self.player and self.level:
            keys = pygame.key.get_pressed()
            # input ke player
            self.player.handle_input(keys)

            # 2) Update posisi & collision pemain
            self.player.update(dt, self.level.obstacles)
            # 3) Update logika level (lever, animasi platform, dll.)
            self.level.update(dt, keys, self.events)
            
            if getattr(self.level, "completed", False):
                self.state = Game.STATE_LEVEL_SELECT
            
            # cek game over
            if self.player.rect.top > SCREEN_HEIGHT:
                self.state = Game.STATE_GAMEOVER

    def _draw(self):
        if self.state == Game.STATE_MENU:
            self.menu.draw()

        elif self.state == Game.STATE_LEVEL_SELECT:
            self.level_sel.draw()

        elif self.state == Game.STATE_PLAYING:
            self.screen.fill(COLOR_SKY)
            self.level.draw(self.screen)
            self.player.draw(self.screen)

        elif self.state == Game.STATE_OPTION:
            self.screen.fill((50, 50, 50))  # placeholder

        elif self.state == Game.STATE_GAMEOVER:
            self.screen.fill((0, 0, 0))
            font = pygame.font.SysFont(None, 72)
            surf = font.render("Game Over - Esc to Menu", True, COLOR_WHITE)
            rect = surf.get_rect(center=self.screen.get_rect().center)
            self.screen.blit(surf, rect)

        pygame.display.flip()
