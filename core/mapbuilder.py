import json
from pathlib import Path

# game imports here
from core.geometry import Rect
from core.room import Room, Hotspot

# Find the map file relative to this Python file
MAP_PATH = Path(__file__).resolve().parent.parent / "assets" / "maps" / "level1.json"
def load_world_data(path):
    with open(path, "r") as file:
        data = json.load(file)
    rooms = {} # make a dict for all rooms
    # go through every room in the map
    for room_id, room_data in data["rooms"].items():
        #make walls
        walls = []
        for wall in room_data["walls"]:
            wall_rect = Rect( wall["x"],wall["y"],wall["w"],wall["h"])
            walls.append(wall_rect)
        # make hotspots
        hotspots = []
        for hotspot in room_data.get("hotspots", []): # this is important because some rooms might not have any so we dont want it to crash
            # data for things
            extra_data = {}
            for key, value in hotspot.items():
                if key not in ["x", "y", "w", "h", "type"]:
                    extra_data[key] = value
            NewHotspotCHUNKLOADER = Hotspot(hotspot["x"],hotspot["y"],hotspot["w"],hotspot["h"],hotspot["type"],extra_data)
            hotspots.append(NewHotspotCHUNKLOADER)
        # assemble rooms with things in them
        rooms[room_id] = Room(room_data["background"], walls,hotspots)
        # eg rooms[1]=Room(blah blah blah)

    # now chunk all data togeher and build map
    start_room = data["start_room"]
    start_x = data["start_x"]
    start_y = data["start_y"]
    return rooms, start_room, start_x, start_y
