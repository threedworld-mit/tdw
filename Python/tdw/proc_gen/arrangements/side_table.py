from typing import List
from tdw.tdw_utils import TDWUtils
from tdw.cardinal_direction import CardinalDirection
from tdw.proc_gen.arrangements.arrangement_along_wall import ArrangementAlongWall


class SideTable(ArrangementAlongWall):
    """
    A side table always has a rectangular arrangement of objects on top of it; see `SideTable.ON_TOP_OF["side_table"]`. Due to its size, there are usually only a few objects.

    The side table model is chosen randomly; see `SideTable.MODEL_CATEGORIES["side_table"]`.

    Side tables are non-kinematic.
    """

    def get_commands(self) -> List[dict]:
        return self._add_object_with_other_objects_on_top(kinematic=False)

    def get_length(self) -> float:
        return TDWUtils.get_bounds_extents(bounds=self._record.bounds)[2] * 1.05

    def _get_depth(self) -> float:
        return TDWUtils.get_bounds_extents(bounds=self._record.bounds)[0] * 1.05

    def _get_rotation(self) -> float:
        if self._wall == CardinalDirection.north:
            return 270
        elif self._wall == CardinalDirection.east:
            return 180
        elif self._wall == CardinalDirection.south:
            return 90
        else:
            return 0

    def _get_category(self) -> str:
        return "side_table"
