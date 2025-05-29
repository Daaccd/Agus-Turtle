import pygame, os
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT, IMAGES_DIR
from src.game import Game

def main():
    pygame.init()
    pygame.mixer.init()
    try:
        icon_path = os.path.join(IMAGES_DIR, "kurakura.png")
        game_icon = pygame.image.load(icon_path)
        pygame.display.set_icon(game_icon)
    except pygame.error as e:
        print(f"Tidak dapat memuat ikon: {icon_path} - {e}")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Agus Turtle")
    game = Game(screen)
    game.run()
    pygame.quit()

if __name__ == "__main__":
    main()