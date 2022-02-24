from typing import List, Dict
import numpy as np
from overrides import final
from tdw.cardinal_direction import CardinalDirection
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.librarian import ModelRecord
from tdw.scene_data.room import Room
from tdw.proc_gen.arrangements.table_and_chairs import TableAndChairs


class KitchenTable(TableAndChairs):
    def __init__(self, room: Room, used_walls: int, record: ModelRecord, position: Dict[str, float],
                 rng: np.random.RandomState):
        """
        :param room: The [`Room`] that the table is in.
        :param used_walls: Bitwise sum of walls with objects.
        :param record: The record of the root object.
        :param position: The position of the root object. This might be adjusted.
        :param rng: The random number generator.
        """

        self._room: Room = room
        super().__init__(table_rotation_range=2, chair_rotation_range=10, used_walls=used_walls,
                         region=room.main_region, record=record, position=position, rng=rng)

    def _get_category(self) -> str:
        return "kitchen_table"

    def _get_chair_category(self) -> str:
        return "kitchen_chair"
