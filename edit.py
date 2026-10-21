import copy
import json
import re
from pathlib import Path

import pygame

from map_loader import MAP_PATH, DEFAULT_WALL_THICKNESS, make_border_walls

ROOT = Path(__file__).resolve().parent
SCALE = 0.7
PANEL_WIDTH = 280
GRIDS = [12, 36, 72]
DOOR_SIZE = 144
TOOLS = ["wall", "door", "hotspot"]

BG = (20, 20, 26)
PANEL_BG = (30, 30, 38)
TEXT = (230, 230, 230)
BORDER_FILL = (0, 0, 0, 120)
WALL_FILL = (255, 0, 255, 90)
WALL_LINE = (255, 0, 255)
DOOR_FILL = (245, 190, 80, 110)
DOOR_LINE = (245, 190, 80)
HOTSPOT_FILL = (0, 220, 255, 90)
HOTSPOT_LINE = (0, 220, 255)
PREVIEW_LINE = (255, 255, 255)
START_COLOR = (200, 60, 60)
GRID_COLOR = (255, 255, 255, 18)


def load_data():
    with open(MAP_PATH, encoding="utf-8") as f:
        data = json.load(f)
    for room in data["rooms"].values():
        room.setdefault("walls", [])
        room.setdefault("doors", [])
        room.setdefault("hotspots", [])
    return data


def save_data(data):
    text = json.dumps(data, indent=2)
    text = re.sub(
        r"\[([^\[\]{}\"]*?)\]",
        lambda m: "[" + ", ".join(x.strip() for x in m.group(1).split(",")) + "]",
        text,
    )
    with open(MAP_PATH, "w", encoding="utf-8") as f:
        f.write(text + "\n")


def hotspot_rect(h):
    if "area" in h:
        return tuple(h["area"])
    return h["x"], h["y"], h["w"], h["h"]


def door_rect(door, width, height, thickness):
    half = door["size"] / 2
    if door["side"] == "left":
        return 0, door["at"] - half, thickness, door["size"]
    if door["side"] == "right":
        return width - thickness, door["at"] - half, thickness, door["size"]
    if door["side"] == "top":
        return door["at"] - half, 0, door["size"], thickness
    return door["at"] - half, height - thickness, door["size"], thickness


def spawn_for(side, at, width, height, thickness):
    if side == "left":
        return [thickness * 2, at]
    if side == "right":
        return [width - thickness * 4, at]
    if side == "top":
        return [at, thickness * 2]
    return [at, height - thickness * 4]


def point_in(px, py, rect):
    x, y, w, h = rect
    return x <= px <= x + w and y <= py <= y + h


def next_room_id(rooms):
    n = 0
    while True:
        rid = chr(ord("a") + n) if n < 26 else "room" + str(n)
        if rid not in rooms:
            return rid
        n += 1


