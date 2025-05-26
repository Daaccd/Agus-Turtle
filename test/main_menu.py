import pygame
import pytest
from unittest.mock import Mock, patch
from src.constants import MENU_ITEMS, COLOR_WHITE, COLOR_HIGHLIGHT, SCREEN_WIDTH
from src.scene.main_menu import MainMenu

pygame.init()
pygame.font.init()

@pytest.fixture
def mock_screen():
    return Mock(spec=pygame.Surface)

@pytest.fixture
def main_menu(mock_screen):
    return MainMenu(mock_screen)

def test_main_menu_initialization(main_menu):
    assert main_menu.screen is not None
    assert main_menu.selected == 0
    assert main_menu.font is not None
    assert len(main_menu.item_rects) == len(MENU_ITEMS)
    for rect in main_menu.item_rects:
        assert isinstance(rect, pygame.Rect)

def test_handle_input_key_up(main_menu):
    main_menu.selected = 1
    event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP)
    result = main_menu.handle_input(event)
    assert main_menu.selected == 0
    assert result is None

def test_handle_input_key_up_wraps_around(main_menu):
    main_menu.selected = 0
    event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP)
    result = main_menu.handle_input(event)
    assert main_menu.selected == len(MENU_ITEMS) - 1
    assert result is None

def test_handle_input_key_down(main_menu):
    main_menu.selected = 0
    event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)
    result = main_menu.handle_input(event)
    assert main_menu.selected == 1
    assert result is None

def test_handle_input_key_down_wraps_around(main_menu):
    main_menu.selected = len(MENU_ITEMS) - 1
    event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)
    result = main_menu.handle_input(event)
    assert main_menu.selected == 0
    assert result is None

def test_handle_input_key_return(main_menu):
    main_menu.selected = 0
    event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
    result = main_menu.handle_input(event)
    assert result == MENU_ITEMS[0]

def test_handle_input_mouse_motion_hover(main_menu):
    target_item_index = 1
    target_rect = main_menu.item_rects[target_item_index]
    event = pygame.event.Event(pygame.MOUSEMOTION, pos=target_rect.center)
    main_menu.handle_input(event)
    assert main_menu.selected == target_item_index

def test_handle_input_mouse_button_down(main_menu):
    target_item_index = 2
    target_rect = main_menu.item_rects[target_item_index]
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=target_rect.center)
    result = main_menu.handle_input(event)
    assert result == MENU_ITEMS[target_item_index]

def test_handle_input_other_event_type(main_menu):
    event = pygame.event.Event(pygame.KEYUP, key=pygame.K_a)
    result = main_menu.handle_input(event)
    assert result is None

def test_update_method_does_nothing(main_menu):
    initial_selected = main_menu.selected
    main_menu.update()
    assert main_menu.selected == initial_selected

def test_draw_method_calls_fill_and_blit(main_menu, mock_screen):
    main_menu.draw()
    mock_screen.fill.assert_called_with((0, 0, 0))
    assert mock_screen.blit.call_count == len(MENU_ITEMS)

def test_draw_method_highlights_selected_item(main_menu, mock_screen):
    main_menu.selected = 0
    main_menu.draw()

    first_blit_call_args = mock_screen.blit.call_args_list[0].args
    rendered_surface = first_blit_call_args[0]
    expected_selected_surf = main_menu.font.render(MENU_ITEMS[0], True, COLOR_HIGHLIGHT)
    assert rendered_surface.get_at((0, 0)) == expected_selected_surf.get_at((0, 0))

    main_menu.selected = 1
    mock_screen.reset_mock()
    main_menu.draw()
    not_selected_surf = main_menu.font.render(MENU_ITEMS[0], True, COLOR_WHITE)
    first_blit_call_args_after = mock_screen.blit.call_args_list[0].args
    rendered_surface_after = first_blit_call_args_after[0]
    assert rendered_surface_after.get_at((0, 0)) == not_selected_surf.get_at((0, 0))