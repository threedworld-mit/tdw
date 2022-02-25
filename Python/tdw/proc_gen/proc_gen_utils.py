from json import loads
from pathlib import Path
from pkg_resources import resource_filename
from typing import List, Tuple
from tdw.tdw_utils import TDWUtils
from tdw.cardinal_direction import CardinalDirection
from tdw.ordinal_direction import OrdinalDirection
from tdw.scene_data.room import Room
from tdw.scene_data.interior_region import InteriorRegion


class ProcGenUtils:
    """
    Utility class for procedural generation.
    """

    @staticmethod
    def get_corners_from_wall(wall: CardinalDirection) -> List[OrdinalDirection]:
        """
        :param wall: The wall as a [`CardinalDirection`](../cardinal_direction.md).

        :return: The corners of the wall as a 2-element list of [`OrdinalDirection`](../ordinal_direction.md).
        """

        if wall == CardinalDirection.north:
            return [OrdinalDirection.northwest, OrdinalDirection.northeast]
        elif wall == CardinalDirection.south:
            return [OrdinalDirection.southwest, OrdinalDirection.southeast]
        elif wall == CardinalDirection.west:
            return [OrdinalDirection.northwest, OrdinalDirection.southwest]
        elif wall == CardinalDirection.east:
            return [OrdinalDirection.northeast, OrdinalDirection.southeast]

    @staticmethod
    def get_direction_from_corner(corner: OrdinalDirection, wall: CardinalDirection) -> CardinalDirection:
        """
        Given an corner an a wall, get the direction that a lateral arrangement will run along.

        :param corner: The corner as an [`OrdinalDirection`](../ordinal_direction.md).
        :param wall: The wall as a [`CardinalDirection`](../cardinal_direction.md).

        :return: Tuple: direction, wall
        """

        if corner == OrdinalDirection.northwest:
            if wall == CardinalDirection.north:
                return CardinalDirection.east
            elif wall == CardinalDirection.west:
                return CardinalDirection.south
        elif corner == OrdinalDirection.northeast:
            if wall == CardinalDirection.north:
                return CardinalDirection.west
            elif wall == CardinalDirection.east:
                return CardinalDirection.south
        elif corner == OrdinalDirection.southwest:
            if wall == CardinalDirection.south:
                return CardinalDirection.east
            elif wall == CardinalDirection.west:
                return CardinalDirection.north
        elif corner == OrdinalDirection.southeast:
            if wall == CardinalDirection.south:
                return CardinalDirection.west
            elif wall == CardinalDirection.east:
                return CardinalDirection.north
        raise Exception(corner, wall)

    @staticmethod
    def get_proc_gen_box_room(width: int, length: int) -> Tuple[List[dict], Room]:
        """
        :param width: The width of the room. Must be between 4 and 12 (inclusive).
        :param length: The length of the room. Must be between 4 and 12 (inclusive).
        :return: Tuple: A list of commands to create the room, [`Room` data](../scene_data/room.md).
        """
        proc_gen_box_rooms = loads(Path(resource_filename(__name__, "data/proc_gen_box_rooms.json")).read_text())
        for proc_gen_box_room in proc_gen_box_rooms:
            if proc_gen_box_room["size"][0] == width and proc_gen_box_room["size"][1] == length:
                room = Room(main_region=InteriorRegion(region_id=proc_gen_box_room["main_region"]["region_id"],
                                                       center=tuple(proc_gen_box_room["main_region"]["center"]),
                                                       bounds=tuple(proc_gen_box_room["main_region"]["bounds"]),
                                                       non_continuous_walls=proc_gen_box_room["main_region"]["non_continuous_walls"],
                                                       walls_with_windows=proc_gen_box_room["main_region"]["walls_with_windows"]),
                            alcoves=[])
                return [{"$type": "load_scene",
                         "scene_name": "ProcGenScene"},
                        TDWUtils.create_empty_room(width, length)], room
        raise Exception(f"Room size not found: {width}, {length}")
