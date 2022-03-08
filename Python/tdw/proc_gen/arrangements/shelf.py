from typing import List
from tdw.tdw_utils import TDWUtils
from tdw.cardinal_direction import CardinalDirection
from tdw.proc_gen.arrangements.arrangement_along_wall import ArrangementAlongWall


class Shelf(ArrangementAlongWall):
    """
    Shelving with objects on the shelves.

    - The shelf model is chosen randomly; see `Shelf.MODEL_CATEGORIES["shelf"]`.
    - The shelf is placed next to a wall.
      - The shelf's position is automatically adjusted to set it flush to the wall.
      - The shelf is automatically rotated so that it faces away from the wall.
    - Each shelf of the object has a rectangular arrangement of objects. The objects are chosen randomly; see `Shelf.ON_TOP_OF["shelf"]`.
    - The shelf object is kinematic.
    """

    def get_commands(self) -> List[dict]:
        return self._add_object_with_other_objects_on_top(cell_size=0.0125, density=0.8, x_scale=0.75, z_scale=0.8)

    def _get_rotation(self) -> float:
        if self._wall == CardinalDirection.north:
            return 270
        elif self._wall == CardinalDirection.east:
            return 180
        elif self._wall == CardinalDirection.south:
            return 90
        else:
            return 0

    def get_length(self) -> float:
        return TDWUtils.get_bounds_extents(bounds=self._record.bounds)[2]

    def _get_depth(self) -> float:
        return TDWUtils.get_bounds_extents(bounds=self._record.bounds)[0]

    def _get_category(self) -> str:
        return "shelf"
