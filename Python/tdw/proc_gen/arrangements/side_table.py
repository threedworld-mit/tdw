from typing import List
from tdw.tdw_utils import TDWUtils
from tdw.cardinal_direction import CardinalDirection
from tdw.proc_gen.arrangements.arrangement_along_wall import ArrangementAlongWall


class SideTable(ArrangementAlongWall):
    """
    A small side table.

    - The side table model is chosen randomly; see `SideTable.MODEL_CATEGORIES["side_table"]`.
    - The side table is placed next to a wall.
      - The side table's position is automatically adjusted to set it flush to the wall.
      - The side table is automatically rotated so that it faces away from the wall.
      - The side table's (x, z) positional coordinates are offset by a factor; see `SideTable.DEPTH_FACTOR` and `SIDE_TABLE.LENGTH_FACTOR`.
    - The side table always has a rectangular arrangement of objects on top of it; see `SideTable.ON_TOP_OF["side_table"]`.
    - The side table is non-kinematic.
    """

    """:class_var
    Offset the distance from the wall by this factor.
    """
    DEPTH_FACTOR: float = 1.05
    """:class_var
    Offset the distance along the wall by this factor.
    """
    LENGTH_FACTOR: float = 1.25

    def get_commands(self) -> List[dict]:
        return self._add_object_with_other_objects_on_top(kinematic=False)

    def get_length(self) -> float:
        return TDWUtils.get_bounds_extents(bounds=self._record.bounds)[2] * SideTable.LENGTH_FACTOR

    def _get_depth(self) -> float:
        return TDWUtils.get_bounds_extents(bounds=self._record.bounds)[0] * SideTable.DEPTH_FACTOR

    def _get_rotation(self) -> float:
        if self._wall == CardinalDirection.north:
            return 0
        elif self._wall == CardinalDirection.east:
            return 90
        elif self._wall == CardinalDirection.south:
            return 180
        else:
            return 270

    def _get_category(self) -> str:
        return "side_table"
