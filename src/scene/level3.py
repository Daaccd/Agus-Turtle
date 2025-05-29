import pygame
from src.constants import COLOR_BROWN, SCREEN_WIDTH, SCREEN_HEIGHT
from src.utils.resource_manager import ResourceManager
import math

# --- Kelas untuk Tuas (Lever) ---
# Dipertahankan
class Lever(pygame.Rect):
    def __init__(self, x, y, width, height, up_img, down_img):
        super().__init__(x, y, width, height)
        self.up_img = up_img
        self.down_img = down_img
        self.is_up = True # Status awal tuas (misal: ke atas)
        self.is_interactable = False # Status apakah pemain cukup dekat untuk berinteraksi

    def draw(self, screen):
        # Gambar tuas sesuai statusnya
        if self.is_up:
            screen.blit(self.up_img, self.topleft)
        else:
            screen.blit(self.down_img, self.topleft)

    def toggle(self):
        # Mengubah status tuas
        self.is_up = not self.is_up

# ---------------------------------------------


class Level3:
    def __init__(self, player, resources, sfx_lever=None, sfx_key_pickup=None, sfx_lock_open=None):
        self.player = player
        self.resources = resources
        self.sfx_lever = sfx_lever
        self.sfx_key_pickup = sfx_key_pickup
        self.sfx_lock_open = sfx_lock_open

        # --- Rintangan Statis (Obstacles) ---
        self.obstacles = [
            pygame.Rect(0, 550, 800, 50),   # lantai
        ]

        # --- Aset Gambar ---
        self.block_img = self.resources.load_image("block")
        self.exit_img = self.resources.load_image("signExit")
        self.bridge_img = self.resources.load_image("bridge")
        lever_up_orig = self.resources.load_image("lever_up")
        lever_down_orig = self.resources.load_image("lever_down")
        key_red_orig = self.resources.load_image("keyRed")
        lock_red_orig = self.resources.load_image("lock_red")


        # Tentukan ukuran untuk tuas (sesuaikan jika perlu)
        lever_width = lever_up_orig.get_width()
        lever_height = lever_down_orig.get_height() # Gunakan gambar down untuk tinggi agar konsisten
        self.lever_up_img = pygame.transform.scale(lever_up_orig, (lever_width, lever_height))
        self.lever_down_img = pygame.transform.scale(lever_down_orig, (lever_width, lever_height))

        # Tentukan ukuran untuk kunci dan gembok (sesuaikan jika perlu)
        key_size = 30 # Ukuran kunci
        lock_size = 50 # Ukuran gembok
        # Skala kunci proporsional
        self.key_red_img = pygame.transform.scale(key_red_orig, (key_size, int(key_size * key_red_orig.get_height() / key_red_orig.get_width())))
        # Skala gembok persegi
        self.lock_red_img = pygame.transform.scale(lock_red_orig, (lock_size, lock_size))


        self.orig_w = self.block_img.get_width()
        self._cache = {}


        # --- Goal (Tanda Exit) ---
        exit_width = self.exit_img.get_width()
        exit_height = self.exit_img.get_height()
        exit_x = SCREEN_WIDTH - exit_width - 20
        exit_y = SCREEN_HEIGHT - 500 - exit_height
        self.exit_rect = pygame.Rect(exit_x, exit_y, exit_width, exit_height)


        # --- Platform Bridge ---
        self.bridge_platforms_rects = []

        # Platform yang akan digerakkan oleh tuas (Platform Utama yang Bergerak)
        self.movable_platform_start_pos = pygame.Vector2(500, 525) # Posisi awal (misal: di bawah)
        self.movable_platform_end_pos = pygame.Vector2(500, 100) # Posisi target saat tuas diaktifkan (misal: di atas dekat exit)
        self.movable_platform_speed = 100 # Kecepatan gerakan platform

        movable_bridge_width = 100
        movable_bridge_height = self.bridge_img.get_height()
        self.movable_platform_rect = pygame.Rect(
            self.movable_platform_start_pos.x,
            self.movable_platform_start_pos.y,
            movable_bridge_width,
            movable_bridge_height
        )

        self.bridge_platforms_rects.append(self.movable_platform_rect)
        self.obstacles.append(self.movable_platform_rect) # Tambahkan ke obstacles agar pemain bertabrakan

        # Platform bridge kedua (platform statis dekat exit)
        bridge_platform_width = 200
        bridge_platform_height = self.bridge_img.get_height()
        bridge_platform_x = 600
        bridge_platform_y = 100
        bridge_rect_top = pygame.Rect(bridge_platform_x, bridge_platform_y, bridge_platform_width, bridge_platform_height)
        self.bridge_platforms_rects.append(bridge_rect_top)
        self.obstacles.append(bridge_rect_top) # Tambahkan ke obstacles
        
        bridge_platform_width = 100
        bridge_platform_height = self.bridge_img.get_height()
        bridge_platform_x = 100
        bridge_platform_y = 450
        bridge_rect_top = pygame.Rect(bridge_platform_x, bridge_platform_y, bridge_platform_width, bridge_platform_height)
        self.bridge_platforms_rects.append(bridge_rect_top)
        self.obstacles.append(bridge_rect_top)
        
        bridge_platform_width = 100
        bridge_platform_height = self.bridge_img.get_height()
        bridge_platform_x = 200
        bridge_platform_y = 350
        bridge_rect_top = pygame.Rect(bridge_platform_x, bridge_platform_y, bridge_platform_width, bridge_platform_height)
        self.bridge_platforms_rects.append(bridge_rect_top)
        self.obstacles.append(bridge_rect_top)
        
        bridge_platform_width = 100
        bridge_platform_height = self.bridge_img.get_height()
        bridge_platform_x = 100
        bridge_platform_y = 250
        bridge_rect_top = pygame.Rect(bridge_platform_x, bridge_platform_y, bridge_platform_width, bridge_platform_height)
        self.bridge_platforms_rects.append(bridge_rect_top)
        self.obstacles.append(bridge_rect_top)


        # --- Tuas (Lever) ---
        # Posisi tuas dipertahankan seperti sebelumnya (x=400)
        lever_x = 400
        lever_y = SCREEN_HEIGHT - 50 - lever_height
        self.lever = Lever(lever_x, lever_y, lever_width, lever_height, self.lever_up_img, self.lever_down_img)
        self._can_interact_lever = True
        self._lever_cooldown_timer = 0

        # --- Gembok (Lock) ---
        # Posisikan gembok agar menutupi bagian bawah tuas (sesuaikan agar pas secara visual)
        lock_width, lock_height = self.lock_red_img.get_size() # Gunakan ukuran gambar gembok yang diskalakan
        lock_x = self.lever.centerx - (lock_width // 2) # Di tengah horizontal tuas
        # Posisikan gembok agar bagian bawahnya sejajar dengan bagian bawah tuas
        lock_y = self.lever.bottom - lock_height # Bagian bawah gembok sejajar dengan bagian bawah tuas
        self.lock_red_rect = pygame.Rect(lock_x, lock_y, lock_width, lock_height)
        self.is_lever_unlocked = False # Status gembok (false = terkunci)


        # --- Kunci (Key) ---
        # Posisikan kunci di suatu tempat yang dapat dijangkau pemain, jauh dari tuas awalnya
        key_x = 150 # Contoh posisi X kunci (sesuaikan)
        key_y = SCREEN_HEIGHT - 450 - self.key_red_img.get_height() # Di atas lantai, gunakan tinggi gambar kunci yang diskalakan
        self.key_red_rect = pygame.Rect(key_x, key_y, self.key_red_img.get_width(), self.key_red_img.get_height())
        self.player_has_key_red = False # Status apakah pemain sudah mengambil kunci
        self.key_used = False # Status apakah kunci sudah digunakan untuk membuka gembok


        # Simpan posisi Y saat ini dari platform yang dapat digerakkan
        self._current_platform_y = self.movable_platform_start_pos.y


    # Metode update - memperbarui status level dan objek-objeknya
    # Tambahkan player_rect sebagai argumen untuk konsistensi panggilan dari game.py
    def update(self, dt, player_rect): # <-- TAMBAHKAN player_rect DI SINI
        # ... sisa kode method update Level3 ...
        # Di dalam method, Anda tetap bisa menggunakan self.player.rect jika objek player disimpan sebagai self.player
        # atau gunakan player_rect yang dilewatkan. Keduanya akan merujuk ke Rect pemain saat ini.

        # --- Logika Kunci (Key) ---
        # Hanya proses logika kunci jika kunci belum digunakan
        if not self.key_used:
            if not self.player_has_key_red:
                # Cek apakah pemain bertabrakan dengan kunci
                # Gunakan player_rect yang dilewatkan
                if player_rect.colliderect(self.key_red_rect): # <-- Gunakan player_rect di sini
                     self.player_has_key_red = True
                     if self.sfx_key_pickup:
                          self.sfx_key_pickup.play()
                     # Kunci diambil, tidak perlu lagi Rect fisik di list obstacles jika ada

            else: # Jika pemain sudah memiliki kunci (dan kunci belum digunakan)
                # Buat kunci mengikuti pemain
                # Sesuaikan offset jika kunci perlu digambar di samping atau di atas pemain
                offset_x = 10 # Sesuaikan offset horizontal kunci dari pusat pemain
                offset_y = -10 # Sesuaikan offset vertikal kunci dari pusat pemain
                # Gunakan centerx dan centery dari player_rect yang dilewatkan
                self.key_red_rect.centerx = player_rect.centerx + offset_x # <-- Gunakan player_rect di sini
                self.key_red_rect.centery = player_rect.centery + offset_y # <-- Gunakan player_rect di sini

                # --- Logika Membuka Gembok dengan Kunci ---
                # Hanya cek jika gembok masih terkunci dan lock_red_rect masih ada
                if not self.is_lever_unlocked and self.lock_red_rect is not None:
                     # Cek apakah kunci (mengikuti pemain) bertabrakan dengan gembok
                     if self.key_red_rect.colliderect(self.lock_red_rect):
                          self.is_lever_unlocked = True # Gembok terbuka!
                          self.key_used = True # Kunci sudah digunakan, jadi menghilang
                          if self.sfx_lock_open:
                               self.sfx_lock_open.play()
                          # Secara opsional, Anda bisa menghapus Rect gembok agar tidak ada tabrakan lagi
                          # self.lock_red_rect = None


        # --- Logika Tuas (Lever) ---
        # Tuas hanya bisa diinteraksi HANYA jika gembok sudah terbuka
        if self.is_lever_unlocked:
            interaction_area = self.lever.inflate(10, 10) # Buat area interaksi sedikit lebih besar dari tuas
            # Gunakan player_rect yang dilewatkan untuk cek tabrakan
            if player_rect.colliderect(interaction_area): # <-- Gunakan player_rect di sini
                self.lever.is_interactable = True # Tandai tuas bisa diinteraksi
                keys = pygame.key.get_pressed()
                # Deteksi input interaksi (hanya tombol E) saat bisa diinteraksi dan tidak cooldown
                if keys[pygame.K_e] and self._can_interact_lever:
                     self.lever.toggle() # Ubah status tuas
                     if self.sfx_lever:
                          self.sfx_lever.play()

                     self._can_interact_lever = False
                     self._lever_cooldown_timer = 0.5

            else:
                self.lever.is_interactable = False # Tidak bisa diinteraksi jika pemain menjauh
        else:
            # Jika gembok masih terkunci, tuas tidak bisa diinteraksi
            self.lever.is_interactable = False
            # Pastikan tuas kembali ke posisi awal jika gembok terkunci (opsional, bisa disesuaikan)
            # self.lever.is_up = True


        # Kelola cooldown tuas
        if not self._can_interact_lever:
             self._lever_cooldown_timer -= dt
             if self._lever_cooldown_timer <= 0:
                  self._can_interact_lever = True


        # --- Logika Pergerakan Platform Utama (Dikontrol Tuas) ---
        # Target Y platform tergantung pada status tuas
        target_y = self.movable_platform_start_pos.y if self.lever.is_up else self.movable_platform_end_pos.y
        distance_to_target = target_y - self._current_platform_y
        move_amount = self.movable_platform_speed * dt

        old_movable_platform_y = self.movable_platform_rect.y

        if distance_to_target > 0:
             self._current_platform_y += min(move_amount, distance_to_target)
        elif distance_to_target < 0:
             self._current_platform_y += max(-move_amount, distance_to_target)

        self.movable_platform_rect.y = int(self._current_platform_y)
        actual_platform_move_y = self.movable_platform_rect.y - old_movable_platform_y


        # Tangani pemain di atas platform bergerak
        # Gunakan player_rect yang dilewatkan untuk cek tabrakan
        if player_rect.colliderect(self.movable_platform_rect): # <-- Gunakan player_rect di sini
             if self.player.vel.y >= 0 and \
                abs(player_rect.bottom - self.movable_platform_rect.top) < 5: # <-- Gunakan player_rect di sini
                  # Modifikasi rect pemain di sini
                  player_rect.y += actual_platform_move_y # <-- Modifikasi player_rect
                  self.player.on_ground = True # Asumsikan player.on_ground juga perlu di-set

        # --- Cek Selesai Level ---
        # Cek apakah pemain mencapai tanda Exit
        # Gunakan player_rect yang dilewatkan untuk cek tabrakan
        if player_rect.colliderect(self.exit_rect): # <-- Gunakan player_rect di sini
            self.completed = True # Set flag completed


    def draw(self, screen):
        # Gambar rintangan (lantai)
        for rect in self.obstacles:
             is_bridge_rect = rect in self.bridge_platforms_rects
             is_exit_rect = rect is self.exit_rect

             if not is_bridge_rect and not is_exit_rect:
                 h = rect.height
                 if h not in self._cache:
                     scaled = pygame.transform.scale(self.block_img, (self.orig_w, h))
                     self._cache[h] = scaled
                 tile_surf = self._cache[h]
                 count = math.ceil(rect.width / self.orig_w)
                 for i in range(count):
                     x = rect.x + i * self.orig_w
                     screen.blit(tile_surf, (x, rect.y))

        # Gambar Tanda Exit
        screen.blit(self.exit_img, self.exit_rect.topleft)

        # --- Gambar Platform Bridge ---
        w_bridge, h_bridge = self.bridge_img.get_size()
        for rect in self.bridge_platforms_rects:
             # Gambar platform bridge hanya jika Rect-nya ada di obstacles
             if rect in self.obstacles: # Ini memastikan platform bergerak digambar saat aktif
                  for x in range(rect.left, rect.right, w_bridge):
                       if x + w_bridge > rect.right:
                            pass
                       else:
                            screen.blit(self.bridge_img, (x, rect.top))


        # Gambar Tuas
        self.lever.draw(screen)

        # --- Gambar Gembok (Lock) ---
        # Gambar gembok HANYA jika tuas masih terkunci dan lock_red_rect ada
        if not self.is_lever_unlocked and self.lock_red_rect is not None:
             screen.blit(self.lock_red_img, self.lock_red_rect.topleft)


        # --- Gambar Kunci (Key) ---
        # Gambar kunci HANYA jika pemain belum mengambilnya DAN kunci belum digunakan
        if not self.player_has_key_red and not self.key_used:
             # Gambar kunci di posisi self.key_red_rect (posisi awal)
             screen.blit(self.key_red_img, self.key_red_rect.topleft)
        # Jika pemain sudah mengambil kunci TAPI kunci belum digunakan, gambar kunci mengikuti pemain
        elif self.player_has_key_red and not self.key_used:
             screen.blit(self.key_red_img, self.key_red_rect.topleft)


        # Opsional: Gambar indikator interaksi tuas
        if self.lever.is_interactable:
             font = pygame.font.SysFont(None, 24)
             text_surf = font.render("Press E", True, (255, 255, 255))
             text_rect = text_surf.get_rect(center=(self.lever.centerx, self.lever.top - 20))
             screen.blit(text_surf, text_rect)

        # Opsional: Gambar indikator untuk mengambil kunci
        # Tampilkan instruksi ini jika pemain belum punya kunci dan dekat dengan kunci
        if not self.player_has_key_red and not self.key_used and self.player.rect.colliderect(self.key_red_rect.inflate(10,10)):
             font = pygame.font.SysFont(None, 24)
             text_surf = font.render("Touch to take key", True, (255, 255, 255))
             text_rect = text_surf.get_rect(center=(self.key_red_rect.centerx, self.key_red_rect.top - 20))
             screen.blit(text_surf, text_rect)

        # Opsional: Gambar indikator untuk membuka gembok
        # Tampilkan instruksi ini jika pemain punya kunci, gembok masih ada, dan pemain dekat dengan gembok
        if self.player_has_key_red and not self.is_lever_unlocked and self.lock_red_rect is not None and self.player.rect.colliderect(self.lock_red_rect.inflate(10,10)):
             font = pygame.font.SysFont(None, 24)
             text_surf = font.render("Touch lock with key", True, (255, 255, 255))
             text_rect = text_surf.get_rect(center=(self.lock_red_rect.centerx, self.lock_red_rect.top - 20))
             screen.blit(text_surf, text_rect)