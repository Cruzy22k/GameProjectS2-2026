PLAYER_WIDTH = 32
PLAYER_HEIGHT = 32
PLAYER_SPEED = 200  # pixels per second adjustable by game mechanices later but not now
from core.geometry import Rect

class Player:
    def __init__(self, x, y, w=PLAYER_WIDTH, h=PLAYER_HEIGHT, speed=PLAYER_SPEED):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.speed = speed

    def rect(self):
        # e players position into a rect so collision code can use it
        return Rect(self.x, self.y, self.w, self.h)

    def try_move(self, dx, dy, dt, room):
        # dx/dy come in as -1, 0, or 1 (direction only). Multiplying by speed and dt delt time is comparitivley
        # converts that into "how many pixels to move THIS frame"
        move_x = dx * self.speed * dt # meaning we take x direction multiplied by speed player is going, and multiply by delta time from window.py 
        move_y = dy * self.speed * dt

        # slide logic, check x and y serperatly
        if not room.collides(Rect(self.x + move_x, self.y, self.w, self.h)):
            self.x += move_x
        if not room.collides(Rect(self.x, self.y + move_y, self.w, self.h)):
            self.y += move_y