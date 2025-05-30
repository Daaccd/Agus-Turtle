import pygame
from src.constants import MENU_ITEMS, COLOR_WHITE, COLOR_HIGHLIGHT, SCREEN_WIDTH, SCREEN_HEIGHT

class MainMenu:
    def __init__(self, screen, game): 
        self.screen   = screen
        self.game = game 
        self.selected = 0
        self.font     = self.game.font_medium
        
        try:
            background_original = self.game.resources.load_image("background")
            self.background_image = pygame.transform.scale(background_original, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except SystemExit: 
            print("Peringatan: Gambar latar belakang menu (background.jpeg) tidak ditemukan. Menggunakan warna solid.")
            self.background_image = None 
        except pygame.error as e:
            print(f"Peringatan: Gagal memuat atau menskalakan gambar latar belakang menu: {e}. Menggunakan warna solid.")
            self.background_image = None

        self.item_rects = []
        for idx, item in enumerate(MENU_ITEMS):
            surf = self.font.render(item, True, COLOR_WHITE) 
            rect = surf.get_rect(center=(SCREEN_WIDTH//2, 250 + idx * 60)) 
            self.item_rects.append(rect)

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(MENU_ITEMS)
                return None
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(MENU_ITEMS)
                return None
            elif event.key == pygame.K_RETURN:
                return MENU_ITEMS[self.selected]

        elif event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            for idx, rect in enumerate(self.item_rects):
                if rect.collidepoint(mx, my):
                    self.selected = idx

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            for idx, rect in enumerate(self.item_rects):
                if rect.collidepoint(mx, my):
                    return MENU_ITEMS[idx]

        return None

    def update(self):
        pass 

    def draw(self):
        if self.background_image:
            self.screen.blit(self.background_image, (0, 0))
        else:
            pass

        for idx, item in enumerate(MENU_ITEMS):
            color = COLOR_HIGHLIGHT if idx == self.selected else COLOR_WHITE
            surf = self.font.render(item, True, color)
            rect = self.item_rects[idx]
            self.screen.blit(surf, rect)
