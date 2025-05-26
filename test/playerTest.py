import pygame
import pytest
from src.constants import GRAVITY, PLAYER_SPEED, JUMP_STRENGTH
from src.characters import player

pygame.init()

@pytest.fixture
def player_image():
     return pygame.Surface((32, 32))

@pytest.fixture
def player(player_image):
     return player(pos=(100, 100), image=player_image)

@pytest.fixture
def obstacle():
     return pygame.Rect(150, 100, 50, 50)

@pytest.fixture
def floor_obstacle():
     return pygame.Rect(0, 200, 800, 50)


def test_player_initialization(player):
     assert player.rect.topleft == (100, 100)
     assert player.vel.x == 0
     assert player.vel.y == 0
     assert player.on_ground == False

def test_handle_input_move_right(player):
     keys = {pygame.K_d: True, pygame.K_a: False, pygame.K_SPACE: False}
     player.handle_input(keys)
     assert player.vel.x == PLAYER_SPEED

def test_handle_input_move_left(player):
     keys = {pygame.K_d: False, pygame.K_a: True, pygame.K_SPACE: False}
     player.handle_input(keys)
     assert player.vel.x == -PLAYER_SPEED

def test_handle_input_no_horizontal_movement(player):
     keys = {pygame.K_d: False, pygame.K_a: False, pygame.K_SPACE: False}
     player.handle_input(keys)
     assert player.vel.x == 0

def test_handle_input_jump(player):
     player.on_ground = True
     keys = {pygame.K_d: False, pygame.K_a: False, pygame.K_SPACE: True}
     player.handle_input(keys)
     assert player.vel.y == JUMP_STRENGTH
     assert player.on_ground == False

def test_handle_input_no_jump_in_air(player):
     player.on_ground = False
     keys = {pygame.K_d: False, pygame.K_a: False, pygame.K_SPACE: True}
     player.handle_input(keys)
     assert player.vel.y == 0

def test_gravity_application(player):
     initial_vel_y = player.vel.y
     dt = 0.1
     player.update(dt, [])
     assert player.vel.y == initial_vel_y + GRAVITY * dt

def test_horizontal_collision_right(player, obstacle):
     player.rect.x = 120
     player.vel.x = PLAYER_SPEED
     dt = 0.1
     player.update(dt, [obstacle])
     assert player.rect.right == obstacle.left

def test_horizontal_collision_left(player, obstacle):
     player.rect.x = 180
     player.vel.x = -PLAYER_SPEED
     dt = 0.1
     player.update(dt, [obstacle])
     assert player.rect.left == obstacle.right

def test_vertical_collision_falling_on_ground(player, floor_obstacle):
     player.rect.y = 170
     player.vel.y = 50
     dt = 0.1
     player.update(dt, [floor_obstacle])
     assert player.rect.bottom == floor_obstacle.top
     assert player.vel.y == 0
     assert player.on_ground == True

def test_vertical_collision_hitting_head(player, obstacle):
     player.rect.y = 120
     player.vel.y = -50
     dt = 0.1
     player.update(dt, [obstacle])
     assert player.rect.top == obstacle.bottom
     assert player.vel.y == 0

def test_no_collision_when_far_apart(player, obstacle):
     initial_rect = player.rect.copy()
     player.vel.x = PLAYER_SPEED
     player.vel.y = GRAVITY
     dt = 0.1
     player.update(dt, [pygame.Rect(500, 500, 50, 50)])
     assert player.rect.x != initial_rect.x
     assert player.rect.y != initial_rect.y
     assert player.on_ground == False

def test_on_ground_resets_if_not_colliding(player, floor_obstacle):
     player.rect.y = 170
     player.vel.y = 50
     dt = 0.1
     player.update(dt, [floor_obstacle])
     assert player.on_ground == True

     player.rect.y -= 10 
     player.update(dt, [floor_obstacle])
     assert player.on_ground == False