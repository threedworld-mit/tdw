import random
from tdw.tdw_utils import TDWUtils
from tdw.controller import Controller
from time import sleep


"""
- Procedurally generate rooms with different layouts.
- Create a ceiling and delete a portion of it.
- Set the floor and wall materials.
"""


def create_office(width, length, corridor_width, min_room_length, max_room_length):
    """
    Generate a simple office.

    :param width: Width of the room.
    :param length: Length of the room.
    :param corridor_width: Width of the central corridor.
    :param min_room_length: Minimum length of a room.
    :param max_room_length: Maximum length of a room.
    :return The commands to create the office.
    """

    # Create the exterior walls.
    exterior_walls = TDWUtils.get_box(width, length)

    interior_walls = []

    doorway_length = 2
    width = max([w["x"] for w in exterior_walls])
    length = max([w["y"] for w in exterior_walls])

    # Go north.
    corridor_x = int(width / 2) - int(corridor_width / 2)
    next_start_doorway = random.randint(min_room_length, max_room_length)
    next_end_doorway = next_start_doorway + doorway_length
    for y in range(length):
        if not (next_end_doorway >= y > next_start_doorway):
            interior_walls.append({"x": corridor_x, "y": y})
        # Build a perpendicular wall at the doorway.
        if y == next_end_doorway + 1:
            for x in range(0, corridor_x):
                interior_walls.append({"x": x, "y": y})
            next_start_doorway = y + random.randint(min_room_length, max_room_length)
            next_end_doorway = next_start_doorway + doorway_length

    # Go south.
    corridor_x = int(width / 2) + int(corridor_width / 2)
    next_start_doorway = random.randint(min_room_length, max_room_length)
    next_end_doorway = next_start_doorway + doorway_length
    for y in range(length):
        if not (next_end_doorway >= y > next_start_doorway):
            interior_walls.append({"x": corridor_x, "y": y})
        # Build a perpendicular wall at the doorway.
        if y == next_end_doorway + 1:
            for x in range(corridor_x, width):
                interior_walls.append({"x": x, "y": y})
            next_start_doorway = y + random.randint(min_room_length, max_room_length)
            next_end_doorway = next_start_doorway + doorway_length

    # Remove bad interior walls.
    interior_walls = [i for i in interior_walls if
                      i["y"] < length - doorway_length or i["x"] == 0 or i["x"] == width]
    walls = []
    walls.extend(exterior_walls)
    walls.extend(interior_walls)

    return [{"$type": "create_exterior_walls", "walls": exterior_walls},
            {"$type": "create_interior_walls", "walls": interior_walls}]


def create_plus(dimension):
    """
    Create a + shaped room.

    :param dimension: The width of each "spoke" of the + shape.
    :return: The commands to create the room.
    """

    x = 0
    y = 0
    first_time_only = True

    dx = 1
    dy = 0

    prev_dx = 1
    prev_dy = 1

    its_x = 0
    its_y = 0

    max_its_x = 2
    max_its_y = 3

    walls = [{"x": x, "y": y}]
    while first_time_only or (x != 0 or y != 0):
        first_time_only = False

        # Next wall.
        for i in range(dimension):
            x += dx
            y += dy
            walls.append({"x": x, "y": y})
        # Change direction.
        if abs(dx) == 1:
            dx = 0

            its_x += 1
            if its_x == max_its_x:
                its_x = 0
                prev_dx *= -1
                if max_its_x == 2:
                    max_its_x = 3
                else:
                    max_its_x = 2

            dy = prev_dy
        elif abs(dy) == 1:
            dy = 0

            its_y += 1
            if its_y == max_its_y:
                its_y = 0
                prev_dy *= -1

            dx = prev_dx
    # Remove the extra (0, 0) wall.
    walls = walls[:-1]

    # Handle the position offset.
    temp = []
    for wall in walls:
        temp.append({"x": wall["x"] + dimension, "y": wall["y"]})
    walls = temp
    return [{"$type": "create_exterior_walls", "walls": walls}]


class ProcGenRoom(Controller):
    @staticmethod
    def get_visualization(room):
        """
        Returns an ASCII visualization of the room.
        :param room: A list of grid points where there are walls.
        """

        max_x = max([p["x"] for p in room]) + 1
        min_x = min([p["x"] for p in room]) - 1

        max_y = max([p["y"] for p in room]) + 1
        min_y = min([p["y"] for p in room]) - 1

        txt = ""
        for y in range(min_y, max_y):
            for x in range(min_x, max_x):
                point = {"x": x, "y": y}
                if point in room:
                    txt += "o"
                else:
                    txt += " "
            if y < max_y - 1:
                txt += "\n"
        return txt

    def create_avatar(self):
        self.communicate(TDWUtils.create_avatar(position={"x": 12, "y": 25, "z": 8},
                                                look_at={"x": 0, "y": 0.2, "z": 0}))

    def run(self):
        empty = [TDWUtils.create_empty_room(12, 12)]
        office = create_office(12, 24, 4, 4, 6)
        plus = create_plus(4)

        for room in [empty, office, plus]:
            # Print a visualization of the room to the console.
            walls = []

            for r in room:
                walls.extend(r["walls"])

            visualization = self.get_visualization(walls)
            print(visualization)
            print("")

            self.start()
            # Create the room.
            self.communicate(room)

            self.create_avatar()

            # Wait.
            sleep(5)

        self.start()
        self.communicate(office)

        self.create_avatar()

        # Create the ceiling.
        self.communicate({"$type": "create_proc_gen_ceiling"})

        # Delete half of the ceiling.
        walls = []
        for r in room:
            walls.extend(r["walls"])
        half_width = max([p["x"] for p in walls]) + 1
        half_length = max([p["y"] for p in walls]) + 1
        for y in range(half_width):
            for x in range(half_length):
                points = [{"x": x, "y": y}]
                self.communicate([{"$type": "destroy_proc_gen_ceiling_tiles",
                                   "ceiling_tiles": points}
                                  ])
                sleep(0.01)

        # Set the floor material.
        # Set the wall material.
        self.communicate([self.get_add_material("parquet_long_horizontal_clean", library="materials_high.json"),
                          self.get_add_material("aluminium_hairline_brushed"),
                          {"$type": "set_proc_gen_floor_material",
                           "name": "parquet_long_horizontal_clean"},
                          {"$type": "set_proc_gen_floor_texture_scale",
                           "scale": {"x": 8, "y": 8}},
                          {"$type": "set_proc_gen_walls_material",
                           "name": "aluminium_hairline_brushed"},
                          {"$type": "set_proc_gen_walls_texture_scale",
                           "scale": {"x": 2, "y": 2}}])


if __name__ == "__main__":
    ProcGenRoom().run()
