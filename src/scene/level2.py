# src/scene/level2.py
import pygame
# Hapus import GRAVITY karena tidak ada lagi kotak dengan fisika
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_SKY, MOVABLE_WALL_SPEED # Import konstanta dasar lainnya
# Hapus import Player karena Level tidak perlu mengelola Player secara langsung di sini
# from src.characters.player import Player
from src.utils.resource_manager import ResourceManager # Import ResourceManager
import math # Import modul math

# Hapus Kelas PushableBox karena kotak akan dihapus
# class PushableBox(pygame.Rect):
#    # ... (definisi kelas PushableBox dihapus)

# --- Kelas untuk Tuas (Lever) ---
# Gunakan definisi Lever dari Level 1/3 atau definisi sederhana di sini
class Lever(pygame.Rect):
    def __init__(self, x, y, width, height, up_img, down_img):
        super().__init__(x, y, width, height)
        self.up_img = up_img
        self.down_img = down_img
        self.is_up = True # Status awal tuas
        self.is_interactable = False # Status apakah pemain cukup dekat

    def draw(self, screen):
        if self.is_up:
            screen.blit(self.up_img, self.topleft)
        else:
            screen.blit(self.down_img, self.topleft)

    def toggle(self):
        self.is_up = not self.is_up
# ---------------------------------------------


