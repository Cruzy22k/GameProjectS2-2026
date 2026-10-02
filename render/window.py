import pygame


#globals here
FPS = 60 #maybe I uncap but how do I get ticker working??>?
WINDOW_DIMENSIONS_HEIGHT=600
WINDOW_DIMENSIONS_WIDTH=800

class Window:
    def __init__(self, width=WINDOW_DIMENSIONS_WIDTH, height=WINDOW_DIMENSIONS_HEIGHT, title="til I die!"):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(title)
        self.clock = pygame.time.Clock()

    def world_tick(self, fps=FPS):
        return self.clock.tick(fps)/1000 # weird pygame ticker division

    def clear(self):
        self.screen.fill((10,10,15))



    def exit(self):
        pygame.quit()
