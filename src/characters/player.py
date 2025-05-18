# src/characters/player.py
import pygame
# >>> Pastikan Anda mengimpor SEMUA konstanta yang diperlukan, termasuk SCREEN_WIDTH dan SCREEN_HEIGHT <<<
from src.constants import GRAVITY, BOB_SPEED, JUMP_STRENGTH, GRAVITY_BOOST, SCREEN_WIDTH, SCREEN_HEIGHT

class Player(pygame.sprite.Sprite):
    def __init__(self, image: pygame.Surface, start_pos: tuple[int,int]):
        super().__init__()
        self.image    = image
        self.rect     = image.get_rect(topleft=start_pos)
        self.velocity = pygame.math.Vector2(0,0)
        self.moving_left  = False
        self.moving_right = False
        self.on_ground    = False
        self.fast_fall    = False
        self.jump_requested = False # Flag untuk permintaan lompatan (untuk perbaikan bug lompatan)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                self.moving_left = True
            elif event.key == pygame.K_d:
                self.moving_right = True
            elif event.key == pygame.K_w:
                # >>> Logika permintaan lompatan hanya set flag, eksekusi di update <<<
                self.jump_requested = True
            elif event.key == pygame.K_s:
                 self.fast_fall = True

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                self.moving_left = False
            elif event.key == pygame.K_d:
                self.moving_right = False
            elif event.key == pygame.K_s:
                 self.fast_fall = False
            # Tidak perlu menangani KEYUP untuk K_w dengan pola jump_requested

    def update(self, static_blocks: list[pygame.Rect], movable_walls: list[pygame.Rect]):
        # --- Bagian Pergerakan Vertikal & Gravitasi ---
        self.velocity.y += GRAVITY
        if self.fast_fall and not self.on_ground:
             self.velocity.y += GRAVITY_BOOST

        if self.velocity.y > 15: # Sesuaikan batas kecepatan jatuh
             self.velocity.y = 15

        self.rect.y += int(self.velocity.y)

        # Deteksi tumbukan vertikal
        self.on_ground = False # Reset status di tanah setiap update
        for block in static_blocks + movable_walls:
            if self.rect.colliderect(block):
                if self.velocity.y > 0:
                    self.rect.bottom = block.top
                    self.velocity.y = 0
                    self.on_ground = True # Pemain berada di tanah setelah tumbukan ini
                elif self.velocity.y < 0:
                    self.rect.top = block.bottom
                    self.velocity.y = 0

        # --- Logika Lompatan (Setelah Deteksi Tumbukan Vertikal) ---
        # >>> Eksekusi lompatan HANYA jika permintaan ada DAN pemain di tanah <<<
        if self.jump_requested and self.on_ground:
            self.velocity.y = JUMP_STRENGTH
            self.on_ground = False

        self.jump_requested = False # Reset permintaan lompatan setelah diproses


        # --- Bagian Pergerakan Horizontal & Tumbukan ---
        self.velocity.x = 0 # Reset kecepatan horizontal
        if self.moving_left:
            self.velocity.x -= BOB_SPEED
        if self.moving_right:
            self.velocity.x += BOB_SPEED

        self.rect.x += int(self.velocity.x)

        # Deteksi tumbukan horizontal
        for block in static_blocks + movable_walls:
             if self.rect.colliderect(block):
                 if self.velocity.x > 0:
                     self.rect.right = block.left
                 elif self.velocity.x < 0:
                     self.rect.left = block.right

        # --- Pemeriksaan Batas Layar ---
        # >>> BAGIAN INI PENTING DAN HILANG DARI KODE YANG ANDA BERIKAN <<<
        # Batas horizontal
        if self.rect.left < 0:
            self.rect.left = 0
            # self.velocity.x = 0 # Opsi: hentikan pergerakan
        elif self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            # self.velocity.x = 0 # Opsi: hentikan pergerakan

        # Batas vertikal
        if self.rect.top < 0:
            self.rect.top = 0
            self.velocity.y = 0
        elif self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.velocity.y = 0
            self.on_ground = True # Dianggap di tanah jika di batas bawah


        # print(f"[PLAYER POS] x: {self.rect.x}, y: {self.rect.y}") # Komen atau hapus

    def draw(self, surface: pygame.Surface):
        surface.blit(self.image, self.rect.topleft)
