class World:
    def __init__(self, rooms, current_room_id, player):
        self.rooms = rooms                      # dict: room id -> Room object
        self.current_room_id = current_room_id  # which key in `rooms` is active
        self.player = player

    @property # give it concrete attribute
    def current_room(self):
        # this doesnt do anything by itsefl its just an alias for world.current_room instead of typing world.room[world.current_room_id]
        return self.rooms[self.current_room_id]

    def update_movement(self, dx, dy, dt):
        self.player.try_move(dx, dy, dt, self.current_room)
        self.INTERNAL_check_door() # try to see. this is shoyld be the only extrnal way to move doors by calling check door thru here

    def INTERNAL_check_door(self):
        # after move if the player's rect now overlaps a door hotspot
        rect = self.player.rect() # create player rect at pos
        for h in self.current_room.hotspots:
            if h.type == "door" and rect.overlaps(h):
                self.current_room_id = h.data["target_room"]
                self.player.x = h.data["target_x"]
                self.player.y = h.data["target_y"]
                return  # find use door 1

    def interact_at(self, px, py):
        # returns id string for interatables like mask or suit or torch
        # or None if nothing was there or it was a door which doesn't need a click
        h = self.current_room.hotspot_at(px, py)
        return h.data.get("id") if h and h.type == "interact" else None