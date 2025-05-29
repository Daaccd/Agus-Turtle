import pygame
from src.constants import COLOR_WHITE, COLOR_HIGHLIGHT, SCREEN_WIDTH, SCREEN_HEIGHT

class OptionMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.SysFont(None, 64)
        self.font_option = pygame.font.SysFont(None, 48)
        self.font_instruction = pygame.font.SysFont(None, 36)

        self.options = ["Volume", "Back to Main Menu"]
        self.selected = 0 # Indeks opsi yang sedang dipilih

        # Item Rects (untuk posisi, bukan rendering teks dinamis)
        self.item_rects = []
        # Posisi Title
        self.title_surf = self.font_title.render("Options", True, COLOR_WHITE)
        self.title_rect = self.title_surf.get_rect(center=(SCREEN_WIDTH // 2, 100))

        # Posisi Opsi (dihitung sekali)
        for idx, item in enumerate(self.options):
            # Gunakan teks placeholder untuk menghitung ukuran awal agar rect tidak bergeser jauh
            temp_text = item
            if item == "Volume":
                temp_text = "Volume: 100%" # Teks terpanjang yang mungkin untuk volume
            
            surf = self.font_option.render(temp_text, True, COLOR_WHITE)
            rect = surf.get_rect(center=(SCREEN_WIDTH // 2, 250 + idx * 70))
            self.item_rects.append(rect)

        # Posisi Instruksi
        self.instruction_surf = self.font_instruction.render("Use LEFT/RIGHT to change volume", True, COLOR_WHITE)
        self.instruction_rect = self.instruction_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))

    def handle_input(self, event):
        result = None
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.options)
            elif self.selected == 0: # Opsi "Volume" terpilih
                current_mixer_volume = pygame.mixer.music.get_volume()
                if event.key == pygame.K_LEFT:
                    new_volume = max(0.0, current_mixer_volume - 0.05) # Turun 5%
                    pygame.mixer.music.set_volume(new_volume)
                elif event.key == pygame.K_RIGHT:
                    new_volume = min(1.0, current_mixer_volume + 0.05) # Naik 5%
                    pygame.mixer.music.set_volume(new_volume)
            elif event.key == pygame.K_RETURN:
                if self.selected == 1: # Opsi "Back to Main Menu" terpilih
                    result = "Back" # Mengembalikan string untuk memberitahu Game class
            elif event.key == pygame.K_ESCAPE:
                result = "Back" # ESC juga berfungsi sebagai "Back"
        return result

    def update(self):
        # Untuk menu opsi sederhana ini, tidak ada logika update yang kompleks
        # Perubahan volume langsung ditangani di handle_input
        pass

    def draw(self):
        self.screen.fill((50, 50, 50)) # Latar belakang abu-abu

        # Gambar judul
        self.screen.blit(self.title_surf, self.title_rect)

        # Gambar opsi
        for idx, item_text in enumerate(self.options):
            color = COLOR_HIGHLIGHT if idx == self.selected else COLOR_WHITE
            
            display_text = item_text
            if item_text == "Volume":
                # Ambil volume aktual dari mixer untuk ditampilkan
                current_volume_percentage = int(pygame.mixer.music.get_volume() * 100)
                display_text = f"Volume: {current_volume_percentage}%"

            surf = self.font_option.render(display_text, True, color)
            
            # Gunakan rect yang sudah dihitung, tapi pastikan teksnya di tengah
            # Recalculate rect center to ensure dynamic text is centered
            rect = surf.get_rect(center=self.item_rects[idx].center)
            self.screen.blit(surf, rect)

        # Gambar instruksi (hanya tampil jika opsi volume terpilih)
        if self.selected == 0:
            self.screen.blit(self.instruction_surf, self.instruction_rect)