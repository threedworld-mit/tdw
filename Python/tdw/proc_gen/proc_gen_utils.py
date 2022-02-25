from json import loads
from pathlib import Path
from pkg_resources import resource_filename
from typing import List, Tuple, Dict
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
    def get_position_along_wall(length: float, depth: float, corner: OrdinalDirection, wall: CardinalDirection,
                                distance: float, region: InteriorRegion) -> Dict[str, float]:
        """
        :param length: The length of the object in meters.
        :param depth: The depth of the object in meters.
        :param corner: The corner as an [`OrdinalDirection`](../ordinal_direction.md).
        :param wall: The wall as a [`CardinalDirection`](../cardinal_direction.md).
        :param distance: The distance from the corner along the wall.
        :param region: The [`InteriorRegion`](../scene_data/interior_region.md).

        :return: The position along the `wall` in the `region` at `distance` meters from the `corner`.
        """

        # Get the position at the origin corner plus the depth offset.
        if wall == CardinalDirection.north:
            z = region.z_max - depth / 2
            if corner == OrdinalDirection.northeast:
                x = region.x_max
            elif corner == OrdinalDirection.northwest:
                x = region.x_min
            else:
                raise Exception(f"Invalid corner: {corner}")
        elif wall == CardinalDirection.south:
            z = region.z_min + depth / 2
            if corner == OrdinalDirection.southeast:
                x = region.x_max
            elif corner == OrdinalDirection.southwest:
                x = region.x_min
            else:
                raise Exception(f"Invalid corner: {corner}")
        elif wall == CardinalDirection.west:
            x = region.x_min + depth / 2
            if corner == OrdinalDirection.northwest:
                z = region.z_max
            elif corner == OrdinalDirection.southwest:
                z = region.z_min
            else:
                raise Exception(f"Invalid corner: {corner}")
        elif wall == CardinalDirection.east:
            x = region.x_max - depth / 2
            if corner == OrdinalDirection.northeast:
                z = region.z_max
            elif corner == OrdinalDirection.southeast:
                z = region.z_min
            else:
                raise Exception(f"Invalid corner: {corner}")
        else:
            raise Exception(wall)
        # Get the distance offset.
        pos = {"x": x, "y": 0, "z": z}
        distance = distance + length / 2
        direction = ProcGenUtils.get_direction_from_corner(corner=corner, wall=wall)
        if direction == CardinalDirection.north:
            pos["z"] += distance
        elif direction == CardinalDirection.south:
            pos["z"] -= distance
        elif direction == CardinalDirection.west:
            pos["x"] -= distance
        elif direction == CardinalDirection.east:
            pos["x"] += distance
        else:
            raise Exception(direction)
        return pos

    @staticmethod
    def get_proc_gen_box_room(width: int, length: int) -> Tuple[List[dict], Room]:
        """
        :param width: The width of the room. Must be between 4 and 12 (inclusive).
        :param length: The length of the room. Must be between 4 and 12 (inclusive).
        :return: Tuple: A list of commands to create the room, [`Room` data](../scene_data/room.md).
        """
        proc_gen_box_rooms = loads(Path(resource_filename(__name__, "data/proc_gen_box_rooms.json")).read_text())
        for box_scene in proc_gen_box_rooms:
            if box_scene["size"][0] == width and box_scene["size"][1] == length:
                box_room = box_scene["room"]
                room = Room(main_region=InteriorRegion(region_id=box_room["main_region"]["region_id"],
                                                       center=tuple(box_room["main_region"]["center"]),
                                                       bounds=tuple(box_room["main_region"]["bounds"]),
                                                       non_continuous_walls=box_room["main_region"]["non_continuous_walls"],
                                                       walls_with_windows=box_room["main_region"]["walls_with_windows"]),
                            alcoves=[])
                return [{"$type": "load_scene",
                         "scene_name": "ProcGenScene"},
                        TDWUtils.create_empty_room(width, length)], room
        raise Exception(f"Room size not found: {width}, {length}")
