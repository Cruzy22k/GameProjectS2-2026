import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MAP_PATH = ROOT / "assets" / "maps" / "level1.json"
WALL_THICKNESS = 20


def edge_rectangle(side, start, end, room_width, room_height, thickness):
    # turns part of a room edge into a wall rectangle
    if side == "top":
        return start, 0, end - start, thickness  # eg (20, 0, 200, 20)
    elif side == "bottom":
        return start, room_height - thickness, end - start, thickness  # eg (20, 580, 200, 20)
    elif side == "left":
        return 0, start, thickness, end - start  # eg (0, 20, 20, 200)
    return room_width - thickness, start, thickness, end - start  # eg (780, 20, 20, 200)


def make_border_walls(room_width, room_height, thickness, doors):
    # makes the room border walls and leaves gaps where the doors go
    walls = []
    # make sure each doorway fits before cutting a gap into a wall
    for door in doors:
        if door["side"] not in ("top", "bottom", "left", "right"):
            raise ValueError("Unknown door side: " + door["side"])

        if door["side"] == "top" or door["side"] == "bottom":
            edge_length = room_width
        else:
            edge_length = room_height

        # at is the middle of the doorway so half the size goes on each side
        opening_start = door["at"] - door["size"] / 2
        opening_end = door["at"] + door["size"] / 2
        if door["size"] <= 0 or opening_start < 0 or opening_end > edge_length:
            raise ValueError("A door opening does not fit on its wall")

    for side in ("top", "bottom", "left", "right"):
        if side == "top" or side == "bottom":
            edge_length = room_width
        else:
            edge_length = room_height

        openings = []
        for door in doors:
            if door["side"] == side:
                opening_start = door["at"] - door["size"] / 2
                opening_end = door["at"] + door["size"] / 2
                openings.append((opening_start, opening_end))
        # sorting the gaps lets us make each wall piece in order
        openings.sort()

        wall_start = 0
        for opening_start, opening_end in openings:
            if opening_start > wall_start:
                wall = edge_rectangle(
                    side, wall_start, opening_start,
                    room_width, room_height, thickness
                )
                walls.append(wall)
            if opening_end > wall_start:
                wall_start = opening_end

        if wall_start < edge_length:
            wall = edge_rectangle(
                side, wall_start, edge_length,
                room_width, room_height, thickness
            )
            walls.append(wall)
    return walls  # eg a list of wall rectangles like [(0, 0, 800, 20)]


def load_map(path=MAP_PATH):
    # reads the map json and turns it into rooms the game can use
    with open(path, encoding="utf-8") as map_file:
        data = json.load(map_file)

    room_width, room_height = data["room_size"]
    wall_thickness = data.get("wall_thickness", WALL_THICKNESS)
    rooms = {}

    for room_id, room_data in data["rooms"].items():
        doors = room_data.get("doors", [])
        walls = make_border_walls(
            room_width, room_height, wall_thickness, doors
        )
        for wall in room_data.get("walls", []):
            walls.append(tuple(wall))

        hotspots = []
        for door in doors:
            # make the doorway click/collision area match which wall its on
            if door["side"] == "left":
                door_x = 0
                door_y = door["at"] - door["size"] / 2
                door_width = wall_thickness
                door_height = door["size"]
            elif door["side"] == "right":
                door_x = room_width - wall_thickness
                door_y = door["at"] - door["size"] / 2
                door_width = wall_thickness
                door_height = door["size"]
            elif door["side"] == "top":
                door_x = door["at"] - door["size"] / 2
                door_y = 0
                door_width = door["size"]
                door_height = wall_thickness
            else:
                door_x = door["at"] - door["size"] / 2
                door_y = room_height - wall_thickness
                door_width = door["size"]
                door_height = wall_thickness

            hotspots.append({
                "rectangle": (door_x, door_y, door_width, door_height),
                "type": "door",
                "data": {
                    "target_room": door["to"],
                    "target_x": door["spawn"][0],
                    "target_y": door["spawn"][1],
                },
            })

        for hotspot in room_data.get("hotspots", []):
            if "area" in hotspot:
                rectangle = tuple(hotspot["area"])
                extra_data = {}
                for key, value in hotspot.items():
                    if key != "area" and key != "type":
                        extra_data[key] = value
            else:
                rectangle = (
                    hotspot["x"], hotspot["y"], hotspot["w"], hotspot["h"]
                )
                extra_data = {}
                for key, value in hotspot.items():
                    if key not in ("x", "y", "w", "h", "type"):
                        extra_data[key] = value

            hotspots.append({
                "rectangle": rectangle,
                "type": hotspot["type"],
                "data": extra_data,
            })

        rooms[room_id] = {
            "background": room_data["background"],
            "walls": walls,
            "hotspots": hotspots,
        }

    start = data["start"]
    return rooms, start["room"], tuple(start["position"])  # eg (rooms, "a", (400, 300))
