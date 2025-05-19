import pygame
from pathlib import Path
from src.utils.resource_manager import ResourceManager
from src.characters.player import Player
from src.scene.main_menu   import MainMenu
from src.scene.level_select import LevelSelect
from src.scene.level1      import Level1
from src.scene.level2      import Level2
from src.scene.level3      import Level3 # Pastikan Level3 juga diimpor jika ada
from src.constants import *

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

        # Scenes dan level
        self.menu        = MainMenu(self.screen)
        self.level_sel   = LevelSelect(self.screen)
        self.level       = None # Inisialisasi level dan player sebagai None
        self.player      = None # Inisialisasi level dan player sebagai None

        # Font untuk pesan Level Clear/Game Over (opsional)
        self.font_large = pygame.font.SysFont(None, 72)
        self.font_medium = pygame.font.SysFont(None, 48)


    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000
            self._handle_events()
            self._update(dt)
            self._draw()

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
                elif choice == "Exit":
                    pygame.quit(); exit()

            elif self.state == Game.STATE_LEVEL_SELECT:
                choice = self.level_sel.handle_input(event)
                if choice in LEVELS:
                    # instantiate level & player
                    bob = self.resources.load_image("bob")
                    # self.player = Player((100, 500), bob) # Player akan diinisialisasi DI SINI
                    # Posisi awal pemain harus ditentukan oleh Level
                    # Kita akan set posisi pemain SAAT level dimuat
                    self.player = Player((0, 0), bob) # Buat instance player dengan posisi dummy dulu

                    # Pilih level yang sesuai dan set ke self.level
                    if choice == "Level 1":
                        self.level  = Level1(self.player, self.resources)
                    elif choice == "Level 2": # Jika Level 2 dipilih
                        self.level = Level2(self.player, self.resources) # Buat instance Level2
                    elif choice == "Level 3": # Jika Level 3 dipilih
                        self.level = Level3(self.player, self.resources) # Buat instance Level3

                    # Set posisi awal pemain berdasarkan posisi awal level
                    # Asumsi setiap Level memiliki atribut player_start_pos
                    # Jika tidak, Anda perlu menentukan posisi awal di sini secara manual per level
                    if hasattr(self.level, 'player_start_pos'):
                         self.player.rect.topleft = self.level.player_start_pos
                    else:
                         # Posisi default jika level tidak mendefinisikan player_start_pos
                         self.player.rect.topleft = (100, 500)


                    self.state  = Game.STATE_PLAYING # Masuk ke state Playing SETELAH level dan player diinisialisasi
                elif choice == "Back":
                    self.state = Game.STATE_MENU

            elif self.state == Game.STATE_PLAYING:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                         self.state = Game.STATE_OPTION # Contoh: pause game dengan P

            elif self.state == Game.STATE_OPTION:
                 if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                      self.state = Game.STATE_MENU # Keluar dari options ke menu

            elif self.state == Game.STATE_GAMEOVER:
                 if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                      self.state = Game.STATE_MENU # Kembali ke menu setelah Game Over

            elif self.state == Game.STATE_LEVEL_CLEAR:
                 # Saat Level Clear dan ESC ditekan, kembali ke LAYAR PEMILIHAN LEVEL
                 if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                      self.state = Game.STATE_LEVEL_SELECT # Kembali ke Level Select


    def _update(self, dt):
        # Update game logic berdasarkan state saat ini
        if self.state == Game.STATE_PLAYING:
            # --- Tambahkan pemeriksaan ini ---
            # Hanya update player dan level jika keduanya sudah diinisialisasi
            if self.player is not None and self.level is not None:
                keys = pygame.key.get_pressed()
                self.player.handle_input(keys)
                # Update player, berikan obstacles dari the current level
                # Line di bawah ini yang menyebabkan error jika self.level None
                self.player.update(dt, self.level.obstacles)

                # Update the level, providing dt and player's rect
                # Level.update() requires player_rect (sesuai perbaikan sebelumnya)
                self.level.update(dt, self.player.rect)

                # Check level completion condition (Level Clear)
                # Use getattr to safely check the 'completed' property
                if getattr(self.level, 'completed', False):
                     # Langsung ganti state ke Level Clear untuk menampilkan pesan
                     self.state = Game.STATE_LEVEL_CLEAR
                     print("Level Clear!") # Debugging print


                # Check Game Over condition (player falling off screen)
                # Hanya cek jika player object exists
                elif self.player.rect.top > SCREEN_HEIGHT + 50: # Beri sedikit toleransi sebelum Game Over
                    self.state = Game.STATE_GAMEOVER
                    print("Game Over!") # Debugging print
            # --- Akhir pemeriksaan ---
            # Jika self.player atau self.level adalah None saat state PLAYING, tidak ada update yang terjadi.


    def _draw(self):
        # Gambar sesuai state game saat ini
        if self.state == Game.STATE_MENU:
            self.screen.fill(COLOR_BROWN) # Pastikan layar dibersihkan
            self.menu.draw()
        elif self.state == Game.STATE_LEVEL_SELECT:
            self.screen.fill(COLOR_BROWN) # Pastikan layar dibersihkan
            self.level_sel.draw()
        elif self.state == Game.STATE_PLAYING:
            self.screen.fill(COLOR_SKY) # Warna latar belakang langit
            # Hanya gambar jika level dan player ada
            if self.level is not None and self.player is not None:
                 self.level.draw(self.screen) # Level menggambar elemennya
                 self.player.draw(self.screen) # Gambar pemain
            else:
                 # Opsional: Gambar layar loading atau kosong jika level belum siap
                 self.screen.fill(COLOR_BLACK) # Layar hitam jika belum siap


        elif self.state == Game.STATE_OPTION:
            self.screen.fill((50, 50, 50))  # Latar abu-abu untuk options
            # Tambahkan elemen UI options di sini
            # Gambar teks indikator kembali
            surf_inst = self.font_medium.render("Press ESC to return to Menu", True, COLOR_WHITE)
            rect_inst = surf_inst.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
            self.screen.blit(surf_inst, rect_inst)


        elif self.state == Game.STATE_GAMEOVER:
            self.screen.fill((0, 0, 0)) # Latar hitam
            # Gambar teks Game Over
            surf = self.font_large.render("Game Over", True, COLOR_WHITE)
            rect = surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 30))
            self.screen.blit(surf, rect)
            surf_inst = self.font_medium.render("Press ESC to return to Menu", True, COLOR_WHITE)
            rect_inst = surf_inst.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20))
            self.screen.blit(surf_inst, rect_inst)

        elif self.state == Game.STATE_LEVEL_CLEAR:
            self.screen.fill(COLOR_SKY) # Latar langit atau warna lain
            # Gambar teks Level Clear
            surf = self.font_large.render("Level Clear!", True, COLOR_WHITE)
            rect = surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 30))
            self.screen.blit(surf, rect)
            surf_inst = self.font_medium.render("Press ESC to return to Level Select", True, COLOR_WHITE) # Teks instruksi
            rect_inst = surf_inst.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20))
            self.screen.blit(surf_inst, rect_inst)
            # Tambahkan tombol atau instruksi lain di sini


        pygame.display.flip() # Update layar