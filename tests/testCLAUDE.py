import unittest
import math
# idk what tests are tbh
from game import enter_door, make_player, move_player, update_radiation
from map_loader import load_map


class GameTests(unittest.TestCase):
    def test_map_loads_with_both_rooms_and_start_position(self):
        rooms, start_room, start_position = load_map()
        self.assertEqual(set(rooms), {"a", "b"})
        self.assertEqual(start_room, "a")
        self.assertEqual(start_position, (960, 540))
        self.assertFalse(rooms["a"]["irradiated"])
        self.assertTrue(rooms["b"]["irradiated"])
        right_door = next(
            hotspot for hotspot in rooms["a"]["hotspots"]
            if hotspot["type"] == "door"
        )
        self.assertEqual(right_door["rectangle"], (1884, 468, 36, 144))

    def test_player_cannot_walk_through_room_border(self):
        rooms, _, _ = load_map()
        player = make_player((36, 100))
        move_player(player, -1, 0, 0.016, rooms["a"])
        self.assertEqual(player["x"], 36)

    def test_door_switches_rooms_and_places_player_at_spawn(self):
        rooms, _, _ = load_map()
        player = make_player((1860, 500))
        room_id = enter_door(rooms, "a", player)
        self.assertEqual(room_id, "b")
        self.assertEqual((player["x"], player["y"]), (72, 540))

    def test_diagonal_movement_does_not_add_speed(self):
        player = make_player((500, 500))
        player["speed"] = 100
        move_player(player, 1, 1, 1, {"walls": []})

        distance_x = player["x"] - 500
        distance_y = player["y"] - 500
        self.assertAlmostEqual(math.hypot(distance_x, distance_y), 100)

    def test_player_stops_at_wall_and_slides_along_it(self):
        player = make_player((0, 20))
        player["speed"] = 100
        room = {"walls": [(50, 0, 10, 100)]}
        move_player(player, 1, 1, 1, room)

        self.assertLessEqual(player["x"], 18)
        self.assertGreater(player["x"], 17)
        self.assertGreater(player["y"], 20)

    def test_radiation_increases_over_time_in_exposed_zone(self):
        exposure = update_radiation(0, 2, in_radiated_zone=True)
        self.assertEqual(exposure, 20)
    def test_radiation_stays_unchanged_when_safe_or_protected(self):
        safe_exposure = update_radiation(25, 2, in_radiated_zone=False)
        protected_exposure = update_radiation(
            25, 2, in_radiated_zone=True, protected=True
        )
        self.assertEqual(safe_exposure, 25)
        self.assertEqual(protected_exposure, 25)
    def test_radiation_is_capped_at_maximum(self):
        exposure = update_radiation(95, 2, in_radiated_zone=True)
        self.assertEqual(exposure, 100)


if __name__ == "__main__":
    unittest.main()