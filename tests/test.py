import unittest

from game import enter_door, make_player, move_player
from map_loader import load_map


class GameTests(unittest.TestCase):
    def test_map_loads_with_both_rooms_and_start_position(self):
        rooms, start_room, start_position = load_map()

        self.assertEqual(set(rooms), {"a", "b"})
        self.assertEqual(start_room, "a")
        self.assertEqual(start_position, (400, 300))

    def test_player_cannot_walk_through_room_border(self):
        rooms, _, _ = load_map()
        player = make_player((20, 100))

        move_player(player, -1, 0, 0.016, rooms["a"])

        self.assertEqual(player["x"], 20)

    def test_door_switches_rooms_and_places_player_at_spawn(self):
        rooms, _, _ = load_map()
        player = make_player((760, 280))

        room_id = enter_door(rooms, "a", player)

        self.assertEqual(room_id, "b")
        self.assertEqual((player["x"], player["y"]), (40, 300))


if __name__ == "__main__":
    unittest.main()