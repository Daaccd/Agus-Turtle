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
        self.sounds_base_path = self.base_path.parent / "sounds"

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
    
    def load_sound(self, name: str) -> pygame.mixer.Sound:
        if name in self.cache:
            return self.cache[name]

        # Ubah path untuk SFX
        sound_path = self.sounds_base_path / f"{name}.wav" # Asumsi semua SFX adalah .wav
        if not sound_path.exists():
            logger.error(f"Gagal menemukan sound effect: {sound_path}")
            return None 

        sound = pygame.mixer.Sound(str(sound_path))
        self.cache[name] = sound
        logger.info(f"Loaded sound effect: {sound_path}")
        return sound

    def load_music(self, name: str):
        # Ubah path untuk BGM
        music_path = self.sounds_base_path / f"{name}.mp3" # Asumsi BGM adalah .mp3
        if not music_path.exists():
            logger.error(f"Gagal menemukan music: {music_path}")
            return False
        
        try:
            pygame.mixer.music.load(str(music_path))
            logger.info(f"Loaded music: {music_path}")
            return True
        except pygame.error as e: # Tangkap error Pygame secara spesifik
            logger.error(f"Error memuat music {music_path}: {e}")
            return False