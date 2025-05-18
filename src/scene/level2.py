# src/scene/level2.py
import pygame
# Import konstanta yang diperlukan (GRAVITY diperlukan untuk blok puzzle)
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT, BLUE_SKY, MOVABLE_WALL_SPEED, GRAVITY
from src.characters.player import Player # Import kelas Player

class Level2:
    def __init__(self, images: dict):
        # Simpan dictionary gambar
        self.images = images

        # Posisi awal pemain di level ini
        self.player_start      = (50, SCREEN_HEIGHT - 100) # Contoh posisi di atas lantai

        # --- Definisi Rintangan Statis ---
        # Rintangan statis adalah objek yang tidak bergerak sendiri, pemain bertabrakan dengannya.
        # Disimpan dalam self.static_obstacles untuk deteksi tabrakan pemain.

        # Lantai dasar (menggunakan gambar block.png)
        floor = pygame.Rect(0, SCREEN_HEIGHT-50, SCREEN_WIDTH, 50)

        # Platform yang menggunakan gambar bridge.png
        # Disimpan dalam list terpisah untuk memudahkan penggambaran dengan gambar bridge.
        self.bridge_platforms_rects = []

        # Platform bridge pertama
        bridge_platform_width = 300
        bridge_platform_x = SCREEN_WIDTH - bridge_platform_width - 400
        bridge_platform_y = SCREEN_HEIGHT - 150
        self.bridge_platforms_rects.append(pygame.Rect(bridge_platform_x, bridge_platform_y, bridge_platform_width, 25))

        # Platform bridge atas
        top_bridge_platform_width = 200
        top_bridge_platform_x = SCREEN_WIDTH - top_bridge_platform_width - 300
        top_bridge_platform_y = SCREEN_HEIGHT - 250
        self.bridge_platforms_rects.append(pygame.Rect(top_bridge_platform_x, top_bridge_platform_y, top_bridge_platform_width, 25))

        # Platform yang diganti menjadi bridge.png (tempat box berada di screenshot)
        second_platform_x = 150
        second_platform_y = SCREEN_HEIGHT - 250
        # Simpan Rect ini untuk nanti digunakan menentukan posisi awal box
        second_bridge_rect_for_box = pygame.Rect(second_platform_x, second_platform_y, 100, 30) # Sesuaikan tinggi jika perlu
        self.bridge_platforms_rects.append(second_bridge_rect_for_box) # Tambahkan ke list platform bridge


        # static_obstacles berisi SEMUA rintangan statis yang akan diperiksa tabrakannya oleh pemain.
        # Ini termasuk lantai dasar dan SEMUA Rect dari list self.bridge_platforms_rects.
        self.static_obstacles = [floor] + self.bridge_platforms_rects


        # --- Definisi Dinding Bergerak ---
        # Dinding bergerak (blok puzzle akan masuk ke sini)
        # Tambahkan velocity_y dan on_ground untuk fisika gravitasi
        class PuzzleBlock(pygame.Rect):
             def __init__(self, x, y, w, h, speed):
                 super().__init__(x, y, w, h)
                 self.velocity_x = 0 # Kecepatan horizontal blok
                 self.velocity_y = 0 # <<< Kecepatan vertikal blok <<<
                 self.speed = speed # Kecepatan dorong blok
                 self.on_ground = False # <<< Status di tanah untuk fisika vertikal <<<

        # Blok puzzle (menggunakan gambar box.png)
        puzzle_block_size = 50
        # Posisikan blok puzzle di atas second_bridge_rect_for_box
        puzzle_block_x = second_bridge_rect_for_box.x + (second_bridge_rect_for_box.width // 2) - (puzzle_block_size // 2) # Sesuaikan dengan lebar second_bridge_rect_for_box
        # >>> Sesuaikan posisi Y agar ada sedikit jarak visual dari platform di bawahnya <<<
        # Kurangi beberapa piksel tambahan dari tepi atas platform
        puzzle_block_y = second_bridge_rect_for_box.y - puzzle_block_size - 2 # Contoh: kurangi 2 piksel lagi
        puzzle_block_rect = PuzzleBlock(puzzle_block_x, puzzle_block_y, puzzle_block_size, puzzle_block_size, MOVABLE_WALL_SPEED) # Gunakan PuzzleBlock
        self.movable_walls    = [puzzle_block_rect] # Masukkan blok puzzle ke dinding bergerak

        # --- Mekanisme Puzzle ---
        # Elemen-elemen yang terkait dengan puzzle (tombol, pintu tertutup)

        # Tombol tekan (Pressure Plate)
        button_width = 60
        button_height = 10
        button_x = SCREEN_WIDTH - 300 # Posisi X tombol tekan (jauh dari pintu keluar)
        button_y = SCREEN_HEIGHT - 60 # Posisi Y tombol tekan (di atas lantai)
        self.pressure_plate_rect = pygame.Rect(button_x, button_y, button_width, button_height)

        # Pintu tertutup (yang menghalangi goal awalnya)
        closed_door_width = 50
        closed_door_height = 80
        closed_door_x = SCREEN_WIDTH - 80 # Posisi X pintu tertutup (lokasi goal)
        closed_door_y = SCREEN_HEIGHT - 130 # Posisi Y pintu tertutup (di atas lantai)
        self.closed_door_rect = pygame.Rect(closed_door_x, closed_door_y, closed_door_width, closed_door_height)

        # Awalnya pintu tertutup, jadi tambahkan ke rintangan statis UNTUK TABRAKAN
        self.static_obstacles.append(self.closed_door_rect)

        # Status pintu (terbuka atau tertutup)
        self.door_open = False

        # Pintu keluar level (lokasi goal)
        self.door_rect        = pygame.Rect(closed_door_x, closed_door_y, closed_door_width, closed_door_height)


        # Warna latar belakang level
        self.background_color = BLUE_SKY

    # Metode handle_event tetap kosong
    def handle_event(self, event: pygame.event.Event, player):
        pass

    # Metode update - memperbarui status level, menangani logika puzzle dan fisika blok puzzle
    def update(self, player: Player | None):
        # --- Logika Puzzle Tombol Tekan & Pintu ---
        is_button_pressed = False
        # Cek pemain menekan tombol
        if player is not None and player.rect.colliderect(self.pressure_plate_rect):
            if player.rect.bottom >= self.pressure_plate_rect.top and player.rect.bottom <= self.pressure_plate_rect.bottom + 5:
                 is_button_pressed = True

        # Periksa blok movable menekan tombol
        if not is_button_pressed:
            for wall in self.movable_walls:
                 if wall.colliderect(self.pressure_plate_rect) and wall.bottom >= self.pressure_plate_rect.top and wall.bottom <= self.pressure_plate_rect.bottom + 5:
                    is_button_pressed = True
                    break

        # Atur status pintu
        self.door_open = is_button_pressed

        # Kelola pintu tertutup
        if self.door_open:
            if self.closed_door_rect in self.static_obstacles:
                self.static_obstacles.remove(self.closed_door_rect)
        else:
            if self.closed_door_rect not in self.static_obstacles:
                 self.static_obstacles.append(self.closed_door_rect)


        # --- Logika Fisika dan Pergerakan Blok Puzzle ---
        obstacles_for_block = self.static_obstacles + [w for w in self.movable_walls if w is not self.movable_walls[0]] # Rintangan untuk blok (static + blok lain jika ada)

        for block in self.movable_walls: # movable_walls berisi objek PuzzleBlock
            # Terapkan gravitasi ke blok puzzle
            block.velocity_y += GRAVITY
            # Batasi kecepatan jatuh
            if block.velocity_y > 15: # Sama seperti batas kecepatan jatuh pemain
                 block.velocity_y = 15

            # Perbarui posisi Y berdasarkan kecepatan vertikal
            block.y += int(block.velocity_y)

            # Deteksi tabrakan vertikal blok puzzle dengan rintangan statis dan movable lainnya
            block.on_ground = False # Reset status di tanah
            for other_block in obstacles_for_block:
                 if block.colliderect(other_block):
                      if block.velocity_y > 0: # Blok jatuh dan bertabrakan dari atas
                           block.bottom = other_block.top
                           block.velocity_y = 0
                           block.on_ground = True # Blok berada di atas objek lain
                      elif block.velocity_y < 0: # Blok bergerak ke atas dan bertabrakan dari bawah (jarang terjadi untuk blok)
                           block.top = other_block.bottom
                           block.velocity_y = 0

            # --- Logika Dorongan Horizontal Blok Puzzle ---
            # Blok hanya bisa didorong jika pemain ada (player is not None)
            if player is not None:
                 # Periksa tumpang tindih vertikal yang cukup untuk dianggap tabrakan horizontal dengan pemain
                 vertical_overlap = min(player.rect.bottom, block.bottom) - max(player.rect.top, block.top)
                 if vertical_overlap > 5: # Jika ada overlap vertikal yang cukup
                      # Buat rect sementara untuk posisi blok jika didorong pemain
                      next_block_rect_x = block.x + int(player.velocity.x)
                      next_block_rect = block.copy()
                      next_block_rect.x = next_block_rect_x

                      # Cek apakah blok di posisi berikutnya akan bertabrakan dengan rintangan lain
                      can_move_horizontally = True
                      for other_block in obstacles_for_block:
                           if next_block_rect.colliderect(other_block):
                                # Tabrakan di posisi dorongan, blok tidak bisa bergerak ke arah itu
                                can_move_horizontally = False
                                # Adjust block position if it was pushed into something
                                if player.velocity.x > 0:
                                    block.right = other_block.left
                                elif player.velocity.x < 0:
                                    other_block_rect_copy = pygame.Rect(other_block) # Gunakan copy agar tidak memodifikasi other_block
                                    block.left = other_block_rect_copy.right
                                break # Hentikan cek karena sudah menabrak

                      # Jika tidak ada tabrakan di posisi dorongan, terapkan pergerakan horizontal
                      if can_move_horizontally:
                           block.x = next_block_rect_x


            # Batasi blok puzzle agar tidak keluar layar (cek setelah pergerakan dan tabrakan)
            if block.left < 0: block.left = 0
            if block.right > SCREEN_WIDTH: block.right = SCREEN_WIDTH


    # Metode draw tetap sama
    def draw(self, screen: pygame.Surface, block_image: pygame.Surface):
        # Menggambar rintangan statis yang menggunakan gambar block (hanya lantai dasar dan pintu tertutup)
        for rect in self.static_obstacles:
             is_bridge_rect = rect in self.bridge_platforms_rects
             is_closed_door_rect = rect is self.closed_door_rect

             if not is_bridge_rect and not is_closed_door_rect:
                w,h = block_image.get_size()
                for x in range(rect.left, rect.right, w):
                    for y in range(rect.top, rect.bottom, h):
                        screen.blit(block_image, (x,y))

        # Menggambar semua platform yang menggunakan gambar bridge.png
        bridge_image = self.images['bridge']
        w_bridge, h_bridge = bridge_image.get_size()
        platforms_to_draw_bridge = self.bridge_platforms_rects

        for rect in platforms_to_draw_bridge:
            for x in range(rect.left, rect.right, w_bridge):
                 for y in range(rect.top, rect.bottom, h_bridge):
                     screen.blit(bridge_image, (x,y))

        # Menggambar dinding bergerak (blok puzzle)
        box_image = self.images['box']
        for rect in self.movable_walls:
             screen.blit(box_image, rect.topleft)


        # Gambar tombol tekan
        button_color = (0, 200, 0) if self.door_open else (0, 0, 0)
        pygame.draw.rect(screen, button_color, self.pressure_plate_rect)

        # Gambar pintu tertutup HANYA jika itu ADA di static_obstacles
        if self.closed_door_rect in self.static_obstacles:
             screen.blit(block_image, self.closed_door_rect.topleft)

    # Metode draw_overlays tetap sama
    def draw_overlays(self, screen: pygame.Surface, images: dict):
         screen.blit(images['door'], self.door_rect.topleft)
         pass
