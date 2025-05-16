# PEMBUATAN GAME/src/main.py
# Berisi logika utama aplikasi/game loop

import pygame
import math
import os

# Import dari modul di dalam package src
from .constants import * # Import konstanta
from .game import Game     # Import kelas Game

def run_game():
    """Fungsi utama untuk menjalankan game Pygame."""

    # 1. Inisialisasi Pygame
    pygame.init()

    # 2. Konfigurasi Jendela Game
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Agus Turtle")

    # 3. Clock untuk mengontrol frame rate
    clock = pygame.time.Clock()

    # 4. Font
    # Font sudah diinisialisasi di pygame.init()
    font_large = pygame.font.SysFont('Arial', 50)
    font_medium = pygame.font.SysFont('Arial', 30)

    # --- 5. Memuat Aset (Gambar) ---
    bob_image = None
    block_image = None
    lever_up_image = None
    lever_down_image = None
    door_image = None 
    
    try:
        # os.path.join akan berfungsi karena kita akan menjalankan skrip ini
        # dengan working directory di root proyek, tempat folder assets berada
        bob_image = pygame.image.load(os.path.join(ASSET_DIR, BOB_IMAGE_FILE)).convert_alpha()
        block_image = pygame.image.load(os.path.join(ASSET_DIR, BLOCK_IMAGE_FILE)).convert()
        lever_up_image = pygame.image.load(os.path.join(ASSET_DIR, LEVER_UP_IMAGE_FILE)).convert_alpha()
        lever_down_image = pygame.image.load(os.path.join(ASSET_DIR, LEVER_DOWN_IMAGE_FILE)).convert_alpha()
        door_image = pygame.image.load(os.path.join(ASSET_DIR, DOOR_IMAGE_FILE)).convert_alpha() 
        print("Aset berhasil dimuat!")
    except pygame.error as e:
        print(f"Gagal memuat aset: {e}")
        print(f"Pastikan kamu memiliki folder '{ASSET_DIR}' di root direktori proyekmu (folder PEMBUATAN GAME).")
        print(f"Di dalam folder '{ASSET_DIR}', pastikan ada file '{BOB_IMAGE_FILE}', '{BLOCK_IMAGE_FILE}', '{LEVER_UP_IMAGE_FILE}', dan '{LEVER_DOWN_IMAGE_FILE}'.")
        pygame.quit()
        exit()

    # 6. Elemen UI Menu
    menu_title_text_surface = font_large.render(" Agus Turtle ", True, WHITE)
    menu_title_rect = menu_title_text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))

    play_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, 200, 50)
    play_button_text_surface = font_medium.render("Main", True, BLACK)
    play_button_text_rect = play_button_text_surface.get_rect(center=play_button_rect.center)

    # 7. Elemen UI Pemilihan Level
    level_select_title_text_surface = font_large.render("Pilih Level", True, WHITE)
    level_select_title_rect = level_select_title_text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))

    level1_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT // 2, 150, 50)
    level1_button_text_surface = font_medium.render("Level 1", True, BLACK)
    level_select_title_text_surface = font_large.render("Pilih Level", True, WHITE)
    level_select_title_rect = level_select_title_text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))

    level1_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT // 2, 150, 50)
    level1_button_text_surface = font_medium.render("Level 1", True, BLACK)
        # Perbaiki baris ini: Ambil center dari level1_button_rect
    level1_button_text_rect = level1_button_text_surface.get_rect(center=level1_button_rect.center)

    # 8. Inisialisasi objek Game
    # Objek game akan menangani state PLAYING
    game = Game(screen, bob_image, block_image, lever_up_image, lever_down_image, door_image)
    
    # Di src/main.py, setelah baris block_image = ...
    print(f"Ukuran block_image: {block_image.get_width()}x{block_image.get_height()} piksel")

    # 9. State Game Saat Ini
    game_state = STATE_MENU

    # 10. Loop Permainan Utama
    running = True

    while running:
        # 11. Penanganan Event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos

                # Tangani event berdasarkan state game saat ini
                if game_state == STATE_MENU:
                    if play_button_rect.collidepoint(mouse_pos):
                        game_state = STATE_LEVEL_SELECT

                elif game_state == STATE_LEVEL_SELECT:
                    if level1_button_rect.collidepoint(mouse_pos):
                         # Coba mulai level di objek game
                         if game.start_level(1): # start_level mengembalikan True jika berhasil
                             game_state = STATE_PLAYING # Ganti state hanya jika level berhasil dimulai

                elif game_state == STATE_PLAYING:
                    # Delegasikan event yang relevan ke objek game jika kita di state PLAYING
                    # Objek game akan mengembalikan True jika event ditangani
                    game.handle_event(event) # Contoh: klik pada Bob


        # 12. Update Logika Game (jika di state PLAYING)
        if game_state == STATE_PLAYING:
            game.update() # Panggil method update di objek game
            
        # --- Cek apakah level selesai setelah update ---
            if game.level_completed:
                print("Mengubah state ke pemilihan level...")
                game_state = STATE_LEVEL_SELECT # <-- Ubah state game

        # 13. Menggambar (Rendering)
        screen.fill(BLACK) # Warna dasar untuk menu/pemilihan level

        if game_state == STATE_MENU:
            # Gambar elemen Menu
            screen.blit(menu_title_text_surface, menu_title_rect)
            pygame.draw.rect(screen, GRAY, play_button_rect)
            screen.blit(play_button_text_surface, play_button_text_rect)

        elif game_state == STATE_LEVEL_SELECT:
            # Gambar elemen Pemilihan Level
            screen.blit(level_select_title_text_surface, level_select_title_rect)
            pygame.draw.rect(screen, GRAY, level1_button_rect)
            screen.blit(level1_button_text_surface, level1_button_text_rect)

        elif game_state == STATE_PLAYING:
            # Gambar background level menggunakan warna dari objek game
            screen.fill(game.background_color)
            # Delegasikan menggambar elemen level (rintangan, Bob) ke objek game
            game.draw()


        # 14. Memperbarui Tampilan
        pygame.display.flip()

        # 15. Mengontrol Kecepatan Frame
        clock.tick(60)

    # 16. Keluar dari Pygame
    # Ini akan dipanggil saat loop 'running' berakhir
    pygame.quit()

# --- Tidak perlu blok if __name__ == "__main__": di sini ---
# File ini dirancang untuk di-import dan fungsi run_game() dipanggil dari luar package