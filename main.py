from pathlib import Path

import pygame

from game import (
    RADIATION_MAX, enter_door, interact_at, make_player, move_player,
    update_radiation,
)
from map_loader import load_map

# Window and timing settings
ROOT = Path(__file__).resolve().parent
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080
WINDOW_TITLE = "til I die!"
FPS = 60
MAX_FRAME_TIME = 0.05

#controls
MOVE_RIGHT_KEY = pygame.K_d
MOVE_LEFT_KEY = pygame.K_a
MOVE_DOWN_KEY = pygame.K_s
MOVE_UP_KEY = pygame.K_w
SNEAKYDEV_TOGGLE =pygame.K_EQUALS

#color
BACKGROUND_COLOR = (10, 10, 15)
FALLBACK_ROOM_COLOR = (60, 60, 70)
PLAYER_COLOR = (200, 60, 60)
DOOR_FILL_COLOR = (25, 22, 18)
DOOR_COLOR = (245, 190, 80)
DOOR_OUTLINE_WIDTH = 4
HUD_FONT_SIZE = 48
HUD_FONT_NAME = None
RADIATION_HUD_LABEL = "Radiation"
HUD_TEXT_COLOR = (240, 240, 240)
HUD_POSITION = (24, 24)

#starting 
INITIAL_RADIATION_EXPOSURE = 0


def input_direction():
    # checks wasd and gives back the direction the player should move
    keys = pygame.key.get_pressed()
    direction_x = int(keys[MOVE_RIGHT_KEY] - keys[MOVE_LEFT_KEY])
    direction_y = int(keys[MOVE_DOWN_KEY] - keys[MOVE_UP_KEY])
    return direction_x, direction_y  # eg (1, 0) means move right


def draw_room(screen, room, player, background_cache):
    # draws the room background and player on the screen
    background_path = ROOT / room["background"]
    cache_key = str(background_path)
    if cache_key not in background_cache:
        try:
            background = pygame.image.load(cache_key).convert()
        except FileNotFoundError:
            #use a plain background when the room art hasnt been made yet
            background = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            background.fill(FALLBACK_ROOM_COLOR)
        background_cache[cache_key] = background

    screen.blit(background_cache[cache_key], (0, 0))
    for hotspot in room["hotspots"]:
        if hotspot["type"] == "door":
            door_rectangle = pygame.Rect(hotspot["rectangle"])
            pygame.draw.rect(screen, DOOR_FILL_COLOR, door_rectangle)
            pygame.draw.rect(screen, DOOR_COLOR, door_rectangle, DOOR_OUTLINE_WIDTH)
    
    player_box = (player["x"], player["y"], player["width"], player["height"])
    pygame.draw.rect(screen, PLAYER_COLOR, player_box)
    # draws on the screen and doesnt return a value






def main():
    # starts pygame and runs the game until the window is closed
    rooms, room_id, start_position = load_map()
    player = make_player(start_position)
    radiation_exposure = INITIAL_RADIATION_EXPOSURE
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)
    clock = pygame.time.Clock()
    hud_font = pygame.font.Font(HUD_FONT_NAME, HUD_FONT_SIZE)
    background_cache = {}
    dev_mode = False
    running = True
    try:
        while running:
            delta_time = min(clock.tick(FPS) / 1000, MAX_FRAME_TIME)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    interact_at(rooms[room_id], event.pos[0], event.pos[1])
                # Add this KEYDOWN block to catch F1 presses
                elif event.type == pygame.KEYDOWN:
                    if event.key == SNEAKYDEV_TOGGLE:
                        dev_mode = not dev_mode

            if running:
                direction_x, direction_y = input_direction()
                move_player(player, direction_x, direction_y,delta_time, rooms[room_id])
                room_id = enter_door(rooms, room_id, player)
                radiation_exposure = update_radiation(radiation_exposure,delta_time,in_radiated_zone=rooms[room_id]["irradiated"])
                
                screen.fill(BACKGROUND_COLOR)
                draw_room(screen, rooms[room_id], player, background_cache)
                if dev_mode:
                    #Draw walls as black bars with a bright magenta outline for contrast
                    for wall in rooms[room_id]["walls"]:
                        wall_rect = pygame.Rect(wall)
                        pygame.draw.rect(screen, (0, 0, 0), wall_rect)  # Black fill
                        pygame.draw.rect(screen, (255, 0, 255), wall_rect, 2)  # Outline
                    #cords
                    coord_text = hud_font.render(f"X: {player['x']:.0f}  Y: {player['y']:.0f}",True,(0, 255, 0))
                    screen.blit(coord_text, (WINDOW_WIDTH - 800, HUD_POSITION[1]))
                    fps_text_and_Delta = hud_font.render(f"Fps: {FPS} Delta_time: {delta_time}", True, (100, 230, 0))
                    screen.blit(fps_text_and_Delta, (WINDOW_WIDTH - 550, HUD_POSITION[1]))
                #radiation area here
                radiation_text = hud_font.render(
                    f"{RADIATION_HUD_LABEL}: "
                    f"{radiation_exposure:.0f} / {RADIATION_MAX}",
                    True, 
                    HUD_TEXT_COLOR,
                )
                screen.blit(radiation_text, HUD_POSITION)  # throw it on pygame window
                pygame.display.flip() # only update ts area  not whole screen
    finally:
        # make sure pygame closes cleanly if the loop ends or errors
        pygame.quit()
    


if __name__ == "__main__":
    main()
