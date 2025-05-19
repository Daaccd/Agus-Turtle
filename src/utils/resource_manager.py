from pathlib import Path
import pygame
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResourceManager:
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.cache = {}

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
        return image