from core.world import World
from core.entity import Player
from core.mapbuilder import load_world_data, MAP_PATH

class state:
    def __init__(self):
        self.running = True
        rooms, start_room, start_x, start_y = load_world_data(MAP_PATH)
        self.world = World(rooms, start_room, Player(start_x, start_y))
    def update(self, dt):
        pass  # how to put radiation :(
    def handle_move(self, dx, dy, dt):
        self.world.update_movement(dx, dy, dt)
    def handle_interact(self, px, py):
        return self.world.interact_at(px, py)