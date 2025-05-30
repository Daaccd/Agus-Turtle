import pygame
from src.constants import LEVELS, COLOR_WHITE, COLOR_HIGHLIGHT, SCREEN_WIDTH

class LevelSelect:
    def __init__(self, screen, game):
        self.screen   = screen
        self.game = game
        self.selected = 0
        self.font     = self.game.font_medium

        self.item_rects = []
        for idx, lvl in enumerate(LEVELS):
            surf = self.font.render(lvl, True, COLOR_WHITE)
            rect = surf.get_rect(center=(SCREEN_WIDTH//2, 250 + idx * 60))
            self.item_rects.append(rect)

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(LEVELS)
                return None
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(LEVELS)
                return None
            elif event.key == pygame.K_RETURN:
                return LEVELS[self.selected]
            elif event.key == pygame.K_ESCAPE:
                return "Back"

        elif event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            for idx, rect in enumerate(self.item_rects):
                if rect.collidepoint(mx, my):
                    self.selected = idx

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            for idx, rect in enumerate(self.item_rects):
                if rect.collidepoint(mx, my):
                    return LEVELS[idx]

        return None

    def update(self):
        pass

    def draw(self):
        for idx, lvl in enumerate(LEVELS):
            color = COLOR_HIGHLIGHT if idx == self.selected else COLOR_WHITE
            surf = self.font.render(lvl, True, color)
            rect = self.item_rects[idx]
            self.screen.blit(surf, rect)
