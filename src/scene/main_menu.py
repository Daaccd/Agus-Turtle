# src/scene/main_menu.py

import pygame
from src.constants import MENU_ITEMS, COLOR_WHITE, COLOR_SKY, COLOR_HIGHLIGHT, SCREEN_WIDTH

class MainMenu:
    def __init__(self, screen):
        self.screen   = screen
        self.selected = 0
        self.font     = pygame.font.SysFont(None, 48)
        self.item_rects = []
        for idx, item in enumerate(MENU_ITEMS):
            surf = self.font.render(item, True, COLOR_WHITE)
            rect = surf.get_rect(center=(SCREEN_WIDTH//2, 200 + idx * 60))
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

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # kiri
            mx, my = event.pos
            for idx, rect in enumerate(self.item_rects):
                if rect.collidepoint(mx, my):
                    return MENU_ITEMS[idx]

        return None

    def update(self):
        pass

    def draw(self):
        self.screen.fill(COLOR_SKY)
        for idx, item in enumerate(MENU_ITEMS):
            color = COLOR_HIGHLIGHT if idx == self.selected else COLOR_WHITE
            surf = self.font.render(item, True, color)
            rect = self.item_rects[idx]
            self.screen.blit(surf, rect)
