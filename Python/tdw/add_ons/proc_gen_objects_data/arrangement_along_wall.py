from typing import Dict
from abc import ABC, abstractmethod
from tdw.add_ons.proc_gen_objects_data.arrangement import Arrangement
from tdw.scene_data.interior_region import InteriorRegion
from tdw.cardinal_direction import CardinalDirection
from tdw.librarian import ModelRecord


class ArrangementAlongWall(Arrangement, ABC):
    """
    A procedurally-generated spatial arrangement of objects that is positioned alongside a wall.
    """

    def __init__(self, record: ModelRecord, position: Dict[str, float], wall: CardinalDirection, region: InteriorRegion):
        self._wall: CardinalDirection = wall
        self._region: InteriorRegion = region
        super().__init__(record=record, position=position)

    def _get_position(self, position: Dict[str, float]) -> Dict[str, float]:
        depth = self._get_depth()
        print("TODO bounds offsets")
        if self._wall == CardinalDirection.north:
            return {"x": position["x"],
                    "y": 0,
                    "z": self._region.bounds.z_max - depth / 2}
        elif self._wall == CardinalDirection.south:
            return {"x": position["x"],
                    "y": 0,
                    "z": self._region.bounds.z_min + depth / 2}
        elif self._wall == CardinalDirection.west:
            return {"x": self._region.bounds.x_min + depth / 2,
                    "y": 0,
                    "z": position["z"]}
        elif self._wall == CardinalDirection.east:
            return {"x": self._region.bounds.x_max - depth / 2,
                    "y": 0,
                    "z": position["z"]}
        else:
            raise Exception(self._wall)

    @abstractmethod
    def _get_depth(self) -> float:
        """
        :return: The depth extent of the object.
        """

        raise Exception()
