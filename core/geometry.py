# we will treat everything as rectangles for collision detection.
class Rect:
    def __init__(self, x, y, width, height):
        # x, y = top left corner
        self.x, self.y, self.width, self.height = x, y, width, height

    def overlaps(self, other):
        # Two rects DON'T overlap if one is entirely to the left/right/above/below the other.
        # So we check all four sides and their cases flip to not
        return (not (self.x + self.width <= other.x or other.x + other.width <= self.x or self.y + self.height <= other.y or other.y + other.height <= self.y))

    def contains_point(self, point_x, point_y):
        # xy inside the rectangle's bounds? for interac
        return self.x <= point_x <= self.x + self.width and self.y <= point_y <= self.y + self.height