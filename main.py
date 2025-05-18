# main.py
import pygame
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from src.game import Game

def run_game():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Agus Turtle")
    clock = pygame.time.Clock()

    # Load images
    images = {
        'bob':        pygame.image.load('assets/images/bob.png').convert_alpha(),
        'block':      pygame.image.load('assets/images/block.png').convert_alpha(),
        'lever_up':   pygame.image.load('assets/images/lever_up.png').convert_alpha(),
        'lever_down': pygame.image.load('assets/images/lever_down.png').convert_alpha(),
        'door':       pygame.image.load('assets/images/door.png').convert_alpha(),
    }

    game = Game(screen, images)
    STATE_MENU, STATE_LEVEL, STATE_PLAY = 0, 1, 2
    state = STATE_MENU

    # Prepare simple UI texts
    font_big   = pygame.font.SysFont('Arial', 48)
    font_small = pygame.font.SysFont('Arial', 32)
    btn_main   = font_small.render('Main', True, (255,255,255))
    btn_rect   = btn_main.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))

    level_text = font_big.render('Pilih Level', True, (255,255,255))
    lvl_btn    = font_small.render('Level 1',  True, (255,255,255))
    lvl_rect   = lvl_btn.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 80))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if state == STATE_MENU and btn_rect.collidepoint(event.pos):
                    state = STATE_LEVEL
                elif state == STATE_LEVEL and lvl_rect.collidepoint(event.pos):
                    if game.start_level(1):
                        state = STATE_PLAY
                elif state == STATE_PLAY:
                    game.handle_event(event)

        if state == STATE_PLAY:
            game.update()
            if game.level_completed:
                state = STATE_LEVEL

        screen.fill((0,0,0))
        if state == STATE_MENU:
            screen.blit(btn_main, btn_rect)
        elif state == STATE_LEVEL:
            screen.blit(level_text, (SCREEN_WIDTH//2 - level_text.get_width()//2, 100))
            screen.blit(lvl_btn, lvl_rect)
        elif state == STATE_PLAY:
            game.draw()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == '__main__':
    run_game()
