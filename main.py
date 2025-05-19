import pygame
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from src.game import Game

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Agus Turtle")
    game = Game(screen)
    game.run()
    pygame.quit()

if __name__ == "__main__":
<<<<<<< HEAD
    main()
=======
    main()
>>>>>>> 066713d7379e26e752460a32ca73c8cee73c0ca0
