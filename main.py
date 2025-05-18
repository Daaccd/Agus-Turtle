# main.py
import pygame
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from src.game import Game
from src.scene.level2 import Level2 # Import Level2
from src.scene.level1 import Level1 # Pastikan Level1 juga diimpor jika belum

def run_game():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Agus Turtle")
    clock = pygame.time.Clock()

    # Load images (Tambahkan 'bridge' ke dictionary ini)
    images = {
        'bob':        pygame.image.load('assets/images/bob.png').convert_alpha(),
        'block':      pygame.image.load('assets/images/block.png').convert_alpha(),
        'lever_up':   pygame.image.load('assets/images/lever_up.png').convert_alpha(),
        'lever_down': pygame.image.load('assets/images/lever_down.png').convert_alpha(),
        'door':       pygame.image.load('assets/images/door.png').convert_alpha(),
        'box':        pygame.image.load('assets/images/box.png').convert_alpha(),
        'bridge':     pygame.image.load('assets/images/bridge.png').convert_alpha(), # <<< Tambahkan ini
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

    # Tombol Level 1
    lvl_btn_1    = font_small.render('Level 1',  True, (255,255,255))
    lvl_rect_1   = lvl_btn_1.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 80))

    # Tombol Level 2
    lvl_btn_2    = font_small.render('Level 2',  True, (255,255,255))
    lvl_rect_2   = lvl_btn_2.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 140))


    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Logika klik mouse untuk menu/pemilihan level
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if state == STATE_MENU and btn_rect.collidepoint(event.pos):
                    state = STATE_LEVEL
                # Cek klik tombol Level 1
                elif state == STATE_LEVEL and lvl_rect_1.collidepoint(event.pos):
                    if game.start_level(1):
                        state = STATE_PLAY
                # Cek klik tombol Level 2
                elif state == STATE_LEVEL and lvl_rect_2.collidepoint(event.pos):
                     if game.start_level(2):
                         state = STATE_PLAY

            # Panggil game.handle_event() untuk SEMUA event saat STATE_PLAY
            if state == STATE_PLAY:
                 game.handle_event(event)


        # Update game state (dilakukan di luar loop event)
        if state == STATE_PLAY:
            game.update()
            if game.level_completed:
                state = STATE_LEVEL

        # Bagian drawing (dilakukan di luar loop event)
        screen.fill((0,0,0))
        if state == STATE_MENU:
            screen.blit(btn_main, btn_rect)
        elif state == STATE_LEVEL:
            screen.blit(level_text, (SCREEN_WIDTH//2 - level_text.get_width()//2, 100))
            screen.blit(lvl_btn_1, lvl_rect_1)
            screen.blit(lvl_btn_2, lvl_rect_2)
        elif state == STATE_PLAY:
            game.draw()


        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == '__main__':
    run_game()
