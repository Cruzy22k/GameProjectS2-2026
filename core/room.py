from core.geometry import Rect
# rooms dont know they are rooms
class Hotspot(Rect):
    # A hotspot is a rect with extra meaning attached"this area is a door" or
    # "this area is a mask you can ghet". `data` carries whatever that type needs
    # (a door needs target_room/target_x/target_y, an interactable just needs an identifying thing
    def __init__(self, x, y, w, h, type_, data):
        super().__init__(x, y, w, h)
        self.type = type_
        self.data = data

class Room:
    def __init__(self, background, walls, hotspots):
        self.background = background  # file/path to room bg image
        self.walls = walls            # list of Rects you can't walk through
        self.hotspots = hotspots      # list of Hotspots (doors, clickables)

    def collides(self, rect):
        # True if the given rect (usually the player's next position) hits ANY wall.
        # `any(...)` short-circuits — stops checking as soon as one wall matches.
        # return any(rect.overlaps(w) for w in self.walls)
        return any(rect.overlaps(w) for w in self.walls)
        
    def hotspot_at(self, px, py):
        # eg when the mouse is clicked which hotspot (if any) is under the cursor?
        for h in self.hotspots:
            if h.contains_point(px, py):
                return h
        return None # mouse is over some bs