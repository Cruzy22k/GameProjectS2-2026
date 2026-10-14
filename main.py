import pygame
from core.state import state
from render.window import Window
def input_vector():
    # get_pressed() checks EVERY key's current state. We only care about WASD
    # True/False acts like 1/0 in subtraction, so pressing D and not A gives dx=1,
    # pressing A and not D gives dx=-1, pressing both or neither gives dx=0
    keys = pygame.key.get_pressed()
    dx = keys[pygame.K_d] - keys[pygame.K_a]
    dy = keys[pygame.K_s] - keys[pygame.K_w]
    return dx, dy

def main():
    x = state()
    window = Window()
    while x.running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                x.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                    x.handle_interact(*event.pos)  # event.pos is (x, y) of the click
            dx, dy = input_vector()
            print(dx, dy) # debug
            dt = window.world_tick()
            x.handle_move(dx, dy, dt)
            x.update(dt)
            window.clear()
            window.draw_room(x.world.current_room, x.world.player)
            window.flip()
    window.exit()
if __name__ == "__main__":
    main()
