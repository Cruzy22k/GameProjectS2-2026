import pygame # keep pyhame in here only


#globals here
WINDOW_TITLE="til I die!"
FPS = 60 #maybe I uncap but how do I get ticker working??>?
WINDOW_DIMENSIONS_HEIGHT=600
WINDOW_DIMENSIONS_WIDTH=800
BACKGROUND_FILL = (10, 10, 15)
FALLBACK_ROOM_FILL = (60, 60, 70)  # def grey
PLAYER_COLOR = (200, 60, 60)

class Window:
    def __init__(self, width=WINDOW_DIMENSIONS_WIDTH, height=WINDOW_DIMENSIONS_HEIGHT, title=WINDOW_TITLE):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(title)
        self.clock = pygame.time.Clock()
        self._bg_cache = {} # cache bg

    def world_tick(self, fps=FPS):
        return self.clock.tick(fps)/1000 # weird pygame ticker division so we can pause loop and return how many ms passed, then div by 1000 to get seconds

    def clear(self):
        self.screen.fill(BACKGROUND_FILL)

    def flip(self):
        pygame.display.flip()
    def poll_quit(self):
        for x in pygame.event.get():
            if x.type == pygame.QUIT:
                return True
        return False
    def _background(self, path):
            # only load bg's once try/except 4 if the art
            # doesn't exist yet show a plain grey rectangle instead of crashing
            if path not in self._bg_cache:
                try:
                    self._bg_cache[path] = pygame.image.load(path).convert()
                except FileNotFoundError:
                    surf = pygame.Surface((WINDOW_DIMENSIONS_WIDTH, WINDOW_DIMENSIONS_HEIGHT))
                    surf.fill(FALLBACK_ROOM_FILL)
                    self._bg_cache[path] = surf
            return self._bg_cache[path]
    def exit(self):
        pygame.quit()

    def draw_room(self, room, player):
        self.screen.blit(self._background(room.background), (0, 0))  # blitting is drawing at a specific location. (niche knowledge)
        pygame.draw.rect(self.screen, PLAYER_COLOR, (player.x, player.y, player.w, player.h)) # render rects and player



    

