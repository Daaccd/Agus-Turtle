import pygame
import math
from src.constants import COLOR_BROWN, SCREEN_WIDTH, SCREEN_HEIGHT
from src.utils.resource_manager import ResourceManager


class Level1:
    def __init__(self, player, resources, sfx_lever=None):
        self.player = player
        self.resources = resources
        self.sfx_lever = sfx_lever
        self.obstacles = []

        self.ground_rect = pygame.Rect(0, 550, SCREEN_WIDTH, 50)
        self.obstacles.append(self.ground_rect)

        movable_platform_width = 200
        movable_platform_height = 20
        self.movable_platform_start_pos = pygame.Vector2(300, 530)
        self.movable_platform_target_y = 340
        self.movable_platform_speed = 100

        self.movable_platform_rect = pygame.Rect(
             self.movable_platform_start_pos.x,
             self.movable_platform_start_pos.y,
             movable_platform_width,
             movable_platform_height
        )
        self.obstacles.append(self.movable_platform_rect)

        static_platform_width = 280
        static_platform_height = 200
        static_platform_x = 525
        static_platform_y = 350
        self.static_platform_rect = pygame.Rect(static_platform_x, static_platform_y, static_platform_width, static_platform_height)
        self.obstacles.append(self.static_platform_rect)

        self.block_img = self.resources.load_image("block") 
        self.grass_img = self.resources.load_image("grass")
        self.bridge_img = self.resources.load_image("bridge")
        self.exit_img = self.resources.load_image("flag")
        self.lever_up_img = self.resources.load_image("lever_up")
        self.lever_down_img = self.resources.load_image("lever_down")

        self.orig_block_w = self.block_img.get_width()
        self.orig_grass_w = self.grass_img.get_width() 
        self.orig_bridge_w = self.bridge_img.get_width()

        self.cloud1_img = self.resources.load_image("cloud1")
        self.cloud2_img = self.resources.load_image("cloud2")
        self.bush_img = self.resources.load_image("bush")
        self.plant_img = self.resources.load_image("plant")
        self.cactus_img = self.resources.load_image("cactus")
        self.rock_img = self.resources.load_image("rock")

        self._block_cache = {} 
        self._grass_cache = {} 
        self._bridge_cache = {}

        exit_width = self.exit_img.get_width()
        exit_height = self.exit_img.get_height()
        exit_x = 800 - exit_width 
        exit_y = 350 - exit_height
        self.exit_rect = pygame.Rect(exit_x, exit_y, exit_width, exit_height)

        lever_width = self.lever_up_img.get_width()
        lever_height = self.lever_up_img.get_height()
        lever_x = 100
        lever_y = 480
        self.lever_rect = pygame.Rect(lever_x, lever_y, lever_width, lever_height)
        self.is_lever_up = True
        self._can_interact_lever = True
        self._lever_cooldown_timer = 0
        self.completed = False
        self._current_platform_y = self.movable_platform_start_pos.y

    def handle_event(self, event: pygame.event.Event):
        pass

    def update(self, dt, player_rect):
        interaction_area = self.lever_rect.inflate(10, 10)
        if player_rect.colliderect(interaction_area):
            keys = pygame.key.get_pressed()
            if keys[pygame.K_e] and self._can_interact_lever:
                 self.is_lever_up = not self.is_lever_up
                 if self.sfx_lever:
                     self.sfx_lever.play()

                 self._can_interact_lever = False
                 self._lever_cooldown_timer = 0.5

        if not self._can_interact_lever:
             self._lever_cooldown_timer -= dt
             if self._lever_cooldown_timer <= 0:
                  self._can_interact_lever = True

        target_y = self.movable_platform_start_pos.y if self.is_lever_up else self.movable_platform_target_y
        distance_to_target = target_y - self._current_platform_y
        move_amount = self.movable_platform_speed * dt
        old_movable_platform_y = self.movable_platform_rect.y

        if distance_to_target > 0:
             self._current_platform_y += min(move_amount, distance_to_target)
        elif distance_to_target < 0:
             self._current_platform_y += max(-move_amount, distance_to_target)

        self.movable_platform_rect.y = int(self._current_platform_y)
        actual_platform_move_y = self.movable_platform_rect.y - old_movable_platform_y

        if player_rect.colliderect(self.movable_platform_rect):
             if player_rect.bottom <= self.movable_platform_rect.top + abs(actual_platform_move_y) + 5:
                  player_rect.y += actual_platform_move_y

        if player_rect.colliderect(self.exit_rect):
            self.completed = True
            
    def draw(self, screen: pygame.Surface):
        for rect in self.obstacles:
            h = rect.height

            if rect is self.ground_rect:
                img_to_use = self.grass_img
                orig_w = self.orig_grass_w
                cache_to_use = self._grass_cache
            elif rect is self.movable_platform_rect:
                 continue
            else:
                img_to_use = self.block_img
                orig_w = self.orig_block_w
                cache_to_use = self._block_cache

            if h not in cache_to_use:
                scaled = pygame.transform.scale(img_to_use, (orig_w, h))
                cache_to_use[h] = scaled

            tile_surf = cache_to_use[h]
            count = math.ceil(rect.width / orig_w)

            for i in range(count):
                x = rect.x + i * orig_w
                screen.blit(tile_surf, (x, rect.y))

        rect = self.movable_platform_rect
        h = rect.height
        img_to_use = self.bridge_img
        orig_w = self.orig_bridge_w
        cache_to_use = self._bridge_cache

        if h not in cache_to_use:
            scaled = pygame.transform.scale(img_to_use, (orig_w, h))
            cache_to_use[h] = scaled

        tile_surf = cache_to_use[h]
        count = math.ceil(rect.width / orig_w)

        for i in range(count):
            x = rect.x + i * orig_w
            screen.blit(tile_surf, (x, rect.y))
            
        screen.blit(self.exit_img, self.exit_rect.topleft)

        if self.is_lever_up:
            screen.blit(self.lever_up_img, self.lever_rect.topleft)
        else:
            screen.blit(self.lever_down_img, self.lever_rect.topleft)
        interaction_area = self.lever_rect.inflate(10, 10)
        if self.player.rect.colliderect(interaction_area):
             font = pygame.font.SysFont(None, 24)
             text_surf = font.render("Press E", True, (255, 255, 255))
             text_rect = text_surf.get_rect(center=(self.lever_rect.centerx, self.lever_rect.top - 20))
             screen.blit(text_surf, text_rect)
        
        screen.blit(self.cloud1_img, (50, 40))
        screen.blit(self.cloud1_img, (220, 80))
        screen.blit(self.cloud1_img, (460, 100))
        screen.blit(self.cloud1_img, (620, 60))
        screen.blit(self.cactus_img, (0, 480))
        screen.blit(self.plant_img, (40, 480))
        screen.blit(self.bush_img, (180, 480))
        screen.blit(self.rock_img, (600, 280))