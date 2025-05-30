import pygame
from src.constants import COLOR_WHITE, COLOR_HIGHLIGHT, SCREEN_WIDTH, SCREEN_HEIGHT

class OptionMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.SysFont(None, 64)
        self.font_option = pygame.font.SysFont(None, 48)
        self.font_instruction = pygame.font.SysFont(None, 36)

        self.options = ["Volume", "Back to Main Menu"]
        self.selected = 0

        self.item_rects = []
        self.title_surf = self.font_title.render("Options", True, COLOR_WHITE)
        self.title_rect = self.title_surf.get_rect(center=(SCREEN_WIDTH // 2, 100))

        for idx, item in enumerate(self.options):
            temp_text = item
            if item == "Volume":
                temp_text = "Volume: 100%"
            
            surf = self.font_option.render(temp_text, True, COLOR_WHITE)
            rect = surf.get_rect(center=(SCREEN_WIDTH // 2, 250 + idx * 70))
            self.item_rects.append(rect)

        self.instruction_surf = self.font_instruction.render("Use LEFT/RIGHT to change volume", True, COLOR_WHITE)
        self.instruction_rect = self.instruction_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))

    def handle_input(self, event):
        result = None
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.options)
            elif self.selected == 0:
                current_mixer_volume = pygame.mixer.music.get_volume()
                if event.key == pygame.K_LEFT:
                    new_volume = max(0.0, current_mixer_volume - 0.05)
                    pygame.mixer.music.set_volume(new_volume)
                elif event.key == pygame.K_RIGHT:
                    new_volume = min(1.0, current_mixer_volume + 0.05)
                    pygame.mixer.music.set_volume(new_volume)
            elif event.key == pygame.K_RETURN:
                if self.selected == 1:
                    result = "Back"
            elif event.key == pygame.K_ESCAPE:
                result = "Back"
        return result

    def update(self):
        pass

    def draw(self):
        self.screen.fill((50, 50, 50))

        self.screen.blit(self.title_surf, self.title_rect)

        for idx, item_text in enumerate(self.options):
            color = COLOR_HIGHLIGHT if idx == self.selected else COLOR_WHITE
            
            display_text = item_text
            if item_text == "Volume":
                current_volume_percentage = int(pygame.mixer.music.get_volume() * 100)
                display_text = f"Volume: {current_volume_percentage}%"

            surf = self.font_option.render(display_text, True, color)
            rect = surf.get_rect(center=self.item_rects[idx].center)
            self.screen.blit(surf, rect)

        if self.selected == 0:
            self.screen.blit(self.instruction_surf, self.instruction_rect)