# src/scene/level1.py
import pygame
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT, BLUE_SKY, MOVABLE_WALL_SPEED
from src.characters.player import Player # Import kelas Player

# 100(lokasi dari kiri, -100(lokasi dari bawah), 100(lebar), 100(tinggi))

class Level1:
    def __init__(self, images: dict):
        # define where the player starts
        self.wall_should_move = False  # Start as False
        self.player_start      = (50, SCREEN_HEIGHT - 100)
        self.wall_initial_y = SCREEN_HEIGHT - 50   # Posisi bawah
        self.wall_target_y  = SCREEN_HEIGHT - 300  # Posisi atas

        # static ground/platforms
        floor = pygame.Rect(0, SCREEN_HEIGHT-50, SCREEN_WIDTH, 50)
        self.static_obstacles = [floor]
        # 100(lokasi dari kiri, - 100(lokasi dari bawah), 100(lebar), 100(tinggi))
        # moving wall (platform)
        wall_rect = pygame.Rect(400, SCREEN_HEIGHT - 50, 400, 50)
        self.movable_walls    = [wall_rect]

        self.wall_speed       = MOVABLE_WALL_SPEED

        # lever to trigger the wall
        self.lever_rect       = pygame.Rect(300, SCREEN_HEIGHT - 100, 100, 100) # Gunakan ukuran yang lebih besar
        self.lever_state      = 'up' # Inisiasi lever state
        # 100(lokasi dari kiri, - 100(lokasi dari bawah), 100(lebar), 100(tinggi))
        # exit door
        self.door_rect        = pygame.Rect(SCREEN_WIDTH-80, SCREEN_HEIGHT-400, 50, 80)

        self.background_color = BLUE_SKY

    def handle_event(self, event: pygame.event.Event, player: Player | None):
        # Tangani event KEYDOWN untuk tombol 'F'
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:
                # print("Tombol F ditekan.") # Debug
                # print(f"Player Rect: {player.rect}") # Debug
                # print(f"Lever Rect: {self.lever_rect}") # Debug

                # Cek apakah player ada dan player rect bertabrakan dengan lever rect
                if player is not None and player.rect.colliderect(self.lever_rect):
                    # print("Pemain bertabrakan dengan tuas!") # Debug
                    # Toggle lever state
                    if self.lever_state == 'up':
                         self.lever_state = 'down'
                    else:
                         self.lever_state = 'up'
                    self.wall_should_move = True  # Izinkan dinding bergerak setelah tuas diklik
                    # print(f"Lever State: {self.lever_state}, Wall Should Move: {self.wall_should_move}") # Debug
                 # else:
                      # print("Pemain TIDAK bertabrakan dengan tuas.") # Debug


    # Modifikasi metode update untuk menangani tabrakan dinding bergerak dengan pemain
    def update(self, player: Player | None):
        if not self.wall_should_move:
            return  # Jangan gerakkan dinding jika flag mati

        # Tentukan target Y berdasarkan lever state
        target_y = self.wall_target_y if self.lever_state == 'down' else self.wall_initial_y

        # Iterasi melalui setiap dinding yang bergerak
        for wall in self.movable_walls:
            # Hitung posisi dinding di frame berikutnya jika bergerak
            next_wall_top = wall.top
            movement_applied = False # Flag untuk menandai apakah ada pergerakan yang diterapkan di frame ini

            # Logika pergerakan dinding menuju target
            if self.lever_state == 'down': # Target adalah posisi atas (wall_target_y)
                if wall.top > target_y: # Jika dinding di bawah target atas, bergerak ke atas
                    next_wall_top -= self.wall_speed # Gerak ke atas
                    movement_applied = True
                    # Pastikan tidak melewati target
                    if next_wall_top < target_y:
                        next_wall_top = target_y

            elif self.lever_state == 'up': # Target adalah posisi bawah (wall_initial_y)
                if wall.top < target_y: # Jika dinding di atas target bawah, bergerak ke bawah
                    next_wall_top += self.wall_speed # Gerak ke bawah
                    movement_applied = True
                    # Pastikan tidak melewati target
                    if next_wall_top > target_y:
                        next_wall_top = target_y

            # Jika tidak ada pergerakan yang diterapkan di blok di atas, lewati sisa loop untuk dinding ini
            if not movement_applied:
                 continue


            # Buat rect sementara untuk posisi berikutnya untuk mengecek tabrakan
            next_wall_rect = wall.copy()
            next_wall_rect.top = next_wall_top

            # Cek tabrakan dengan pemain PADA POSISI BERIKUTNYA
            player_collision_at_next = False
            if player is not None and player.rect.colliderect(next_wall_rect):
                 player_collision_at_next = True

            # Tentukan apakah dinding harus bergerak berdasarkan potensi tabrakan dan arah
            should_move = True
            if player_collision_at_next:
                # Jika akan bertabrakan:
                if self.lever_state == 'down': # Bergerak ke atas menuju target atas
                     # Jika bergerak ke atas dan bertabrakan, HENTIKAN HANYA jika pemain berada di atas dinding SAAT INI
                     # (artinya dinding seharusnya tidak mengangkatnya)
                     # Jika bagian atas dinding SAAT INI di bawah atau sama dengan bagian bawah pemain SAAT INI,
                     # itu kemungkinan tabrakan "mengangkat" -> IZINKAN pergerakan
                    # Gunakan posisi wall.top saat ini vs player.rect.bottom saat ini
                    if wall.top >= player.rect.bottom - 2: # Tabrakan mengangkat - IZINKAN
                         should_move = True
                    else:
                         should_move = False # Tabrakan lain saat gerak ke atas - HENTIKAN

                elif self.lever_state == 'up': # Bergerak ke bawah menuju target bawah
                     # Jika bergerak ke bawah dan bertabrakan -> HENTIKAN (squish dari atas)
                     should_move = False


            # Terapkan pergerakan jika diizinkan
            if should_move:
                wall.top = next_wall_top


            # Opsi: Hentikan pergerakan sepenuhnya jika sudah sampai target
            # if wall.top == target_y:
            #     self.wall_should_move = False # Matikan flag setelah mencapai target


    def draw(self, screen: pygame.Surface, block_image: pygame.Surface):
        # tile static & movable blocks
        for rect in self.static_obstacles + self.movable_walls:
            w,h = block_image.get_size()
            for x in range(rect.left, rect.right, w):
                for y in range(rect.top, rect.bottom, h):
                    screen.blit(block_image, (x,y))

    def draw_overlays(self, screen: pygame.Surface, images: dict):
        # draw lever
        img = images['lever_down'] if self.lever_state=='down' else images['lever_up']
        screen.blit(img, self.lever_rect.topleft)
