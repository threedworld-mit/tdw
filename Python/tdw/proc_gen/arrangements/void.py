from typing import List
from tdw.proc_gen.arrangements.arrangement_along_wall import ArrangementAlongWall
from tdw.cardinal_direction import CardinalDirection
from tdw.ordinal_direction import OrdinalDirection
from tdw.scene_data.interior_region import InteriorRegion


class Void(ArrangementAlongWall):
    """
    An empty space along a wall.
    """

    def __init__(self, length: float, corner: OrdinalDirection, wall: CardinalDirection, distance: float,
                 region: InteriorRegion):
        """
        :param length: The length of the void.
        :param wall: The wall as a [`CardinalDirection`](../../cardinal_direction.md) that the root object is next to.
        :param corner: The origin [`Corner`](../../corner.md) of this wall. This is used to derive the direction.
        :param distance: The distance in meters from the corner along the derived direction.
        :param region: The [`InteriorRegion`](../../scene_data/interior_region.md) that the object is in.
        """

        self._length: float = length
        super().__init__(corner=corner, wall=wall, distance=distance, region=region)

    def get_commands(self) -> List[dict]:
        return []

    def _get_commands(self) -> List[dict]:
        return []

    def get_length(self) -> float:
        return self._length

    def _get_depth(self) -> float:
        return 0

    def _get_category(self) -> str:
        return ""

    def _get_rotation(self) -> float:
        return 0
