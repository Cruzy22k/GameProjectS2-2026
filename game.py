# player specific globals

PLAYER_SIZE = 32
PLAYER_SPEED = 800
RADIATION_MAX = 100
RADIATION_PER_SECOND = 10

def update_radiation(exposure, delta_time, in_radiated_zone, protected=False): # protected for mask
    if not in_radiated_zone or protected:
        return exposure
    return min(exposure + RADIATION_PER_SECOND * delta_time, RADIATION_MAX)
    # if over, min will just return 100 instead yay


def rectangles_overlap(first, second):
    # checks if two rectangles are touching each other
    x, y, width, height = first
    other_x, other_y, other_width, other_height = second
    # if one rectangle is fully past another they dont overlap
    if (x + width <= other_x or other_x + other_width <= x
            or y + height <= other_y or other_y + other_height <= y):
        return False  # eg False means the rectangles dont overlap
    return True  # eg True means the rectangles overlap


def point_in_rectangle(point_x, point_y, rectangle):
    # checks if a mouse position is inside a rectangle
    x, y, width, height = rectangle
    if x <= point_x <= x + width and y <= point_y <= y + height:
        return True  # eg True if the mouse is inside the rectangle
    return False  # eg False if the mouse is outside the rectangle


def make_player(position):
    # sets up the player position, size and movement speed
    player = {
        "x": position[0],
        "y": position[1],
        "width": PLAYER_SIZE, # 32 should be same for both ++
        "height": PLAYER_SIZE, 
        "speed": PLAYER_SPEED,
    }
    return player  # eg {"x": 400, "y": 300, "width": 32, "height": 32, "speed": 400}


def player_rectangle(player, x=None, y=None):
    # gives back the players rectangle, with an optional test position
    if x is None:
        x = player["x"]
    if y is None:
        y = player["y"]
    return x, y, player["width"], player["height"]  # eg (12, 12, 32, 32)


def room_collides(room, rectangle):
    # checks if a rectangle hits any wall in this room
    for wall in room["walls"]:
        if rectangles_overlap(rectangle, wall):
            return True  # eg True means this rectangle hit a wall
    return False  # eg False means it didnt hit any walls


def move_player(player, direction_x, direction_y, delta_time, room):
    # moves the player and stops them going through walls
    # delta time keeps movement speed steady even if the frame rate changes
    move_x = direction_x * player["speed"] * delta_time
    move_y = direction_y * player["speed"] * delta_time

    # check each direction on its own so the player can slide along walls
    next_x = player["x"] + move_x
    if not room_collides(room, player_rectangle(player, x=next_x)):
        player["x"] = next_x

    next_y = player["y"] + move_y
    if not room_collides(room, player_rectangle(player, y=next_y)):
        player["y"] = next_y
    # changes the player position and doesnt return anything


def enter_door(rooms, room_id, player):
    # switches rooms if the player walks into a door
    zebulon = player_rectangle(player)
    for hotspot in rooms[room_id]["hotspots"]:
        if hotspot["type"] == "door":
            if rectangles_overlap(zebulon, hotspot["rectangle"]):
                door_data = hotspot["data"]
                player["x"] = door_data["target_x"]
                player["y"] = door_data["target_y"]
                return door_data["target_room"]  # eg "b" if the door leads to room b
    return room_id  # eg "a" if the player stayed in room a


def interact_at(room, point_x, point_y):
    # finds a clickable thing under the mouse and returns its id
    for hotspot in room["hotspots"]:
        if hotspot["type"] == "interact":
            if point_in_rectangle(point_x, point_y, hotspot["rectangle"]):
                return hotspot["data"].get("id")  # eg "mask" if thats what was clicked
    return None  # eg None when the click wasnt on an item
