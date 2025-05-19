from pathlib import Path
<<<<<<< HEAD
import pygame
import sys
import logging
=======
import pygame, sys, logging
>>>>>>> 066713d7379e26e752460a32ca73c8cee73c0ca0

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResourceManager:
    def __init__(self, base_path: Path):
        self.base_path = base_path
<<<<<<< HEAD
        self.cache = {}
=======
        self.cache     = {}
>>>>>>> 066713d7379e26e752460a32ca73c8cee73c0ca0

    def load_image(self, name: str) -> pygame.Surface:
        if name in self.cache:
            return self.cache[name]

        img_path = self.base_path / f"{name}.png"
        if not img_path.exists():
            logger.error(f"Gagal menemukan image: {img_path}")
            sys.exit(1)

        image = pygame.image.load(str(img_path)).convert_alpha()
        self.cache[name] = image
        logger.info(f"Loaded image: {img_path}")
<<<<<<< HEAD
        return image
=======
        return image
>>>>>>> 066713d7379e26e752460a32ca73c8cee73c0ca0