def main():
    data = load_data()
    width, height = data["room_size"]
    thickness = data.get("wall_thickness", DEFAULT_WALL_THICKNESS)
    canvas_w, canvas_h = int(width * SCALE), int(height * SCALE)

    pygame.init()
    screen = pygame.display.set_mode((canvas_w + PANEL_WIDTH, canvas_h))
    pygame.display.set_caption("room editor")
    font = pygame.font.Font(None, 24)
    clock = pygame.time.Clock()
    overlay = pygame.Surface((canvas_w, canvas_h), pygame.SRCALPHA)
    bg_cache = {}

    room_id = data["start"]["room"]
    tool = 0
    grid_index = 1
    door_target = None
    drag_start = None
    undo_stack = []
    dirty = False
    status = "ready"

    def grid():
        return GRIDS[grid_index]

    def snap(v, limit):
        return max(0, min(limit, round(v / grid()) * grid()))

    def mouse_room():
        mx, my = pygame.mouse.get_pos()
        return mx / SCALE, my / SCALE

    def snapped_mouse():
        x, y = mouse_room()
        return snap(x, width), snap(y, height)

    def push_undo():
        undo_stack.append(copy.deepcopy(data))
        if len(undo_stack) > 100:
            undo_stack.pop(0)

    def other_rooms():
        return [r for r in data["rooms"] if r != room_id]

    def current_target():
        others = other_rooms()
        if not others:
            return None
        return door_target if door_target in others else others[0]

    def place_door(x, y):
        target = current_target()
        if target is None:
            return "need a second room first (N)"
        distances = {"top": y, "bottom": height - y, "left": x, "right": width - x}
        side = min(distances, key=distances.get)
        along = x if side in ("top", "bottom") else y
        edge = width if side in ("top", "bottom") else height
        at = max(DOOR_SIZE / 2, min(edge - DOOR_SIZE / 2, snap(along, edge)))
        at = int(at) if at == int(at) else at
        opposite = {"left": "right", "right": "left", "top": "bottom", "bottom": "top"}[side]
        push_undo()
        data["rooms"][room_id]["doors"].append({
            "side": side, "at": at, "size": DOOR_SIZE, "to": target,
            "spawn": spawn_for(opposite, at, width, height, thickness),
        })
        back = data["rooms"][target]["doors"]
        if not any(d["side"] == opposite and d["to"] == room_id for d in back):
            back.append({
                "side": opposite, "at": at, "size": DOOR_SIZE, "to": room_id,
                "spawn": spawn_for(side, at, width, height, thickness),
            })
            return "door added both ways"
        return "door added"

    def delete_at(x, y):
        room = data["rooms"][room_id]
        for i in range(len(room["hotspots"]) - 1, -1, -1):
            if point_in(x, y, hotspot_rect(room["hotspots"][i])):
                push_undo()
                room["hotspots"].pop(i)
                return "hotspot removed"
        for i in range(len(room["walls"]) - 1, -1, -1):
            if point_in(x, y, room["walls"][i]):
                push_undo()
                room["walls"].pop(i)
                return "wall removed"
        for i in range(len(room["doors"]) - 1, -1, -1):
            if point_in(x, y, door_rect(room["doors"][i], width, height, thickness)):
                push_undo()
                room["doors"].pop(i)
                return "door removed"
        return "nothing there"

    def load_bg(path):
        if path not in bg_cache:
            try:
                img = pygame.image.load(str(ROOT / path)).convert()
                img = pygame.transform.smoothscale(img, (canvas_w, canvas_h))
            except (FileNotFoundError, pygame.error):
                img = pygame.Surface((canvas_w, canvas_h))
                img.fill((60, 60, 70))
            bg_cache[path] = img
        return bg_cache[path]

    def scaled(rect):
        return pygame.Rect(
            round(rect[0] * SCALE), round(rect[1] * SCALE),
            max(1, round(rect[2] * SCALE)), max(1, round(rect[3] * SCALE)),
        )

    def draw_rect(rect, fill, line):
        r = scaled(rect)
        pygame.draw.rect(overlay, fill, r)
        pygame.draw.rect(overlay, line, r, 2)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                ctrl = event.mod & pygame.KMOD_CTRL
                if ctrl and event.key == pygame.K_s:
                    save_data(data)
                    dirty = False
                    status = "saved"
                elif ctrl and event.key == pygame.K_z:
                    if undo_stack:
                        data.clear()
                        data.update(undo_stack.pop())
                        if room_id not in data["rooms"]:
                            room_id = data["start"]["room"]
                        dirty = True
                        status = "undone"
                elif event.key == pygame.K_1:
                    tool = 0
                elif event.key == pygame.K_2:
                    tool = 1
                elif event.key == pygame.K_3:
                    tool = 2
                elif event.key == pygame.K_g:
                    grid_index = (grid_index + 1) % len(GRIDS)
                elif event.key == pygame.K_TAB:
                    ids = list(data["rooms"])
                    room_id = ids[(ids.index(room_id) + 1) % len(ids)]
                    door_target = None
                elif event.key == pygame.K_t:
                    others = other_rooms()
                    if others:
                        cur = current_target()
                        door_target = others[(others.index(cur) + 1) % len(others)]
                elif event.key == pygame.K_i:
                    push_undo()
                    room = data["rooms"][room_id]
                    room["irradiated"] = not room.get("irradiated", False)
                    dirty = True
                elif event.key == pygame.K_p:
                    x, y = snapped_mouse()
                    push_undo()
                    data["start"] = {"room": room_id, "position": [x, y]}
                    dirty = True
                    status = "start set"
                elif event.key == pygame.K_n:
                    push_undo()
                    rid = next_room_id(data["rooms"])
                    data["rooms"][rid] = {
                        "background": f"assets/images/room_{rid}_1080p.png",
                        "walls": [], "doors": [], "hotspots": [],
                    }
                    room_id = rid
                    door_target = None
                    dirty = True
                    status = "room " + rid + " created"
            elif event.type == pygame.MOUSEBUTTONDOWN and event.pos[0] < canvas_w:
                if event.button == 1:
                    if TOOLS[tool] == "door":
                        x, y = mouse_room()
                        status = place_door(x, y)
                        dirty = True
                    else:
                        drag_start = snapped_mouse()
                elif event.button == 3:
                    x, y = mouse_room()
                    status = delete_at(x, y)
                    dirty = True
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and drag_start:
                x, y = snapped_mouse()
                x0, y0 = min(drag_start[0], x), min(drag_start[1], y)
                w, h = abs(x - drag_start[0]), abs(y - drag_start[1])
                if w > 0 and h > 0:
                    push_undo()
                    room = data["rooms"][room_id]
                    if TOOLS[tool] == "wall":
                        room["walls"].append([x0, y0, w, h])
                    else:
                        room["hotspots"].append({
                            "type": "interact",
                            "id": "item" + str(len(room["hotspots"]) + 1),
                            "area": [x0, y0, w, h],
                        })
                    dirty = True
                drag_start = None

        room = data["rooms"][room_id]
        screen.fill(BG)
        screen.blit(load_bg(room["background"]), (0, 0))
        overlay.fill((0, 0, 0, 0))

        g = grid()
        for gx in range(0, width + 1, g):
            pygame.draw.line(overlay, GRID_COLOR, (gx * SCALE, 0), (gx * SCALE, canvas_h))
        for gy in range(0, height + 1, g):
            pygame.draw.line(overlay, GRID_COLOR, (0, gy * SCALE), (canvas_w, gy * SCALE))

        try:
            for wall in make_border_walls(width, height, thickness, room["doors"]):
                pygame.draw.rect(overlay, BORDER_FILL, scaled(wall))
        except ValueError:
            status = "a door doesn't fit its wall"
        for wall in room["walls"]:
            draw_rect(wall, WALL_FILL, WALL_LINE)
        for door in room["doors"]:
            draw_rect(door_rect(door, width, height, thickness), DOOR_FILL, DOOR_LINE)
        for hs in room["hotspots"]:
            draw_rect(hotspot_rect(hs), HOTSPOT_FILL, HOTSPOT_LINE)

        if drag_start:
            x, y = snapped_mouse()
            preview = scaled((min(drag_start[0], x), min(drag_start[1], y),
                              abs(x - drag_start[0]), abs(y - drag_start[1])))
            pygame.draw.rect(overlay, PREVIEW_LINE, preview, 2)

        if data["start"]["room"] == room_id:
            sx, sy = data["start"]["position"]
            pygame.draw.circle(overlay, START_COLOR, (int(sx * SCALE), int(sy * SCALE)), 8)

        screen.blit(overlay, (0, 0))

        pygame.draw.rect(screen, PANEL_BG, (canvas_w, 0, PANEL_WIDTH, canvas_h))
        mx, my = snapped_mouse()
        lines = [
            f"room: {room_id}{' *' if dirty else ''}",
            f"tool: {TOOLS[tool]}",
            f"grid: {g}",
            f"door to: {current_target()}",
            f"irradiated: {room.get('irradiated', False)}",
            f"cursor: {mx}, {my}",
            "",
            "1 wall  2 door  3 hotspot",
            "drag = draw, click = door",
            "right click = delete",
            "G grid   T door target",
            "Tab next room   N new room",
            "I irradiated   P set start",
            "Ctrl+Z undo   Ctrl+S save",
            "",
            status,
        ]
        for i, line in enumerate(lines):
            screen.blit(font.render(line, True, TEXT), (canvas_w + 16, 16 + i * 26))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()