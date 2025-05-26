import pygame
import pytest
from unittest.mock import Mock, patch
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from src.scene.level1 import Level1
from src.characters.player import Player
from src.utils.resource_manager import ResourceManager
import math

pygame.init()

@pytest.fixture
def mock_player_image():
    return pygame.Surface((32, 32))

@pytest.fixture
def player(mock_player_image):
    return Player(pos=(0, 0), image=mock_player_image)

@pytest.fixture
def mock_resource_manager():
    rm = Mock(spec=ResourceManager)
    rm.load_image.return_value = pygame.Surface((1, 1))
    rm.load_image.side_effect = lambda x: pygame.Surface((32, 32)) if x in ["block", "grass", "bridge", "flag", "lever_up", "lever_down"] else pygame.Surface((1, 1))
    return rm

@pytest.fixture
def level1(player, mock_resource_manager):
    return Level1(player, mock_resource_manager)

@pytest.fixture
def small_dt():
    return 0.01

@pytest.fixture
def long_dt():
    return 1.0

def test_level1_initialization(level1):
    assert level1.player is not None
    assert level1.resources is not None
    assert len(level1.obstacles) > 0
    assert level1.ground_rect in level1.obstacles
    assert level1.movable_platform_rect in level1.obstacles
    assert level1.static_platform_rect in level1.obstacles
    assert level1.is_lever_up == True
    assert level1.completed == False

def test_movable_platform_initial_position(level1):
    assert level1.movable_platform_rect.topleft == level1.movable_platform_start_pos.topleft

def test_handle_event_does_nothing(level1):
    event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_x)
    initial_lever_status = level1.is_lever_up
    level1.handle_event(event)
    assert level1.is_lever_up == initial_lever_status

def test_lever_interaction_toggle(level1, player, small_dt):
    player.rect.center = level1.lever_rect.center
    initial_lever_status = level1.is_lever_up

    with patch('pygame.key.get_pressed', return_value={pygame.K_e: True}):
        level1.update(small_dt, player.rect)
        assert level1.is_lever_up != initial_lever_status

def test_lever_interaction_cooldown(level1, player, small_dt):
    player.rect.center = level1.lever_rect.center
    initial_lever_status = level1.is_lever_up

    with patch('pygame.key.get_pressed', return_value={pygame.K_e: True}):
        level1.update(small_dt, player.rect)
        assert level1.is_lever_up != initial_lever_status
        assert level1._can_interact_lever == False

        second_status = level1.is_lever_up
        level1.update(small_dt, player.rect)
        assert level1.is_lever_up == second_status

    level1.update(0.6, player.rect)
    assert level1._can_interact_lever == True

    with patch('pygame.key.get_pressed', return_value={pygame.K_e: True}):
        level1.update(small_dt, player.rect)
        assert level1.is_lever_up != second_status

def test_movable_platform_moves_down_when_lever_up(level1, small_dt):
    level1.is_lever_up = True
    level1._current_platform_y = level1.movable_platform_target_y
    level1.movable_platform_rect.y = int(level1._current_platform_y)

    initial_y = level1.movable_platform_rect.y
    level1.update(small_dt, level1.player.rect)
    assert level1.movable_platform_rect.y > initial_y

def test_movable_platform_moves_up_when_lever_down(level1, small_dt):
    level1.is_lever_up = False
    level1._current_platform_y = level1.movable_platform_start_pos.y
    level1.movable_platform_rect.y = int(level1._current_platform_y)

    initial_y = level1.movable_platform_rect.y
    level1.update(small_dt, level1.player.rect)
    assert level1.movable_platform_rect.y < initial_y

def test_movable_platform_stops_at_target_y(level1, long_dt):
    level1.is_lever_up = False
    level1._current_platform_y = level1.movable_platform_start_pos.y
    level1.movable_platform_rect.y = int(level1._current_platform_y)

    level1.update(long_dt, level1.player.rect)
    assert level1.movable_platform_rect.y == level1.movable_platform_target_y

def test_movable_platform_stops_at_start_pos_y(level1, long_dt):
    level1.is_lever_up = True
    level1._current_platform_y = level1.movable_platform_target_y
    level1.movable_platform_rect.y = int(level1._current_platform_y)

    level1.update(long_dt, level1.player.rect)
    assert level1.movable_platform_rect.y == level1.movable_platform_start_pos.y

def test_player_moves_with_platform(level1, player, small_dt):
    level1.is_lever_up = False
    player.rect.bottom = level1.movable_platform_rect.top
    player.rect.x = level1.movable_platform_rect.x + 10

    initial_player_y = player.rect.y
    initial_platform_y = level1.movable_platform_rect.y

    level1.update(small_dt, player.rect)

    actual_platform_move_y = level1.movable_platform_rect.y - initial_platform_y

    assert player.rect.y == initial_player_y + actual_platform_move_y

def test_level_completion(level1, player, small_dt):
    assert level1.completed == False
    player.rect.center = level1.exit_rect.center
    level1.update(small_dt, player.rect)
    assert level1.completed == True

def test_level_not_completed_when_not_at_exit(level1, player, small_dt):
    player.rect.topleft = (0, 0)
    level1.update(small_dt, player.rect)
    assert level1.completed == False

def test_draw_method_calls_blit(level1):
    mock_screen = Mock(spec=pygame.Surface)
    level1.draw(mock_screen)

    mock_screen.blit.assert_called()

    assert mock_screen.blit.call_args_list[0].args[0] in [level1.lever_up_img, level1.lever_down_img, level1.exit_img, level1.grass_img, level1.block_img, level1.bridge_img]