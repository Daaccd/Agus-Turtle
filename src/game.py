# game.py

import pygame
import math

# Import konstanta dari constants.py
from .constants import *

class Game:
    # Tambahkan parameter gambar tuas di konstruktor
    def __init__(self, screen, bob_image, block_image, lever_up_image, lever_down_image, door_image):
        """
        Inisialisasi objek Game.
        screen: Permukaan layar Pygame.
        bob_image: Surface gambar Bob.
        block_image: Surface gambar block.
        lever_up_image: Surface gambar tuas up.
        lever_down_image: Surface gambar tuas down.
        """
        self.screen = screen
        self.bob_image = bob_image
        self.block_image = block_image
        self.door_image = door_image
        # Simpan gambar tuas dalam dictionary
        self.lever_images = {'up': lever_up_image, 'down': lever_down_image}

        # Variabel status Bob
        self.bob_x = 0
        self.bob_y = 0
        self.bob_speed = BOB_SPEED
        self.bob_direction = 1
        self.bob_is_moving = False
        self.bob_vertical_speed = 0
        self.bob_on_ground = False
        self.bob_rect = None

        # Variabel status level
        self.current_level_num = None
        self.background_color = BLACK
        self.static_obstacles = []
        self.movable_wall = None
        self.lever = None
        self.exit_zone = None 
        
        # Variabel baru untuk exit zone dan status selesai
        self.exit_zone = None      # <-- Rect untuk zona keluar
        self.level_completed = False # <-- Status apakah level sudah selesai

        # Variabel untuk objek di level
        self.static_obstacles = [] # Daftar Rect untuk obstacle statis
        self.movable_wall = None    # Dictionary untuk obstacle bergerak { 'rect': Rect, 'initial_y_top': int, 'target_y_top': int, 'is_moving': bool }
        self.lever = None           # Dictionary untuk tuas { 'rect': Rect, 'state': 'up' or 'down' }
        self.movable_wall_speed = MOVABLE_WALL_SPEED # Kecepatan obstacle bergerak dari konstanta

        # Data Level (Diubah strukturnya)
        self.level_data = {
            1: {
                'bob_start_pos': (50, SCREEN_HEIGHT - 50),
                # Obstacle statis dipisah
                'static_obstacles': [
                    # Alas lantai (ukuran disesuaikan dengan block_image atau ditiling di draw)
                    pygame.Rect(0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50),
                  #{ 'rect': pygame.Rect(0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50), 'image': IMAGE_KEY_BLOCK, 'tiled': True },
                    # Tambahkan obstacle statis lain di sini
                ],
                 # Obstacle bergerak didefinisikan terpisah
                'movable_wall': {
                    # Rect: (posisi_x_kiri, posisi_y_atas, lebar, tinggi)
                    'rect': pygame.Rect(400, SCREEN_HEIGHT - 150, 1000, 100), # Posisi dan ukuran awal
                    # Target Y (atas) saat bergerak turun
                    'target_y_top': SCREEN_HEIGHT - 50, # Akan turun sampai pas di atas lantai
                },
                
                # Tuas didefinisikan terpisah
                'lever': {
                    # Rect: (posisi_x_kiri, posisi_y_atas, lebar, tinggi)
                    'rect': pygame.Rect(300, SCREEN_HEIGHT - 70, 70, 70), # Posisi dan ukuran visual tuas
                },
                'door': { # <-- Definisi objek pintu
                    # Rect: (posisi_x_kiri, posisi_y_atas, lebar, tinggi)
                    # Sesuaikan ukuran Rect ini dengan ukuran gambar door.png yang kamu miliki
                    'rect': pygame.Rect(SCREEN_WIDTH - 80, SCREEN_HEIGHT - 180, 70, 70), # Contoh posisi dan ukuran pintu
                },
                'background_color': BLUE_SKY,
                'exit_zone': pygame.Rect(SCREEN_WIDTH - 50, 0, 50, SCREEN_HEIGHT)
            }
            # Tambahkan level lain di sini
        }

    def start_level(self, level_num):
        """Memuat dan memulai level tertentu."""
        if level_num not in self.level_data:
            print(f"Error: Level {level_num} tidak ditemukan.")
            # Reset status game jika level tidak valid? Atau biarkan di menu?
            # Untuk saat ini, biarkan status game tetap, tapi tidak memuat level.
            return False # Gagal memulai level

        level = self.level_data[level_num]
        self.current_level_num = level_num
        
        # Reset status selesai level
        self.level_completed = False # <-- Reset saat memulai level baru

        # Set posisi awal Bob
        self.bob_x, self.bob_y = level['bob_start_pos']
        self.bob_is_moving = False # Mulai berhenti
        self.bob_vertical_speed = 0
        self.bob_on_ground = False
        self.bob_rect = self.bob_image.get_rect()
        self.bob_rect.center = (int(self.bob_x), int(self.bob_y))
        
        # Muat data pintu
        door_data = level.get('door')
        if door_data:
            self.door = { 'rect': door_data['rect'].copy() }
        else:
            self.door = None

        # Muat obstacle statis
        self.static_obstacles = level.get('static_obstacles', []) # Gunakan .get dengan default []

        # Muat data obstacle bergerak dan inisialisasi statusnya
        movable_wall_data = level.get('movable_wall')
        if movable_wall_data:
             self.movable_wall = {
                 'rect': movable_wall_data['rect'].copy(), # Gunakan copy agar Rect asli di level_data tidak berubah
                 'initial_y_top': movable_wall_data['rect'].top, # Simpan posisi Y awal
                 'target_y_top': movable_wall_data['target_y_top'],
                 'is_moving': False, # Awalnya tidak bergerak
             }
        else:
            self.movable_wall = None # Pastikan None jika tidak ada di level_data

        # Muat data tuas dan inisialisasi statusnya
        lever_data = level.get('lever')
        if lever_data:
            self.lever = {
                'rect': lever_data['rect'].copy(), # Gunakan copy
                'state': 'up', # Awalnya tuas dalam posisi 'up'
            }
        else:
            self.lever = None # Pastikan None jika tidak ada di level_data
            
        # Muat data exit zone
        


        self.background_color = level['background_color']

        print(f"Memulai Level {level_num}")
        return True


    def handle_event(self, event):
        """Menangani event yang relevan dengan state PLAYING (misal: klik pada Bob, klik tuas)."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            # Tangani klik pada Bob
            if self.bob_rect and self.bob_rect.collidepoint(mouse_pos):
                 self.bob_is_moving = not self.bob_is_moving
                 print(f"Bob is now moving: {self.bob_is_moving}")
                 return True # Event ditangani

            # Tangani klik pada Tuas jika tuas ada
            if self.lever and self.lever['rect'].collidepoint(mouse_pos):
                 print("Tuas diklik!")
                 # Periksa status tuas
                 if self.lever['state'] == 'up':
                     self.lever['state'] = 'down' # Ubah status visual tuas
                     print("Status tuas: down")
                     # Picu pergerakan movable wall jika ada dan belum bergerak
                     if self.movable_wall:
                         self.movable_wall['current_target_y'] = self.movable_wall['target_y_top']
                         self.movable_wall['is_moving'] = True # Picu pergerakan
                         print(f"Movable wall menarget Y={self.movable_wall['current_target_y']} (turun)")
                 elif self.lever['state'] == 'down':
                     self.lever['state'] = 'up' # Ubah status visual ke 'up'
                     print("Status tuas: up")
                     # Set target posisi movable wall ke posisi atas (initial_y_top)
                     if self.movable_wall:
                          self.movable_wall['current_target_y'] = self.movable_wall['initial_y_top'] # Target kembali ke posisi awal (atas)
                          self.movable_wall['is_moving'] = True # Picu pergerakan
                          print(f"Movable wall menarget Y={self.movable_wall['current_target_y']} (naik)")

                 return True # Event ditangani

        return False # Event tidak ditangani


    def update(self):
        """Mengupdate logika game (gravitasi, pergerakan Bob, tabrakan, pergerakan obstacle)."""
        if not self.bob_rect:
            return

        self.bob_rect.center = (int(self.bob_x), int(self.bob_y))

        # --- Terapkan Gravitasi pada Bob ---
        self.bob_vertical_speed += GRAVITY

        # --- Hitung Perubahan Posisi Bob yang Diinginkan ---
        delta_x = self.bob_speed * self.bob_direction if self.bob_is_moving else 0
        delta_y = self.bob_vertical_speed

        # --- Terapkan Pergerakan Vertikal Bob dan Cek Tabrakan Y ---
        self.bob_y += delta_y
        self.bob_rect.centery = int(self.bob_y)

        vertical_collision = False
        landed_on_obstacle = None

        # Cek tabrakan vertikal dengan obstacle STATIS
        for obstacle_rect in self.static_obstacles:
            if self.bob_rect.colliderect(obstacle_rect):
                 if self.bob_vertical_speed > 0: # Jika Bob jatuh dan bertabrakan
                    vertical_collision = True
                    landed_on_obstacle = obstacle_rect
                    break

        # Cek tabrakan vertikal dengan obstacle BERGERAK jika ada
        if not vertical_collision and self.movable_wall:
             if self.bob_rect.colliderect(self.movable_wall['rect']):
                  if self.bob_vertical_speed > 0: # Jika Bob jatuh dan bertabrakan dengan obstacle bergerak
                    vertical_collision = True
                    landed_on_obstacle = self.movable_wall['rect'] # Mendarat di movable wall
                    # Tetap lanjutkan cek statis jika ada, tapi dalam desain level ini biasanya mendarat di satu tempat

        # --- Selesaikan Tabrakan Vertikal Bob ---
        if vertical_collision:
            self.bob_y = landed_on_obstacle.top - self.bob_rect.height / 2
            self.bob_vertical_speed = 0
            self.bob_on_ground = True
            self.bob_rect.centery = int(self.bob_y)
        else:
            self.bob_on_ground = False


        # --- Terapkan Pergerakan Horizontal Bob dan Cek Tabrakan X ---
        if self.bob_is_moving:
            self.bob_x += delta_x
            self.bob_rect.centerx = int(self.bob_x)

            horizontal_collision = False
            hit_obstacle_rect = None # Simpan obstacle yang ditabrak horizontal

            # Cek tabrakan horizontal dengan obstacle STATIS
            for obstacle_rect in self.static_obstacles:
                 if self.bob_rect.colliderect(obstacle_rect):
                       horizontal_collision = True
                       hit_obstacle_rect = obstacle_rect
                       break

             # Cek tabrakan horizontal dengan obstacle BERGERAK jika ada
            if not horizontal_collision and self.movable_wall:
                 if self.bob_rect.colliderect(self.movable_wall['rect']):
                       horizontal_collision = True
                       hit_obstacle_rect = self.movable_wall['rect'] # Menabrak movable wall
                       # Jangan break jika ingin tahu mana yang ditabrak duluan, tapi untuk berhenti saja cukup


            # --- Selesaikan Tabrakan Horizontal Bob ---
            if horizontal_collision:
                 self.bob_x -= delta_x # Batalkan pergerakan X
                 self.bob_is_moving = False # Hentikan gerak horizontal
                 self.bob_rect.centerx = int(self.bob_x)
                 print("Bob menabrak dinding samping!")
                 
            if self.bob_rect:
             self.bob_rect.center = (int(self.bob_x), int(self.bob_y))

        # --- Cek Kondisi Selesai Level ---
        # Cek jika exit_zone ada di level ini DAN Bob bertabrakan dengannya
        if self.door and self.bob_rect.colliderect(self.door['rect']):
            # Bob sudah masuk zona keluar!
            self.level_completed = True # Tandai level sebagai selesai
            self.bob_is_moving = False # Opsional: hentikan Bob saat masuk zona keluar
            print(f"Level {self.current_level_num} Selesai!")

        # --- Update Posisi Obstacle Bergerak (Movable Wall) ---
        if self.movable_wall and self.movable_wall['is_moving']:
            current_top = self.movable_wall['rect'].top
            target_top = self.movable_wall['current_target_y']

            # Jika belum sampai target Y
            if current_top < target_top:
                direction = 1 # Bergerak ke bawah
            elif current_top > target_top:
                direction = -1 # Bergerak ke atas
            else:
                # Sudah di target, hentikan pergerakan
                self.movable_wall['is_moving'] = False
                print("Movable wall mencapai target!")
                direction = 0 # Tidak bergerak
            
            if direction != 0:
                # Hitung jumlah pergerakan di frame ini
                move_amount = self.movable_wall_speed

                # Hitung posisi top berikutnya
                next_top = current_top + direction * move_amount

                # Cek apakah pergerakan melewati target
                moved_past_target = False
                if direction == 1 and next_top >= target_top: # Bergerak turun, melewati atau sampai target
                    moved_past_target = True
                elif direction == -1 and next_top <= target_top: # Bergerak naik, melewati atau sampai target
                    moved_past_target = True

                if moved_past_target:
                    # Jika melewati target, set posisi tepat di target dan hentikan
                    self.movable_wall['rect'].top = target_top
                    self.movable_wall['is_moving'] = False
                    print("Movable wall mencapai target!")
                else:
                    # Jika belum sampai target, terapkan pergerakan
                    self.movable_wall['rect'].top = next_top

        # Bob's rect is updated during vertical and horizontal resolution

    def draw(self):
        """Menggambar elemen game (background, rintangan, Bob, tuas)."""
        # Gambar background
        self.screen.fill(self.background_color)

        # Ambil ukuran piksel dari gambar block untuk tiling
        block_width = self.block_image.get_width()
        block_height = self.block_image.get_height()

        # Gambar obstacle STATIS (tiling)
        for obstacle_rect in self.static_obstacles:
            for x in range(obstacle_rect.left, obstacle_rect.right, block_width):
                for y in range(obstacle_rect.top, obstacle_rect.bottom, block_height):
                    self.screen.blit(self.block_image, (int(x), int(y)))

        # Gambar obstacle BERGERAK (tiling) jika ada
        if self.movable_wall:
            movable_rect = self.movable_wall['rect']
            for x in range(movable_rect.left, movable_rect.right, block_width):
                for y in range(movable_rect.top, movable_rect.bottom, block_height):
                    self.screen.blit(self.block_image, (int(x), int(y)))

        # Gambar tuas jika ada (blit gambar sesuai statusnya)
        if self.lever:
            lever_rect = self.lever['rect']
            # Pilih gambar berdasarkan status tuas ('up' atau 'down')
            lever_image_to_draw = self.lever_images[self.lever['state']]
            self.screen.blit(lever_image_to_draw, lever_rect.topleft)

        # Gambar Bob
        if self.bob_rect:
             self.screen.blit(self.bob_image, self.bob_rect.topleft)
             
        # Gambar pintu jika ada
        if self.door:
            door_rect = self.door['rect']
        # Gambar aset gambar pintu di posisi top-left dari Rect pintu
        self.screen.blit(self.door_image, door_rect.topleft)