class Level2:
    # Ubah signature __init__ agar menerima player dan resources
    def __init__(self, player, resources):
        # --- PASTIKAN BARIS INI DI AWAL __init__ ---
        self.player = player # Simpan objek player
        self.resources = resources # Simpan objek resource manager
        # --------------------------------------------

        # Posisi awal pemain di level ini (Anda bisa menentukan di sini atau di game.py)
        self.player_start_pos = (50, SCREEN_HEIGHT - 100) # Contoh posisi di atas lantai


        # --- Definisi Rintangan Statis ---
        self.obstacles = [] # List utama obstacles

        # Lantai dasar (menggunakan gambar grass.png)
        self.ground_rect = pygame.Rect(0, SCREEN_HEIGHT-50, SCREEN_WIDTH, 50)
        self.obstacles.append(self.ground_rect) # Tambahkan ke obstacles

        # Platform yang menggunakan gambar bridge.png
        self.bridge_platforms_rects = []

        # Platform bridge pertama
        bridge_platform_width = 300
        bridge_platform_x = SCREEN_WIDTH - bridge_platform_width - 400
        bridge_platform_y = SCREEN_HEIGHT - 150
        rect1 = pygame.Rect(bridge_platform_x, bridge_platform_y, bridge_platform_width, 25)
        self.bridge_platforms_rects.append(rect1)
        self.obstacles.append(rect1) # Tambahkan ke obstacles

        # Platform bridge atas
        top_bridge_platform_width = 200
        top_bridge_platform_x = SCREEN_WIDTH - top_bridge_platform_width - 300
        top_bridge_platform_y = SCREEN_HEIGHT - 250
        rect2 = pygame.Rect(top_bridge_platform_x, top_bridge_platform_y, top_bridge_platform_width, 25)
        self.bridge_platforms_rects.append(rect2)
        self.obstacles.append(rect2) # Tambahkan ke obstacles

        # Platform yang diganti menjadi bridge.png (dulu tempat box)
        second_platform_x = 100
        second_platform_y = SCREEN_HEIGHT - 300
        self.second_bridge_rect = pygame.Rect(second_platform_x, second_platform_y, 100, 20) # Sesuaikan tinggi jika perlu
        self.bridge_platforms_rects.append(self.second_bridge_rect) # Tambahkan ke list platform bridge
        self.obstacles.append(self.second_bridge_rect) # Tambahkan ke obstacles


        # --- Aset Gambar ---
        # Muat semua aset menggunakan ResourceManager
        self.block_img = self.resources.load_image("fence")
        self.grass_img = self.resources.load_image("grass")
        self.bridge_img = self.resources.load_image("bridge")
        # Hapus pemuatan box_img
        # self.box_img = self.resources.load_image("box")
        # Hapus pemuatan gambar tombol
        # self.button_img_unpressed_orig = self.resources.load_image("buttonBlue")
        # self.button_img_pressed_orig = self.resources.load_image("buttonBlue_pressed")
        # Muat gambar tuas
        self.lever_up_img = self.resources.load_image("lever_up")
        self.lever_down_img = self.resources.load_image("lever_down")
        self.door_img = self.resources.load_image("signExit") # Gambar pintu exit (menggunakan signExit.png)

        # Ukuran asli gambar untuk tiling/scaling
        self.orig_block_w = self.block_img.get_width()
        self.orig_grass_w = self.grass_img.get_width()
        self.orig_bridge_w = self.bridge_img.get_width()

        # Cache untuk gambar yang diskalakan berdasarkan tinggi
        self._block_cache = {}
        self._grass_cache = {}
        self._bridge_cache = {}


        # --- Tuas (Lever) ---
        # Posisikan tuas di lokasi tombol sebelumnya
        lever_width = self.lever_up_img.get_width()
        lever_height = self.lever_up_img.get_height()
        lever_x = SCREEN_WIDTH - 685 # Posisi X (sama dengan tombol sebelumnya)
        lever_y = SCREEN_HEIGHT - 300 - lever_height # Di atas lantai
        self.lever = Lever(lever_x, lever_y, lever_width, lever_height, self.lever_up_img, self.lever_down_img)
        self._can_interact_lever = True # Untuk cooldown interaksi
        self._lever_cooldown_timer = 0


        # --- Pintu Tertutup (Obstacle sementara) ---
        # Gunakan gambar block.png atau gambar lain jika ada asset pintu tertutup
        closed_door_width = 50
        closed_door_height = 80
        closed_door_x = SCREEN_WIDTH - 80 # Posisi X pintu tertutup
        closed_door_y = SCREEN_HEIGHT - 50 - closed_door_height # Di atas lantai
        self.closed_door_rect = pygame.Rect(closed_door_x, closed_door_y, closed_door_width, closed_door_height)

        # Status pintu (terbuka atau tertutup) - Dikontrol oleh tuas
        # Awalnya pintu tertutup, jadi door_open = False
        self.door_open = False


        # --- Goal (Exit) ---
        # Gunakan gambar door.png (yang sekarang signExit.png)
        exit_width = self.door_img.get_width() # Gunakan ukuran gambar exit (signExit.png)
        exit_height = self.door_img.get_height()
        # Posisikan di lokasi pintu tertutup, tetapi ini adalah lokasi Goal
        exit_x = closed_door_x # Sama dengan posisi X pintu tertutup
        exit_y = closed_door_y - (exit_height - closed_door_height) # Sesuaikan Y agar bagian bawah signExit sejajar dengan bagian bawah pintu tertutup (sesuaikan offset)
        self.exit_rect = pygame.Rect(exit_x, exit_y, exit_width, exit_height)
        # Tidak perlu ditambahkan ke obstacles jika hanya lokasi finish


        # --- Hapus Kotak yang Bisa Didorong ---
        # self.pushable_boxes = [] # Hapus list ini


        # --- Status Level ---
        self.completed = False # Flag untuk menandai level selesai


        # --- Post-init Setup (Tambahkan rintangan yang status awalnya ditentukan) ---
        # Tambahkan pintu tertutup ke obstacles jika awalnya tertutup
        if not self.door_open:
             self.obstacles.append(self.closed_door_rect)
        # Hapus penambahan kotak ke obstacles
        # for box in self.pushable_boxes:
        #      self.obstacles.append(box)


    # Metode handle_event - hanya untuk input yang tidak ditangani Player
    def handle_event(self, event: pygame.event.Event):
        pass

    # Metode update - memperbarui status level dan objek-objeknya
    # Ubah signature agar menerima dt dan player_rect
    def update(self, dt, player_rect): # <-- UBAH SIGNATURE
        # --- Hapus Update Kotak yang Bisa Didorong ---
        # Logika update kotak dihapus


        # --- Logika Tuas (Lever) & Pintu ---
        # Deteksi interaksi pemain dengan tuas
        interaction_area = self.lever.inflate(10, 10) # Area interaksi lebih besar dari tuas
        if player_rect.colliderect(interaction_area):
            # Pemain dekat, periksa input E dan cooldown
            self.lever.is_interactable = True # Tandai tuas bisa diinteraksi
            keys = pygame.key.get_pressed()
            if keys[pygame.K_e] and self._can_interact_lever:
                 self.lever.toggle() # Toggle status tuas

                 # Atur status pintu berdasarkan status tuas
                 # Jika tuas ke bawah (is_up = False), buka pintu (door_open = True)
                 self.door_open = not self.lever.is_up

                 # Aktifkan cooldown
                 self._can_interact_lever = False
                 self._lever_cooldown_timer = 0.5 # Cooldown 0.5 detik

        else:
             self.lever.is_interactable = False # Tidak bisa diinteraksi jika pemain menjauh


        # Kelola cooldown tuas
        if not self._can_interact_lever:
             self._lever_cooldown_timer -= dt
             if self._lever_cooldown_timer <= 0:
                  self._can_interact_lever = True


        # Kelola pintu tertutup (tambahkan/hapus dari obstacles)
        if self.door_open:
            if self.closed_door_rect in self.obstacles: # Cek di self.obstacles
                self.obstacles.remove(self.closed_door_rect)
        else:
            if self.closed_door_rect not in self.obstacles: # Cek di self.obstacles
                 self.obstacles.append(self.closed_door_rect)


        # --- Cek Selesai Level ---
        # Cek apakah pemain mencapai Goal (lokasi Exit)
        # Gunakan player_rect yang dilewatkan
        if player_rect.colliderect(self.exit_rect): # exit_rect merepresentasikan lokasi Goal
            # Pastikan pintu terbuka sebelum bisa menyelesaikan level
            if self.door_open:
                 self.completed = True # Set flag completed


    # Metode draw - menggambar semua elemen level
    # Ubah signature agar menerima screen
    def draw(self, screen: pygame.Surface): # <-- UBAH SIGNATURE
        # --- Gambar Rintangan ---
        for rect in self.obstacles:
            h = rect.height

            # Tentukan gambar, lebar asli, dan cache yang akan digunakan
            # Lewati menggambar jika itu bridge atau closed door karena akan digambar terpisah
            if rect is self.ground_rect:
                # Jika ini adalah lantai dasar, gunakan gambar grass
                img_to_use = self.grass_img
                orig_w = self.orig_grass_w
                cache_to_use = self._grass_cache
            elif rect in self.bridge_platforms_rects:
                 # JANGAN gambar platform bridge di sini, akan digambar terpisah
                 continue
            elif rect is self.closed_door_rect:
                 # JANGAN gambar pintu tertutup di sini, akan digambar terpisah
                 continue
            else:
                # Untuk rintangan statis lainnya (jika ada), gunakan gambar block
                img_to_use = self.block_img
                orig_w = self.orig_block_w
                cache_to_use = self._block_cache


            # Ambil atau buat scaled tile untuk ketinggian h menggunakan cache yang benar
            if h not in cache_to_use:
                # scale hanya di sumbu Y, sumbu X biarkan orig_w
                scaled = pygame.transform.scale(img_to_use, (orig_w, h))
                cache_to_use[h] = scaled

            tile_surf = cache_to_use[h]

            # hitung berapa tile horizontal yang diperlukan
            count = math.ceil(rect.width / orig_w)

            # Gambar tiling horizontal
            for i in range(count):
                x = rect.x + i * orig_w
                # Gambar tile, hanya menutupi tinggi rect
                screen.blit(tile_surf, (x, rect.y))

        # --- Gambar Lantai Dasar Menggunakan grass.png ---
        # Lantai dasar sudah digambar di loop obstacles jika tidak dilewati

        # --- Gambar Platform Bridge Menggunakan bridge.png ---
        w_bridge, h_bridge = self.bridge_img.get_size()
        for rect in self.bridge_platforms_rects:
             # Gambarkan platform bridge yang ada di list
             for x in range(rect.left, rect.right, w_bridge):
                  # Gambarkan tile, sesuaikan jika perlu memotong tile terakhir
                  draw_width = min(w_bridge, rect.right - x)
                  draw_height = h_bridge # Gunakan tinggi asli gambar bridge
                  if draw_width > 0: # Hanya gambar jika ada lebar positif
                      # Gambar tiling horizontal
                      screen.blit(self.bridge_img, (x, rect.top), (0, 0, draw_width, draw_height))

        # --- Gambar Tuas ---
        self.lever.draw(screen)
        # Opsional: Gambar indikator interaksi
        if self.lever.is_interactable:
             font = pygame.font.SysFont(None, 24)
             text_surf = font.render("Press E", True, (255, 255, 255))
             text_rect = text_surf.get_rect(center=(self.lever.centerx, self.lever.top - 20))
             screen.blit(text_surf, text_rect)
        # -------------------

        # --- Gambar Pintu Tertutup (Jika Ada di Obstacles) ---
        # Gambarkan pintu tertutup HANYA jika itu ADA di self.obstacles (status tertutup)
        if self.closed_door_rect in self.obstacles:
             # Gunakan gambar block.png untuk pintu tertutup, atau asset lain jika ada
             h = self.closed_door_rect.height
             img_to_use = self.block_img # Menggunakan block.png sebagai contoh pintu tertutup
             orig_w = self.orig_block_w
             cache_to_use = self._block_cache

             if h not in cache_to_use:
                 scaled = pygame.transform.scale(img_to_use, (orig_w, h))
                 cache_to_use[h] = scaled
             tile_surf = cache_to_use[h]

             count = math.ceil(self.closed_door_rect.width / orig_w)
             for i in range(count):
                 x = self.closed_door_rect.x + i * orig_w
                 screen.blit(tile_surf, (x, self.closed_door_rect.y))
        # --------------------------------------------------


        # --- Gambar Goal (Exit) ---
        # Gambarkan gambar door.png (yang sekarang signExit.png) di lokasi exit_rect
        screen.blit(self.door_img, self.exit_rect.topleft)
        # -------------------------