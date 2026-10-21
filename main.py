from pathlib import Path

import pygame

from game import enter_door, interact_at, make_player, move_player
from map_loader import load_map

ROOT = Path(__file__).resolve().parent
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WINDOW_TITLE = "til I die!"
FPS = 60
BACKGROUND_COLOR = (10, 10, 15)
FALLBACK_ROOM_COLOR = (60, 60, 70)
PLAYER_COLOR = (200, 60, 60)


def input_direction():
    # checks wasd and gives back the direction the player should move
    keys = pygame.key.get_pressed()
    direction_x = keys[pygame.K_d] - keys[pygame.K_a]
    direction_y = keys[pygame.K_s] - keys[pygame.K_w]
    return direction_x, direction_y  # eg (1, 0) means move right


def draw_room(screen, room, player, background_cache):
    # draws the room background and player on the screen
    background_path = ROOT / room["background"]
    cache_key = str(background_path)
    if cache_key not in background_cache:
        try:
            background = pygame.image.load(cache_key).convert()
        except FileNotFoundError:
            # use a plain background when the room art hasnt been made yet
            background = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            background.fill(FALLBACK_ROOM_COLOR)
        background_cache[cache_key] = background

    screen.blit(background_cache[cache_key], (0, 0))
    player_box = (
        player["x"], player["y"], player["width"], player["height"]
    )
    pygame.draw.rect(screen, PLAYER_COLOR, player_box)
    # draws on the screen and doesnt return a value


def main():
    # starts pygame and runs the game until the window is closed
    rooms, room_id, start_position = load_map()
    player = make_player(start_position)

    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)
    clock = pygame.time.Clock()
    background_cache = {}
    running = True

    try:
        while running:
            delta_time = clock.tick(FPS) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    interact_at(rooms[room_id], event.pos[0], event.pos[1])

            if running:
                direction_x, direction_y = input_direction()
                move_player(
                    player, direction_x, direction_y,
                    delta_time, rooms[room_id]
                )
                room_id = enter_door(rooms, room_id, player)

                screen.fill(BACKGROUND_COLOR)
                draw_room(screen, rooms[room_id], player, background_cache)
                pygame.display.flip()
    finally:
        # make sure pygame closes cleanly if the loop ends or errors
        pygame.quit()
    # runs the game and doesnt return a value


if __name__ == "__main__":
    main()
