import importlib
from json import loads
from pathlib import Path
from pkg_resources import resource_filename
from typing import List, Tuple, Dict, Callable
import numpy as np
from tdw.tdw_utils import TDWUtils
from tdw.cardinal_direction import CardinalDirection
from tdw.ordinal_direction import OrdinalDirection
from tdw.scene_data.room import Room
from tdw.scene_data.interior_region import InteriorRegion
from tdw.proc_gen.arrangements.arrangement_along_wall import ArrangementAlongWall
from tdw.proc_gen.arrangements.basket import Basket
from tdw.proc_gen.arrangements.dishwasher import Dishwasher
from tdw.proc_gen.arrangements.kitchen_counter import KitchenCounter
from tdw.proc_gen.arrangements.kitchen_counter_top import KitchenCounterTop
from tdw.proc_gen.arrangements.painting import Painting
from tdw.proc_gen.arrangements.radiator import Radiator
from tdw.proc_gen.arrangements.refrigerator import Refrigerator
from tdw.proc_gen.arrangements.shelf import Shelf
from tdw.proc_gen.arrangements.side_table import SideTable
from tdw.proc_gen.arrangements.sink import Sink
from tdw.proc_gen.arrangements.stool import Stool
from tdw.proc_gen.arrangements.stove import Stove
from tdw.proc_gen.arrangements.suitcase import Suitcase
from tdw.proc_gen.arrangements.void import Void


class ProcGenUtils:
    """
    Utility class for procedural generation.
    """

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

    @staticmethod
    def get_lateral_arrangement(categories: List[str], corner: OrdinalDirection, wall: CardinalDirection,
                                region: InteriorRegion, length: float = None, rng: np.random.RandomState = None) -> List[dict]:
        if length is None:
            length = region.get_length(side=wall)
        if rng is None:
            rng = np.random.RandomState(0)
        distance = 0
        commands = []
        for category in categories:
            # A very dirty hack.
            klass = getattr(importlib.import_module(f"tdw.proc_gen.arrangements.{category}"),
                            category.replace("_", " ").title().replace(" ", ""))
            # Get the arrangement.
            print(klass)
            arrangement = klass(corner=corner, wall=wall, distance=distance, region=region, wall_length=length, rng=rng)
            # Get the commands.
            commands.extend(arrangement.get_commands())
            # Increment the distance.
            distance += arrangement.get_length()
        return commands


commands, room = ProcGenUtils.get_proc_gen_box_room(4, 5)
q = ProcGenUtils.get_lateral_arrangement(categories=["dishwasher", "kitchen_counter_top"], corner=OrdinalDirection.northwest,
                                         wall=CardinalDirection.north, region=room.main_region)
print(q)