# src/game.py

import pygame
from pathlib import Path
from src.utils.resource_manager import ResourceManager
from src.characters.player import Player
from src.scene.main_menu import MainMenu
from src.scene.level_select import LevelSelect
from src.scene.level1 import Level1
from src.scene.level2 import Level2
from src.scene.level3 import Level3
from src.constants import *
from src.scene.option_menu import OptionMenu

class Game:
    STATE_MENU        = 0
    STATE_LEVEL_SELECT= 1
    STATE_PLAYING     = 2
    STATE_OPTION      = 3
    STATE_GAMEOVER    = 4
    STATE_LEVEL_CLEAR = 5

    def __init__(self, screen):
        self.screen = screen
        self.clock  = pygame.time.Clock()
        self.state  = Game.STATE_MENU

        # Resource Manager
        base_dir = Path(__file__).resolve().parent.parent
        img_dir  = base_dir / IMAGES_DIR
        self.resources = ResourceManager(img_dir)

        # Muat semua SFX di awal
        self.sfx_jump  = self.resources.load_sound("jump")
        self.sfx_lever = self.resources.load_sound("lever")
        self.sfx_level_clear = self.resources.load_sound("game_clear")
        self.sfx_game_over   = self.resources.load_sound("game_over")
        self.sfx_key_pickup = self.resources.load_sound("key_pickup")
        self.sfx_lock_open = self.resources.load_sound("lock_open")

        # Muat musik BGM
        self.bgm_main_menu = "main_menu_bgm"
        self.bgm_game_play = "game_play_bgm"

        # Pengaturan Volume Awal
        self.master_volume = 0.5
        pygame.mixer.music.set_volume(self.master_volume)

        # >>> TAMBAHKAN BARIS INI <<<
        self.current_bgm = None # Inisialisasi variabel untuk melacak BGM yang sedang diputar
        # >>> AKHIR TAMBAH <<<

        self._play_bgm(self.bgm_main_menu)

        # Scenes dan level
        self.menu        = MainMenu(self.screen)
        self.level_sel   = LevelSelect(self.screen)
        self.option_menu = OptionMenu(self.screen)
        self.level       = None
        self.player      = None

        # Font
        self.font_large = pygame.font.SysFont(None, 72)
        self.font_medium = pygame.font.SysFont(None, 48)

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000
            self._handle_events()
            self._update(dt)
            self._draw()

    def _play_bgm(self, bgm_name: str):
        """Fungsi pembantu untuk memainkan BGM."""
        # Jika musik yang diminta sudah diputar, jangan lakukan apa-apa
        if self.current_bgm == bgm_name and pygame.mixer.music.get_busy():
            return

        if self.resources.load_music(bgm_name):
            pygame.mixer.music.play(-1)
            pygame.mixer.music.set_volume(self.master_volume)
            # >>> TAMBAHKAN BARIS INI <<<
            self.current_bgm = bgm_name # Perbarui BGM yang sedang diputar
            # >>> AKHIR TAMBAH <<<
        else:
            print(f"Warning: BGM {bgm_name} tidak dapat dimuat atau dimainkan.")

    def _stop_bgm(self):
        """Fungsi pembantu untuk menghentikan BGM."""
        pygame.mixer.music.stop()
        # >>> TAMBAHKAN BARIS INI <<<
        self.current_bgm = None # Atur BGM saat ini menjadi None ketika dihentikan
        # >>> AKHIR TAMBAH <<<

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if self.state == Game.STATE_MENU:
                choice = self.menu.handle_input(event)
                if choice == "Start Game":
                    self.state = Game.STATE_LEVEL_SELECT
                elif choice == "Options":
                    self.state = Game.STATE_OPTION
                    self.option_menu.selected = 0
                    self.master_volume = pygame.mixer.music.get_volume()
                elif choice == "Exit":
                    pygame.quit(); exit()

            elif self.state == Game.STATE_LEVEL_SELECT:
                choice = self.level_sel.handle_input(event)
                if choice in LEVELS:
                    bob = self.resources.load_image("bob")
                    self.player = Player((0, 0), bob, sfx_jump=self.sfx_jump)
                    if choice == "Level 1":
                        self.level  = Level1(self.player, self.resources, sfx_lever=self.sfx_lever)
                    elif choice == "Level 2":
                        self.level = Level2(self.player, self.resources, sfx_lever=self.sfx_lever)
                    elif choice == "Level 3":
                        self.level = Level3(self.player, self.resources,
                                            sfx_lever=self.sfx_lever,
                                            sfx_key_pickup=self.sfx_key_pickup,
                                            sfx_lock_open=self.sfx_lock_open)

                    if hasattr(self.level, 'player_start_pos'):
                         self.player.rect.topleft = self.level.player_start_pos
                    else:
                         self.player.rect.topleft = (100, 500)

                    self._stop_bgm()
                    self._play_bgm(self.bgm_game_play)
                    self.state  = Game.STATE_PLAYING

                elif choice == "Back":
                    self.state = Game.STATE_MENU
                    # >>> BARIS YANG DIMODIFIKASI <<<
                    if not pygame.mixer.music.get_busy() or self.current_bgm != self.bgm_main_menu:
                        self._stop_bgm()
                        self._play_bgm(self.bgm_main_menu)
                    # >>> AKHIR MODIFIKASI <<<

            elif self.state == Game.STATE_PLAYING:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                         self.state = Game.STATE_OPTION
                         self.option_menu.selected = 0
                         self.master_volume = pygame.mixer.music.get_volume()

            elif self.state == Game.STATE_OPTION:
                result = self.option_menu.handle_input(event)
                if result == "Back":
                    self.state = Game.STATE_MENU
                    self.master_volume = pygame.mixer.music.get_volume()
                    # >>> BARIS YANG DIMODIFIKASI <<<
                    if not pygame.mixer.music.get_busy() or self.current_bgm != self.bgm_main_menu:
                        self._stop_bgm()
                        self._play_bgm(self.bgm_main_menu)
                    # >>> AKHIR MODIFIKASI <<<

            elif self.state == Game.STATE_GAMEOVER:
                 if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                      self.state = Game.STATE_MENU
                      # >>> BARIS YANG DIMODIFIKASI <<<
                      if not pygame.mixer.music.get_busy() or self.current_bgm != self.bgm_main_menu:
                          self._stop_bgm()
                          self._play_bgm(self.bgm_main_menu)
                      # >>> AKHIR MODIFIKASI <<<
                      self.level = None
                      self.player = None

            elif self.state == Game.STATE_LEVEL_CLEAR:
                 if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                      self.state = Game.STATE_LEVEL_SELECT
                      # >>> BARIS YANG DIMODIFIKASI <<<
                      if not pygame.mixer.music.get_busy() or self.current_bgm != self.bgm_main_menu:
                          self._stop_bgm()
                          self._play_bgm(self.bgm_main_menu)
                      # >>> AKHIR MODIFIKASI <<<
                      self.level = None
                      self.player = None

    def _update(self, dt):
       if self.state == Game.STATE_PLAYING:
           if self.player is not None and self.level is not None:
               keys = pygame.key.get_pressed()
               self.player.handle_input(keys)
               self.player.update(dt, self.level.obstacles)

               self.level.update(dt, self.player.rect)

               if getattr(self.level, 'completed', False):
                    self._stop_bgm()
                    if self.sfx_level_clear:
                        self.sfx_level_clear.play()
                    self.state = Game.STATE_LEVEL_CLEAR
                    print("Level Clear!")

               elif self.player.rect.top > SCREEN_HEIGHT + 50:
                   self._stop_bgm()
                   if self.sfx_game_over:
                       self.sfx_game_over.play()
                   self.state = Game.STATE_GAMEOVER
                   print("Game Over!")
       elif self.state == Game.STATE_OPTION:
           self.option_menu.update()

    def _draw(self):
       if self.state == Game.STATE_MENU:
           self.screen.fill(COLOR_BROWN)
           self.menu.draw()
       elif self.state == Game.STATE_LEVEL_SELECT:
           self.screen.fill(COLOR_BROWN)
           self.level_sel.draw()
       elif self.state == Game.STATE_PLAYING:
           self.screen.fill(COLOR_SKY)
           if self.level is not None and self.player is not None:
                self.level.draw(self.screen)
                self.player.draw(self.screen)
           else:
                self.screen.fill((0,0,0))


       elif self.state == Game.STATE_OPTION:
            self.option_menu.draw()

       elif self.state == Game.STATE_GAMEOVER:
           self.screen.fill((0, 0, 0))
           surf = self.font_large.render("Game Over", True, COLOR_WHITE)
           rect = surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 30))
           self.screen.blit(surf, rect)
           surf_inst = self.font_medium.render("Press ESC to return to Menu", True, COLOR_WHITE)
           rect_inst = surf_inst.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20))
           self.screen.blit(surf_inst, rect_inst)

       elif self.state == Game.STATE_LEVEL_CLEAR:
           self.screen.fill(COLOR_SKY)
           surf = self.font_large.render("Level Clear!", True, COLOR_WHITE)
           rect = surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 30))
           self.screen.blit(surf, rect)
           surf_inst = self.font_medium.render("Press ESC to return to Level Select", True, COLOR_WHITE)
           rect_inst = surf_inst.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20))
           self.screen.blit(surf_inst, rect_inst)

       pygame.display.flip()