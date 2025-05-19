<<<<<<< HEAD
# src/scene/main_menu.py

=======
>>>>>>> 066713d7379e26e752460a32ca73c8cee73c0ca0
import pygame
from src.constants import MENU_ITEMS, COLOR_WHITE, COLOR_HIGHLIGHT, SCREEN_WIDTH

class MainMenu:
    def __init__(self, screen):
<<<<<<< HEAD
        self.screen   = screen
        self.selected = 0
        self.font     = pygame.font.SysFont(None, 48)
        # hitung rect per item sekali saja
=======
        self.screen     = screen
        self.selected   = 0
        self.font       = pygame.font.SysFont(None, 48)
        # Precompute rect tiap item
>>>>>>> 066713d7379e26e752460a32ca73c8cee73c0ca0
        self.item_rects = []
        for idx, item in enumerate(MENU_ITEMS):
            surf = self.font.render(item, True, COLOR_WHITE)
            rect = surf.get_rect(center=(SCREEN_WIDTH//2, 200 + idx * 60))
            self.item_rects.append(rect)

    def handle_input(self, event):
        # Keyboard
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(MENU_ITEMS)
<<<<<<< HEAD
                return None
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(MENU_ITEMS)
                return None
            elif event.key == pygame.K_RETURN:
                return MENU_ITEMS[self.selected]

        # Mouse movement → hover effect
        elif event.type == pygame.MOUSEMOTION:
=======
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(MENU_ITEMS)
            elif event.key == pygame.K_RETURN:
                return MENU_ITEMS[self.selected]

        # Mouse hover
        if event.type == pygame.MOUSEMOTION:
>>>>>>> 066713d7379e26e752460a32ca73c8cee73c0ca0
            mx, my = event.pos
            for idx, rect in enumerate(self.item_rects):
                if rect.collidepoint(mx, my):
                    self.selected = idx

<<<<<<< HEAD
        # Mouse click → selection
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # kiri
=======
        # Mouse click
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
>>>>>>> 066713d7379e26e752460a32ca73c8cee73c0ca0
            mx, my = event.pos
            for idx, rect in enumerate(self.item_rects):
                if rect.collidepoint(mx, my):
                    return MENU_ITEMS[idx]

        return None

<<<<<<< HEAD
    def update(self):
        pass

=======
>>>>>>> 066713d7379e26e752460a32ca73c8cee73c0ca0
    def draw(self):
        self.screen.fill((0, 0, 0))
        for idx, item in enumerate(MENU_ITEMS):
            color = COLOR_HIGHLIGHT if idx == self.selected else COLOR_WHITE
<<<<<<< HEAD
            surf = self.font.render(item, True, color)
            rect = self.item_rects[idx]
=======
            surf  = self.font.render(item, True, color)
            rect  = self.item_rects[idx]
>>>>>>> 066713d7379e26e752460a32ca73c8cee73c0ca0
            self.screen.blit(surf, rect)
