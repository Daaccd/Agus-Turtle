import pygame
from src.constants import COLOR_BROWN, SCREEN_WIDTH, SCREEN_HEIGHT # Import konstanta dasar
from src.utils.resource_manager import ResourceManager
import math # Import modul math

class Level1:
    def __init__(self, player, resources):
        # --- PASTIKAN BARIS INI DI AWAL __init__ ---
        self.player = player
        self.resources = resources
        # --------------------------------------------

        # --- Rintangan Statis (Obstacles) ---
        self.obstacles = []

        # Lantai dasar - Simpan referensi ke Rect ini agar mudah diidentifikasi saat menggambar
        self.ground_rect = pygame.Rect(0, 550, SCREEN_WIDTH, 50)
        self.obstacles.append(self.ground_rect)

        # Platform yang akan digerakkan oleh tuas (Platform Utama yang Bergerak)
        movable_platform_width = 200
        movable_platform_height = 20
        self.movable_platform_start_pos = pygame.Vector2(300, 530) # Posisi awal (di atas lantai)
        self.movable_platform_target_y = 340 # Posisi target saat lever aktif (DISESUAIKAN)
        self.movable_platform_speed = 100 # Kecepatan gerakan platform

        self.movable_platform_rect = pygame.Rect(
             self.movable_platform_start_pos.x,
             self.movable_platform_start_pos.y,
             movable_platform_width,
             movable_platform_height
        )
        self.obstacles.append(self.movable_platform_rect) # Tambahkan ke obstacles

        # Platform statis (platform di (525, 350) dari code teman Anda)
        static_platform_width = 280
        static_platform_height = 200
        static_platform_x = 525
        static_platform_y = 350
        self.static_platform_rect = pygame.Rect(static_platform_x, static_platform_y, static_platform_width, static_platform_height) # Simpan referensi
        self.obstacles.append(self.static_platform_rect) # Tambahkan ke obstacles


        # --- Aset Gambar ---
        # Sekarang self.resources sudah diinisialisasi, jadi bisa digunakan di sini
        self.block_img = self.resources.load_image("block") # Gambar untuk platform statis lain
        self.grass_img = self.resources.load_image("grass") # Gambar untuk lantai bawah
        self.bridge_img = self.resources.load_image("bridge") # Gambar untuk platform bergerak
        #self.exit_img = self.resources.load_image("signExit") # Hapus baris ini
        self.exit_img = self.resources.load_image("flag") # <-- Menggunakan aset "flag"
        self.lever_up_img = self.resources.load_image("lever_up") # Gambar tuas ke atas
        self.lever_down_img = self.resources.load_image("lever_down") # Gambar tuas ke bawah

        self.orig_block_w = self.block_img.get_width() # Lebar asli gambar block untuk tiling
        self.orig_grass_w = self.grass_img.get_width() # Lebar asli gambar grass untuk tiling
        self.orig_bridge_w = self.bridge_img.get_width() # Lebar asli gambar bridge untuk tiling


        self._block_cache = {} # Cache untuk scaled block images
        self._grass_cache = {} # Cache untuk scaled grass images
        self._bridge_cache = {} # Cache untuk scaled bridge images # Tambahkan cache untuk bridge


        # --- Goal (Tanda Exit) ---
        exit_width = self.exit_img.get_width()
        exit_height = self.exit_img.get_height()
        # Posisikan tanda exit (menggunakan posisi pintu teman Anda)
        exit_x = 800 - exit_width # Di tepi kanan level
        exit_y = 350 - exit_height # Di atas platform statis (sesuaikan y jika perlu)
        self.exit_rect = pygame.Rect(exit_x, exit_y, exit_width, exit_height)


        # --- Tuas (Lever) ---
        # Posisi tuas (menggunakan posisi tuas teman Anda)
        lever_width = self.lever_up_img.get_width()
        lever_height = self.lever_up_img.get_height() # Gunakan tinggi gambar
        lever_x = 100
        lever_y = 480 # Di atas lantai
        self.lever_rect = pygame.Rect(lever_x, lever_y, lever_width, lever_height)
        self.is_lever_up = True # Status tuas (sesuai inisialisasi teman Anda)
        self._can_interact_lever = True # Untuk cooldown interaksi
        self._lever_cooldown_timer = 0


        # --- Status Level ---
        self.completed = False # Flag untuk menandai level selesai


        # Simpan posisi Y saat ini dari platform yang dapat digerakkan
        self._current_platform_y = self.movable_platform_start_pos.y


    # Metode handle_event - hanya untuk input yang tidak ditangani Player
    def handle_event(self, event: pygame.event.Event):
        pass


    # Metode update - memperbarui status level dan objek-objeknya
    def update(self, dt, player_rect): # Menerima player_rect
        # --- Logika Tuas (Lever) ---
        # Deteksi interaksi pemain dengan tuas
        interaction_area = self.lever_rect.inflate(10, 10) # Area interaksi lebih besar dari tuas
        if player_rect.colliderect(interaction_area):
            # Pemain dekat, periksa input E dan cooldown
            keys = pygame.key.get_pressed()
            if keys[pygame.K_e] and self._can_interact_lever:
                 self.is_lever_up = not self.is_lever_up # Toggle status tuas

                 # Aktifkan cooldown
                 self._can_interact_lever = False
                 self._lever_cooldown_timer = 0.5 # Cooldown 0.5 detik


        # Kelola cooldown tuas
        if not self._can_interact_lever:
             self._lever_cooldown_timer -= dt
             if self._lever_cooldown_timer <= 0:
                  self._can_interact_lever = True


        # --- Logika Pergerakan Platform Utama (Dikontrol Tuas) ---
        # Target Y platform tergantung pada status tuas
        # is_up = True (awal) -> platform di start_pos (bawah)
        # is_up = False -> platform di target_y (atas)
        target_y = self.movable_platform_start_pos.y if self.is_lever_up else self.movable_platform_target_y
        distance_to_target = target_y - self._current_platform_y
        move_amount = self.movable_platform_speed * dt

        old_movable_platform_y = self.movable_platform_rect.y

        # Gerakkan platform menuju target_y
        if distance_to_target > 0: # Platform perlu naik
             self._current_platform_y += min(move_amount, distance_to_target)
        elif distance_to_target < 0: # Platform perlu turun
             self._current_platform_y += max(-move_amount, distance_to_target)

        # Perbarui posisi Rect platform
        self.movable_platform_rect.y = int(self._current_platform_y)

        # Hitung pergerakan Y platform di frame ini untuk menggerakkan pemain di atasnya
        actual_platform_move_y = self.movable_platform_rect.y - old_movable_platform_y

        # Tangani pemain di atas platform bergerak (pemain bergerak bersama platform)
        if player_rect.colliderect(self.movable_platform_rect):
             # Asumsikan pemain di atas platform jika bottom pemain <= top platform
             if player_rect.bottom <= self.movable_platform_rect.top + abs(actual_platform_move_y) + 5: # Tambah toleransi
                  # Gerakkan pemain sejauh platform bergerak secara vertikal
                  player_rect.y += actual_platform_move_y
                  # Status on_ground pemain perlu diatur di logika update pemain saat menabrak platform


        # --- Cek Selesai Level ---
        # Cek apakah pemain mencapai tanda Exit
        if player_rect.colliderect(self.exit_rect):
            self.completed = True # Set flag completed


    # Metode draw - menggambar semua elemen level
    def draw(self, screen: pygame.Surface):
        # --- Gambar Rintangan ---
        for rect in self.obstacles:
            h = rect.height

            # Tentukan gambar, lebar asli, dan cache yang akan digunakan
            if rect is self.ground_rect:
                # Jika ini adalah lantai dasar, gunakan gambar grass
                img_to_use = self.grass_img
                orig_w = self.orig_grass_w
                cache_to_use = self._grass_cache
            elif rect is self.movable_platform_rect:
                 # JANGAN gambar platform bergerak di sini, akan digambar terpisah
                 continue
            else:
                # Untuk platform statis lainnya, gunakan gambar block
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

        # --- Gambar Platform Bergerak Menggunakan bridge.png ---
        rect = self.movable_platform_rect
        h = rect.height
        img_to_use = self.bridge_img
        orig_w = self.orig_bridge_w
        cache_to_use = self._bridge_cache

        if h not in cache_to_use:
            scaled = pygame.transform.scale(img_to_use, (orig_w, h))
            cache_to_use[h] = scaled

        tile_surf = cache_to_use[h]
        count = math.ceil(rect.width / orig_w)

        for i in range(count):
            x = rect.x + i * orig_w
            screen.blit(tile_surf, (x, rect.y))
        # ------------------------------------------------------


        # --- Gambar Tanda Exit ---
        screen.blit(self.exit_img, self.exit_rect.topleft)

        # --- Gambar Tuas ---
        # Gambar tuas sesuai statusnya
        if self.is_lever_up:
            screen.blit(self.lever_up_img, self.lever_rect.topleft)
        else:
            screen.blit(self.lever_down_img, self.lever_rect.topleft)

        # Opsional: Gambar indikator interaksi tuas
        # Cek apakah pemain dekat dengan tuas (tanpa harus memuat kunci/gembok di Lvl1)
        # Gunakan self.player.rect yang disimpan di Level1 karena draw tidak menerima player_rect
        interaction_area = self.lever_rect.inflate(10, 10)
        if self.player.rect.colliderect(interaction_area):
             font = pygame.font.SysFont(None, 24)
             text_surf = font.render("Press E", True, (255, 255, 255))
             text_rect = text_surf.get_rect(center=(self.lever_rect.centerx, self.lever_rect.top - 20))
             screen.blit(text_surf, text_rect)